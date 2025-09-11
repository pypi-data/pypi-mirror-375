from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetSiltRequest(_message.Message):
    __slots__ = ("session_id", "soil_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    soil_id: str
    def __init__(self, session_id: _Optional[str] = ..., soil_id: _Optional[str] = ...) -> None: ...

class GetSiltResponse(_message.Message):
    __slots__ = ("silt_props",)
    SILT_PROPS_FIELD_NUMBER: _ClassVar[int]
    silt_props: SiltProperties
    def __init__(self, silt_props: _Optional[_Union[SiltProperties, _Mapping]] = ...) -> None: ...

class SetSiltRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "soil_id", "silt_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    SILT_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    soil_id: str
    silt_props: SiltProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., soil_id: _Optional[str] = ..., silt_props: _Optional[_Union[SiltProperties, _Mapping]] = ...) -> None: ...

class SetSiltResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SiltProperties(_message.Message):
    __slots__ = ("cohesion_Silt", "friction_angle_Silt", "initial_stiffness_Silt")
    COHESION_SILT_FIELD_NUMBER: _ClassVar[int]
    FRICTION_ANGLE_SILT_FIELD_NUMBER: _ClassVar[int]
    INITIAL_STIFFNESS_SILT_FIELD_NUMBER: _ClassVar[int]
    cohesion_Silt: float
    friction_angle_Silt: float
    initial_stiffness_Silt: float
    def __init__(self, cohesion_Silt: _Optional[float] = ..., friction_angle_Silt: _Optional[float] = ..., initial_stiffness_Silt: _Optional[float] = ...) -> None: ...
