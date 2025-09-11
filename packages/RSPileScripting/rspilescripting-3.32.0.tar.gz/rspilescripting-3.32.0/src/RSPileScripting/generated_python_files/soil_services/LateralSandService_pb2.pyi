from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetSandRequest(_message.Message):
    __slots__ = ("session_id", "soil_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    soil_id: str
    def __init__(self, session_id: _Optional[str] = ..., soil_id: _Optional[str] = ...) -> None: ...

class GetSandResponse(_message.Message):
    __slots__ = ("sand_props",)
    SAND_PROPS_FIELD_NUMBER: _ClassVar[int]
    sand_props: SandProperties
    def __init__(self, sand_props: _Optional[_Union[SandProperties, _Mapping]] = ...) -> None: ...

class SetSandRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "soil_id", "sand_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    SAND_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    soil_id: str
    sand_props: SandProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., soil_id: _Optional[str] = ..., sand_props: _Optional[_Union[SandProperties, _Mapping]] = ...) -> None: ...

class SetSandResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SandProperties(_message.Message):
    __slots__ = ("friction_angle_S", "kpy_S", "kpy_S_GW")
    FRICTION_ANGLE_S_FIELD_NUMBER: _ClassVar[int]
    KPY_S_FIELD_NUMBER: _ClassVar[int]
    KPY_S_GW_FIELD_NUMBER: _ClassVar[int]
    friction_angle_S: float
    kpy_S: float
    kpy_S_GW: float
    def __init__(self, friction_angle_S: _Optional[float] = ..., kpy_S: _Optional[float] = ..., kpy_S_GW: _Optional[float] = ...) -> None: ...
