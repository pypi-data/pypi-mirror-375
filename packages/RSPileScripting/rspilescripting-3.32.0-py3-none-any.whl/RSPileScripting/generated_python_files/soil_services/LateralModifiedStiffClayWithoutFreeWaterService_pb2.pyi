from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetModifiedStiffClayWithoutFreeWaterRequest(_message.Message):
    __slots__ = ("session_id", "soil_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    soil_id: str
    def __init__(self, session_id: _Optional[str] = ..., soil_id: _Optional[str] = ...) -> None: ...

class GetModifiedStiffClayWithoutFreeWaterResponse(_message.Message):
    __slots__ = ("modified_stiff_clay_props",)
    MODIFIED_STIFF_CLAY_PROPS_FIELD_NUMBER: _ClassVar[int]
    modified_stiff_clay_props: ModifiedStiffClayWithoutFreeWaterProperties
    def __init__(self, modified_stiff_clay_props: _Optional[_Union[ModifiedStiffClayWithoutFreeWaterProperties, _Mapping]] = ...) -> None: ...

class SetModifiedStiffClayWithoutFreeWaterRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "soil_id", "modified_stiff_clay_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    MODIFIED_STIFF_CLAY_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    soil_id: str
    modified_stiff_clay_props: ModifiedStiffClayWithoutFreeWaterProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., soil_id: _Optional[str] = ..., modified_stiff_clay_props: _Optional[_Union[ModifiedStiffClayWithoutFreeWaterProperties, _Mapping]] = ...) -> None: ...

class SetModifiedStiffClayWithoutFreeWaterResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ModifiedStiffClayWithoutFreeWaterProperties(_message.Message):
    __slots__ = ("strain_factor_MSCwoutFW", "undrained_shear_strength_MSCwoutFW", "initial_stiffness_MSCwoutFW")
    STRAIN_FACTOR_MSCWOUTFW_FIELD_NUMBER: _ClassVar[int]
    UNDRAINED_SHEAR_STRENGTH_MSCWOUTFW_FIELD_NUMBER: _ClassVar[int]
    INITIAL_STIFFNESS_MSCWOUTFW_FIELD_NUMBER: _ClassVar[int]
    strain_factor_MSCwoutFW: float
    undrained_shear_strength_MSCwoutFW: float
    initial_stiffness_MSCwoutFW: float
    def __init__(self, strain_factor_MSCwoutFW: _Optional[float] = ..., undrained_shear_strength_MSCwoutFW: _Optional[float] = ..., initial_stiffness_MSCwoutFW: _Optional[float] = ...) -> None: ...
