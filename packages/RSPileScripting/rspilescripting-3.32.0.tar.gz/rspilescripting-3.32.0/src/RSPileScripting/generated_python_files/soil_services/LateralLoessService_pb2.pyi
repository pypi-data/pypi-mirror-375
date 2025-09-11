from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetLoessRequest(_message.Message):
    __slots__ = ("session_id", "soil_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    soil_id: str
    def __init__(self, session_id: _Optional[str] = ..., soil_id: _Optional[str] = ...) -> None: ...

class GetLoessResponse(_message.Message):
    __slots__ = ("loess_props",)
    LOESS_PROPS_FIELD_NUMBER: _ClassVar[int]
    loess_props: LoessProperties
    def __init__(self, loess_props: _Optional[_Union[LoessProperties, _Mapping]] = ...) -> None: ...

class SetLoessRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "soil_id", "loess_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    LOESS_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    soil_id: str
    loess_props: LoessProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., soil_id: _Optional[str] = ..., loess_props: _Optional[_Union[LoessProperties, _Mapping]] = ...) -> None: ...

class SetLoessResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class LoessProperties(_message.Message):
    __slots__ = ("cone_penetration_loess",)
    CONE_PENETRATION_LOESS_FIELD_NUMBER: _ClassVar[int]
    cone_penetration_loess: float
    def __init__(self, cone_penetration_loess: _Optional[float] = ...) -> None: ...
