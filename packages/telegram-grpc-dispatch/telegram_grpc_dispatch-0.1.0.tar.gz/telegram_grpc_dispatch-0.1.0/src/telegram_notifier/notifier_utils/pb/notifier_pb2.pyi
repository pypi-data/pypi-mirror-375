from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class SendMessageRequest(_message.Message):
    __slots__ = ("bot_token", "receiver_id", "topic_id", "text")
    BOT_TOKEN_FIELD_NUMBER: _ClassVar[int]
    RECEIVER_ID_FIELD_NUMBER: _ClassVar[int]
    TOPIC_ID_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    bot_token: str
    receiver_id: int
    topic_id: int
    text: str
    def __init__(self, bot_token: _Optional[str] = ..., receiver_id: _Optional[int] = ..., topic_id: _Optional[int] = ..., text: _Optional[str] = ...) -> None: ...
