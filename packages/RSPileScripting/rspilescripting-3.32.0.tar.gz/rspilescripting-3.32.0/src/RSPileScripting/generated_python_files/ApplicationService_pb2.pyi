from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class PingRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class PingResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class OpenFileRequest(_message.Message):
    __slots__ = ("session_id", "file_name")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    FILE_NAME_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    file_name: str
    def __init__(self, session_id: _Optional[str] = ..., file_name: _Optional[str] = ...) -> None: ...

class OpenFileResponse(_message.Message):
    __slots__ = ("model_id",)
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    model_id: str
    def __init__(self, model_id: _Optional[str] = ...) -> None: ...

class CloseApplicationRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CloseApplicationResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
