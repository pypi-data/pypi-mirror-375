import datetime
import json
import logging
import secrets
import sys
from dataclasses import dataclass
from typing import Callable, Literal

import elasticapm

from .client import Client
from ..notifier_utils.pb import notifier_pb2, notifier_pb2_grpc


def prepare_for_html(message: str):
    return message.replace("<", "&lt;").replace(">", "&gt;")


@dataclass
class Message:
    page: int
    content: str
    message_tag: str
    emergency: str = ''
    amend: dict = None

    def message(self) -> str:
        if self.emergency:
            self.emergency = prepare_for_html(self.emergency)
        self.content = prepare_for_html(self.content)
        emergency = f"<b>Emergency Message</b><blockquote>{self.emergency}</blockquote>\n" if self.emergency else ""
        page = f"<b>Page: {self.page}</b>\n"
        return f"<blockquote>{self.content}</blockquote>\n{emergency}{page}{self.message_tag}"


@dataclass
class PrettifiedMessage:
    title: str
    apm_reference: str = None
    body: str = None
    amend: dict = None
    mentions: str = None

    def message(self, message_truncate_limit):
        developers = f'\n👨‍💻    {self.mentions}' if self.mentions else ''

        body = f"{self.body[:message_truncate_limit]}..." if self.body and (
                len(self.body) > message_truncate_limit) else self.body
        body = f'\n<b>Body</b>\n<blockquote>{prepare_for_html(body)}</blockquote>\n' if body else ''

        apm_reference = f'📊 <b>APM Reference:</b>   <code>{self.apm_reference}</code>' if self.apm_reference else ''

        message = (f'<blockquote>🔵 <b>Title:</b>    <code class>{prepare_for_html(self.title)}</code>\n'
                   f'{apm_reference}'
                   f'{developers}</blockquote>\n'
                   f'{body}')

        amend = (f'\n<b>Amend</b>\n'
                 f'<pre><code class="language-python">'
                 f'{prepare_for_html(json.dumps(self.amend, default=str, indent=4))}'
                 f'</code></pre>') if self.amend else ''

        return f'<b>Message </b>\n{message}{amend}'


class NotifierClient(Client):
    def __init__(
            self,
            server_url: str,
            server_port: int,
            tg_bot_token: str,
            tg_receiver_id: int,
            tg_topic_id: int = None,
    ):
        """
        Notify errors, exceptions, and infos to Telegram.

        Args:
            server_url (str): Notifier server URL.
            server_port (int): Notifier server port.
            tg_bot_token (str): Telegram bot token.
            tg_receiver_id (int): Telegram chat ID.
            tg_topic_id (int): Telegram topic ID.
        """
        super().__init__(server_url=server_url, server_port=server_port)
        self.telegram_bot_token = tg_bot_token
        self.receiver_id = tg_receiver_id
        self.topic_id = tg_topic_id

    def get_stub(self):
        return notifier_pb2_grpc.NotifierServiceStub(self.channel)

    def send_message_to_server(self, message: str):
        """
        Sends an alert message to the configured receiver.

        Args:
            message (str): The message to be sent.
        """
        return self.unary_call(
            self.get_stub().SendMessage,
            notifier_pb2.SendMessageRequest(
                receiver_id=self.receiver_id,
                topic_id=self.topic_id,
                bot_token=self.telegram_bot_token,
                text=message
            )
        )


