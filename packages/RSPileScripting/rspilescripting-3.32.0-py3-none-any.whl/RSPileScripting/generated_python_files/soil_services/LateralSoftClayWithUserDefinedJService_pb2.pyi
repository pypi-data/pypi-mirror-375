from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetSoftClayWithUserDefinedJRequest(_message.Message):
    __slots__ = ("session_id", "soil_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    soil_id: str
    def __init__(self, session_id: _Optional[str] = ..., soil_id: _Optional[str] = ...) -> None: ...

class GetSoftClayWithUserDefinedJResponse(_message.Message):
    __slots__ = ("soft_clay_props",)
    SOFT_CLAY_PROPS_FIELD_NUMBER: _ClassVar[int]
    soft_clay_props: SoftClayWithUserDefinedJProperties
    def __init__(self, soft_clay_props: _Optional[_Union[SoftClayWithUserDefinedJProperties, _Mapping]] = ...) -> None: ...

class SetSoftClayWithUserDefinedJRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "soil_id", "soft_clay_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    SOFT_CLAY_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    soil_id: str
    soft_clay_props: SoftClayWithUserDefinedJProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., soil_id: _Optional[str] = ..., soft_clay_props: _Optional[_Union[SoftClayWithUserDefinedJProperties, _Mapping]] = ...) -> None: ...

class SetSoftClayWithUserDefinedJResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SoftClayWithUserDefinedJProperties(_message.Message):
    __slots__ = ("strain_factor_SCwJ", "undrained_shear_strength_SCwJ", "stiffness_factor_J_SCwJ")
    STRAIN_FACTOR_SCWJ_FIELD_NUMBER: _ClassVar[int]
    UNDRAINED_SHEAR_STRENGTH_SCWJ_FIELD_NUMBER: _ClassVar[int]
    STIFFNESS_FACTOR_J_SCWJ_FIELD_NUMBER: _ClassVar[int]
    strain_factor_SCwJ: float
    undrained_shear_strength_SCwJ: float
    stiffness_factor_J_SCwJ: float
    def __init__(self, strain_factor_SCwJ: _Optional[float] = ..., undrained_shear_strength_SCwJ: _Optional[float] = ..., stiffness_factor_J_SCwJ: _Optional[float] = ...) -> None: ...
