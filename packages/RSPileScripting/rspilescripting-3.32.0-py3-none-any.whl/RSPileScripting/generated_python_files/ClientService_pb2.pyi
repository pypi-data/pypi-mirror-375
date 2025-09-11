from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class GenerateNewSessionRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GenerateNewSessionResponse(_message.Message):
    __slots__ = ("session_id",)
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    def __init__(self, session_id: _Optional[str] = ...) -> None: ...

class EndSessionRequest(_message.Message):
    __slots__ = ("session_id",)
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    def __init__(self, session_id: _Optional[str] = ...) -> None: ...

class EndSessionResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CheckVersionRequest(_message.Message):
    __slots__ = ("library_version",)
    LIBRARY_VERSION_FIELD_NUMBER: _ClassVar[int]
    library_version: str
    def __init__(self, library_version: _Optional[str] = ...) -> None: ...

class CheckVersionResponse(_message.Message):
    __slots__ = ("do_versions_match", "modeler_version")
    DO_VERSIONS_MATCH_FIELD_NUMBER: _ClassVar[int]
    MODELER_VERSION_FIELD_NUMBER: _ClassVar[int]
    do_versions_match: bool
    modeler_version: str
    def __init__(self, do_versions_match: bool = ..., modeler_version: _Optional[str] = ...) -> None: ...
