import logging
from concurrent.futures.thread import ThreadPoolExecutor
from http import HTTPStatus
from time import sleep

import requests

from ..notifier_utils.pb import notifier_pb2_grpc

logger = logging.getLogger('telegram_notifier')


class NotifierService(notifier_pb2_grpc.NotifierServiceServicer):

    def __init__(self, max_workers: int = 10, only_print: bool = False):
        self.executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix='telegram_notifier')
        self.only_print = only_print

    def SendMessage(self, request, context):
        self.executor.submit(
            self.send_message,
            request.text, request.receiver_id, request.bot_token, request.topic_id, 5,
        )
        return request

    def send_message(self, message: str, receiver_id: int, telegram_bot_token: str,
                     topic_id: int = None, retrying=5):
        if self.only_print:
            logger.info(message)
            return
        url = f'https://api.telegram.org/bot{telegram_bot_token}/sendMessage'
        data = {
            'chat_id': receiver_id,
            'text': message,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML'
        }
        if topic_id:
            data['reply_to_message_id'] = topic_id

        response = requests.Response()
        for i in range(1, retrying + 1):
            try:
                response = requests.post(url=url, data=data, timeout=5)
            except requests.exceptions.RequestException as e:
                logger.error(f'Exception while sending message: {e}')
                if i == retrying:
                    logger.info(f'can not send message: {message}')
                    return
                continue
            if response.status_code == HTTPStatus.OK:
                break
            elif response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
                sleep_time = response.json().get('parameters').get('retry_after')
                sleep(sleep_time)

        if response.status_code != HTTPStatus.OK:
            error = 'Failed to Send message:\n response= %s \n message= %s \n receiver_id= %s'
            params = (response.content, message, receiver_id)
            logger.error(error % params)
