from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetSoftClayRequest(_message.Message):
    __slots__ = ("session_id", "soil_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    soil_id: str
    def __init__(self, session_id: _Optional[str] = ..., soil_id: _Optional[str] = ...) -> None: ...

class GetSoftClayResponse(_message.Message):
    __slots__ = ("soft_clay_props",)
    SOFT_CLAY_PROPS_FIELD_NUMBER: _ClassVar[int]
    soft_clay_props: SoftClayProperties
    def __init__(self, soft_clay_props: _Optional[_Union[SoftClayProperties, _Mapping]] = ...) -> None: ...

class SetSoftClayRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "soil_id", "soft_clay_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    SOFT_CLAY_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    soil_id: str
    soft_clay_props: SoftClayProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., soil_id: _Optional[str] = ..., soft_clay_props: _Optional[_Union[SoftClayProperties, _Mapping]] = ...) -> None: ...

class SetSoftClayResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SoftClayProperties(_message.Message):
    __slots__ = ("strain_factor_scs", "shear_strength_scs")
    STRAIN_FACTOR_SCS_FIELD_NUMBER: _ClassVar[int]
    SHEAR_STRENGTH_SCS_FIELD_NUMBER: _ClassVar[int]
    strain_factor_scs: float
    shear_strength_scs: float
    def __init__(self, strain_factor_scs: _Optional[float] = ..., shear_strength_scs: _Optional[float] = ...) -> None: ...
