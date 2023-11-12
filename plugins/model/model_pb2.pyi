from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Request(_message.Message):
    __slots__ = ["name", "payload"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    name: str
    payload: bytes
    def __init__(self, name: _Optional[str] = ..., payload: _Optional[bytes] = ...) -> None: ...

class Response(_message.Message):
    __slots__ = ["response", "type"]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    response: bytes
    type: str
    def __init__(self, response: _Optional[bytes] = ..., type: _Optional[str] = ...) -> None: ...