class ThresholdNotifierClient(NotifierClient):

    def __init__(
            self,
            server_url: str,
            server_port: int,
            tg_bot_token: str,
            tg_receiver_id: int,
            redis,
            tg_topic_id: int = None,
            app_name: str = None,
            process_name: str = None,
            message_expire: int = 3600,
            message_truncate_limit: int = 500,
            developers_id: tuple[str] = None,
    ):
        """
        Notifies errors, exceptions, and information messages to Telegram with custom settings,
        such as sending repeated messages only once within a specified time window.

        Args:
            server_url (str): Notifier server URL.
            server_port (int): Notifier server port.
            tg_bot_token (str): Telegram bot token.
            tg_receiver_id (int): Telegram chat ID.
            tg_topic_id (int): Telegram topic ID.
            app_name (str): Name of the application sending the message.
            process_name (str): Name of the process sending the message.
            message_expire (int): Expiration time (in seconds) for a message to prevent repeated sends.
                If set to `0`, the message is sent immediately.
            message_truncate_limit (int): Maximum allowed message length.
            developers_id (tuple[str]): List of developer Telegram IDs to mention in the message.
            redis: Redis object used to store message-sending settings.
        """

        super().__init__(
            server_url=server_url,
            server_port=server_port,
            tg_bot_token=tg_bot_token,
            tg_receiver_id=tg_receiver_id,
            tg_topic_id=tg_topic_id
        )
        self.app_name = app_name
        self.process_name = process_name
        self.message_expire = message_expire
        self.message_truncate_limit = message_truncate_limit
        self.developers_id = developers_id
        self.topic_id = tg_topic_id
        self.redis = redis

    def check_send_message_condition(self, title: str, expire: int, initial_count: int, counter_algorithm: str):
        msg_key = f'{title}:::{self.receiver_id}:::{self.topic_id}:::count'
        expire = self.message_expire if expire is None else expire
        if initial_count:
            self.redis.incr(msg_key, 1)
            self.redis.expire(msg_key, expire, nx=True)
            count = int(self.redis.get(msg_key))
            if count == 1 or self.check_count(count, initial_count, counter_algorithm):
                return True

        elif expire == 0 or self.redis.set(msg_key, 0, ex=expire, nx=True):
            self.redis.incr(msg_key)
            return True
        return False

    def send_message(
            self, title: str, body: str = None, params: tuple = None, amend: dict = None,
            mention_dev: bool = False, expire: int = None, send_condition: bool = True,
            initial_count: int = None, counter_algorithm: Literal['step'] = 'step'
    ):
        """
        Sends informational or error messages.
        If the same message is sent within the expiration time, it will not be sent again.

        Args:
            title (str): Title of the message.
                Maximum length is 500 characters. Otherwise, an error will be returned when sending the message.
            body (str): Body of the message. Can be parameterized if `params` is set.
                Maximum length is 500 characters; excess characters are replaced with ellipsis (`...`).
            params (tuple): Parameters used for formatting the message.
            amend (dict): Additional information to include in the Telegram message.
            mention_dev (bool): Whether developers should be mentioned in the Telegram notification.
            expire (int): Expiration time (in seconds) that prevents repeated messages.
                Default is 1 hour. If set to `0`, the message is sent immediately.
            send_condition (bool): If `False`, the message will not be sent to Telegram.
            initial_count (int): Controls when the first and subsequent messages are sent.
                The first message is sent immediately, and the next one is sent only after this many messages with the same title have been attempted.
            counter_algorithm (str): Algorithm for counting messages after reaching `initial_count`.
                Defines how many additional messages are counted before sending again. The default is `"step"`.
        """

        if body and params:
            body %= params

        amend = amend or {}
        if send_condition and self.check_send_message_condition(
                title=title, expire=expire, initial_count=initial_count, counter_algorithm=counter_algorithm
        ):
            amend, mentions = self.extend_amends(amend, mention_dev)
            return self.send_message_to_server(
                message=PrettifiedMessage(title=title, body=body, amend=amend, mentions=mentions).message(
                    message_truncate_limit=self.message_truncate_limit
                ),
            )

    def send_exception(
            self, title_prefix: str, exc_info: tuple = None, amend: dict = None, mention_dev: bool = False,
            expire: int = None, send_condition: bool = True,
            initial_count: int = None, counter_algorithm: Literal['step'] = 'step'
    ):
        """
        Sends exception notifications.
        If the same exception is sent within the expiration time, it will not be sent again.

        Args:
            title_prefix (str): Prefix for the exception title in the Telegram message.
                Maximum length is 500 characters.
            exc_info (tuple): A tuple containing exception type, exception value, and traceback.
                If not provided, the exception info is obtained using `sys.exc_info()`.
            amend (dict): Additional information to include in the Telegram message.
            mention_dev (bool): Whether developers should be mentioned in the Telegram notification.
            expire (int): Expiration time (in seconds) that prevents repeated messages.
                Default is 1 hour. If set to `0`, the message is sent immediately.
            send_condition (bool): If `False`, the message will not be sent to Telegram.
            initial_count (int): Controls when the first and subsequent messages are sent.
    T           The first message is sent immediately, and the next one is sent only after this many messages with the same title have been attempted.
            counter_algorithm (str): Algorithm for counting messages after reaching `initial_count`.
                Defines how many additional messages are counted before sending again. The default is `"step"`.
        """

        exc_info = exc_info or sys.exc_info()
        exc_val = str(exc_info[1])
        amend = amend or {}
        title = f"{title_prefix}-{exc_info[0].__name__}"
        if send_condition and self.check_send_message_condition(
                title=title, expire=expire, initial_count=initial_count, counter_algorithm=counter_algorithm
        ):
            amend, mentions = self.extend_amends(amend, mention_dev)
            return self.send_message_to_server(
                message=PrettifiedMessage(title=title, body=exc_val, amend=amend, mentions=mentions).message(
                    message_truncate_limit=self.message_truncate_limit
                ),
            )

    def send_stat(self, message, mention_dev=False, amend=None):
        """
        Sends a basic message without expiration.
        This method formats, paginates, and appends amendments to the Telegram message.
        It is suitable for sending long statistics.

        Args:
            message (str): The message to send.
            mention_dev (bool): Whether developers should be mentioned in the Telegram notification.
            amend (dict): Additional information to include in the Telegram message.
        """
        amend, mentions = self.extend_amends(amend, mention_dev)
        message += "\n" + " ".join(mentions)
        return self.send_message_pagination(message=message, amend=amend)

    def send_raw_stat(self, message: str, mention_dev: bool = False):
        """
        Sends a raw message to Telegram without pagination or built-in formatting.
        Supports custom formatting using HTML tags.
        Suitable for sending single-page, self-formatted messages.

        Args:
            message (str): The message to send.
            mention_dev (bool): Whether developers should be mentioned in the Telegram notification.
        """
        if mention_dev and self.developers_id:
            message += "\n" + " ".join(self.developers_id)

        return self.send_message_to_server(message=message)

    def extend_amends(self, amend: dict, mention_dev: bool):
        mentions = ' '.join(self.developers_id) if mention_dev and self.developers_id else ''
        amend = amend or {}
        amend['AppName'] = self.app_name
        amend['ProcessName'] = self.process_name
        amend['SendTime'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return amend, mentions

    def send_message_pagination(
            self, message: str, amend: dict = None, emergency_msg: str = ''
    ):
        """
        Sends a message in paginated form and retries if necessary.
        Handles large messages by splitting them into multiple parts and manages retries by checking the status of each sent part.

        Args:
            message (str): The message to send.
            amend (dict, optional): Additional information to include in the message.
            emergency_msg (str, optional): An emergency message to append to each message part.
        """
        message = message.replace('<', '&lt;').replace('>', '&gt;')
        msg_list = self.split_msg(message, amend, emergency_msg)
        for msg in msg_list:
            try:
                self.send_message_to_server(msg.message())
            except Exception as e:
                logging.exception(f'exception:{e}')

    def split_msg(self, message: str, amend: dict = None, emergency_msg: str = '') -> list[Message]:
        """
        Splits a given message into multiple parts if it exceeds a predefined size.
        Each split message can include the emergency message and amendments, if provided.

        Args:
            message (str): The original message to split.
            amend (dict, optional): Amendments to append to each message part.
            emergency_msg (str, optional): An emergency message to include in each message part.

        Returns:
            list[Message]: A list of message parts.
        """
        message_part_size = self.message_truncate_limit
        if emergency_msg:
            mandatory_msg = f'\nemergency_msg: {emergency_msg}\namend: {amend}'
            message_part_size = self.message_truncate_limit - len(mandatory_msg)
            if message_part_size < 0:
                raise Exception('Max size is to low')
        message_tag = f'#{secrets.token_hex(5)}\n'
        messages = []
        page = 1
        for message_part in range(0, len(message), message_part_size):
            messages.append(
                Message(
                    page=page,
                    content=message[message_part: message_part + message_part_size],
                    message_tag=message_tag,
                    emergency=emergency_msg,
                    amend=amend,
                )
            )
            page += 1
        return messages

    @staticmethod
    def check_count(now_count, count, algorithm):
        if algorithm is None or algorithm == 'step':
            return (now_count % count) == 0


class APMNotifierClient(ThresholdNotifierClient):
    def __init__(
            self,
            server_url: str,
            server_port: int,
            tg_bot_token: str,
            tg_receiver_id: int,
            redis,
            apm_client,
            tg_topic_id: int = None,
            app_name: str = None,
            process_name: str = None,
            message_expire: int = 3600,
            message_truncate_limit: int = 500,
            developers_id: tuple[str] = None,
    ):
        """
        Sends errors, exceptions, and informational messages to a Telegram bot with custom settings.
        Prevents duplicate messages within a specified time window and stores additional information in APM.

        Args:
            server_url (str): URL of the notifier server.
            server_port (int): Port of the notifier server.
            tg_bot_token (str): Telegram bot token.
            tg_receiver_id (int): Telegram chat ID.
            tg_topic_id (int): Telegram topic ID.
            app_name (str): Name of the application sending the message.
            process_name (str): Name of the process sending the message.
            message_expire (int): Time-to-live (in seconds) for preventing repeated messages.
                If set to `0`, the message is sent immediately.
            message_truncate_limit (int): Maximum allowed message length.
            developers_id (tuple[str]): Telegram IDs of developers to mention in the message.
            redis: Redis client used to store message-sending settings.
            apm_client: APM client used to log additional context.
        """
        super().__init__(
            server_url,
            server_port,
            tg_bot_token,
            tg_receiver_id,
            redis,
            tg_topic_id,
            app_name,
            process_name,
            message_expire,
            message_truncate_limit,
            developers_id,
        )
        self.apm_client = apm_client

    def send_message(
            self, title: str, body: str = None, params: tuple = None, amend: dict = None,
            mention_dev: bool = False, expire: int = None, send_condition: bool = True,
            initial_count: int = None, counter_algorithm: Literal['step'] = 'step',
            apm_expire: int = None,
    ):

        """
        Sends informational or error messages.
        If the same message is sent within the expiration time, it will not be sent again.

        Args:
            title (str): Title of the message.
                Maximum length is 500 characters; otherwise, an error will be returned when sending the Telegram message.
            body (str): Body of the message. Can be parameterized if `params` is set.
                Maximum length is 500 characters; excess characters are replaced with ellipsis (`...`).
            params (tuple): Parameters used for formatting the message.
            amend (dict): Additional information to include in the Telegram message.
                This data will also be logged in the APM custom context.
            mention_dev (bool): Whether developers should be mentioned in the Telegram notification.
            expire (int): Expiration time (in seconds) that prevents repeated messages.
                Default is 1 hour. If set to `0`, the message is sent immediately.
            send_condition (bool): If `False`, the message will not be sent to Telegram.
            initial_count (int): Controls when the first and subsequent messages are sent.
                The first message is sent immediately, and the next one is sent only after this many messages with the same title have been attempted.
            counter_algorithm (str): Algorithm for counting messages after reaching `initial_count`.
                Defines how many additional messages are counted before sending again. Default is `"step"`.
            apm_expire (int): Similar to `expire` but used for APM message capture.
        """

        if body and params:
            body %= params

        amend = amend or {}
        apm_reference = self._apm_capture_with_limit(method=self.apm_client.capture_message, message=title,
                                                     tags=dict(message_body=body, **amend), expire=apm_expire)
        if send_condition and self.check_send_message_condition(
                title=title, expire=expire, initial_count=initial_count, counter_algorithm=counter_algorithm
        ):
            amend, mentions = self.extend_amends(amend, mention_dev)
            return self.send_message_to_server(
                message=PrettifiedMessage(
                    title=title, body=body, amend=amend, mentions=mentions,
                    apm_reference=str(apm_reference),
                ).message(
                    message_truncate_limit=self.message_truncate_limit
                ),
            )

    def send_exception(
            self, title_prefix: str, exc_info: tuple = None, amend: dict = None, mention_dev: bool = False,
            expire: int = None, send_condition: bool = True,
            initial_count: int = None, counter_algorithm: Literal['step'] = 'step',
            apm_expire: int = None
    ):
        """
        Sends exception notifications.
        If the same exception is sent within the expiration time, it will not be sent again.

        Args:
            title_prefix (str): Prefix for the exception title in the Telegram message.
                Maximum length is 500 characters.
            exc_info (tuple): Tuple containing exception type, exception value, and traceback.
                If not provided, exception info is obtained using `sys.exc_info()`.
            amend (dict): Additional information to include in the Telegram message.
                This data will also be logged in the APM custom context.
            mention_dev (bool): Whether developers should be mentioned in the Telegram notification.
            expire (int): Expiration time (in seconds) that prevents repeated messages.
                Default is 1 hour. If set to `0`, the message is sent immediately.
            send_condition (bool): If `False`, the message will not be sent to Telegram.
            initial_count (int): Controls when the first and subsequent messages are sent.
                The first message is sent immediately, and the next one is sent only after this many messages with the same title have been attempted.
            counter_algorithm (str): Algorithm for counting messages after reaching `initial_count`.
                Defines how many additional messages are counted before sending again. Default is `"step"`.
            apm_expire (int): Similar to `expire` but used for APM message capture.
        """
        exc_info = exc_info or sys.exc_info()
        exc_val = str(exc_info[1])
        amend = amend or {}
        title = f'{title_prefix}-{exc_info[0].__name__}'
        amend = {
            **amend,
            'apm_trace_id': elasticapm.get_trace_id(),
            'apm_transaction_id': elasticapm.get_transaction_id(),
            'apm_span_id': elasticapm.get_span_id(),
        }
        apm_reference = self._apm_capture_with_limit(
            method=self.apm_client.capture_exception, message=exc_info, tags=amend, expire=apm_expire
        )
        if send_condition and self.check_send_message_condition(
                title=title, expire=expire, initial_count=initial_count, counter_algorithm=counter_algorithm
        ):
            amend, mentions = self.extend_amends(amend, mention_dev)
            return self.send_message_to_server(
                message=PrettifiedMessage(
                    title=title, body=exc_val, amend=amend, mentions=mentions,
                    apm_reference=str(apm_reference),
                ).message(
                    message_truncate_limit=self.message_truncate_limit
                ),
            )

    def _apm_capture_with_limit(self, method: Callable, message: tuple | str, tags: dict, expire: int):
        receiver_id = self.receiver_id
        topic_id = self.topic_id
        redis_key = f"APM:{self.app_name}:{self.process_name}:{receiver_id}:{topic_id}:{message}"
        if not expire or not self.redis or self.redis.set(redis_key, 1, ex=expire, nx=True):
            context = self._manage_tags(**tags)
            return method(message, context=context)
        return None

    def _manage_tags(self, **tags):
        tags['message_source'] = 'telegram_notifier'
        if elasticapm.get_transaction_id():
            self.apm_client.label(**tags)
        else:
            return dict(tags=tags)
