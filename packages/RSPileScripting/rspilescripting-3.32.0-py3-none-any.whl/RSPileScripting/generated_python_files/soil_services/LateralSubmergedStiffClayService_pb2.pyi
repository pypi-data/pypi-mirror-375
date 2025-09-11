from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetSubmergedStiffClayRequest(_message.Message):
    __slots__ = ("session_id", "soil_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    soil_id: str
    def __init__(self, session_id: _Optional[str] = ..., soil_id: _Optional[str] = ...) -> None: ...

class GetSubmergedStiffClayResponse(_message.Message):
    __slots__ = ("submerged_stiff_clay_props",)
    SUBMERGED_STIFF_CLAY_PROPS_FIELD_NUMBER: _ClassVar[int]
    submerged_stiff_clay_props: SubmergedStiffClayProperties
    def __init__(self, submerged_stiff_clay_props: _Optional[_Union[SubmergedStiffClayProperties, _Mapping]] = ...) -> None: ...

class SetSubmergedStiffClayRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "soil_id", "submerged_stiff_clay_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    SUBMERGED_STIFF_CLAY_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    soil_id: str
    submerged_stiff_clay_props: SubmergedStiffClayProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., soil_id: _Optional[str] = ..., submerged_stiff_clay_props: _Optional[_Union[SubmergedStiffClayProperties, _Mapping]] = ...) -> None: ...

class SetSubmergedStiffClayResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SubmergedStiffClayProperties(_message.Message):
    __slots__ = ("shear_strength_SSC", "strain_factor_SSC", "ks_SSC")
    SHEAR_STRENGTH_SSC_FIELD_NUMBER: _ClassVar[int]
    STRAIN_FACTOR_SSC_FIELD_NUMBER: _ClassVar[int]
    KS_SSC_FIELD_NUMBER: _ClassVar[int]
    shear_strength_SSC: float
    strain_factor_SSC: float
    ks_SSC: float
    def __init__(self, shear_strength_SSC: _Optional[float] = ..., strain_factor_SSC: _Optional[float] = ..., ks_SSC: _Optional[float] = ...) -> None: ...
