from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class LateralSoilType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    LATERAL_TYPE_UNSPECIFIED: _ClassVar[LateralSoilType]
    E_ELASTIC_SOIL_LAT: _ClassVar[LateralSoilType]
    E_SOFT_CLAY_SOIL_LAT: _ClassVar[LateralSoilType]
    E_SUBMERGED_STIFF_CLAY_LAT: _ClassVar[LateralSoilType]
    E_DRY_STIFF_CLAY_LAT: _ClassVar[LateralSoilType]
    E_SAND_LAT: _ClassVar[LateralSoilType]
    E_WEAK_ROCK_LAT: _ClassVar[LateralSoilType]
    E_USER_DEFINED_LAT: _ClassVar[LateralSoilType]
    E_SMALL_STRAIN_SAND: _ClassVar[LateralSoilType]
    E_API_SAND_LAT: _ClassVar[LateralSoilType]
    E_LOESS_LAT: _ClassVar[LateralSoilType]
    E_LIQUEFIED_SAND_LAT: _ClassVar[LateralSoilType]
    E_PIEDMONT_RESIDUAL_SOILS_LAT: _ClassVar[LateralSoilType]
    E_STRONG_ROCK_LAT: _ClassVar[LateralSoilType]
    E_MODIFIED_STIFF_CLAY_WITHOUT_FREE_WATER_LAT: _ClassVar[LateralSoilType]
    E_SILT_LAT: _ClassVar[LateralSoilType]
    E_SOFT_CLAY_WITH_USER_DEFINED_J_LAT: _ClassVar[LateralSoilType]
    E_LAT_HYBRID_LIQUEFIED_SAND: _ClassVar[LateralSoilType]
    E_LAT_MASSIVE_ROCK: _ClassVar[LateralSoilType]
LATERAL_TYPE_UNSPECIFIED: LateralSoilType
E_ELASTIC_SOIL_LAT: LateralSoilType
E_SOFT_CLAY_SOIL_LAT: LateralSoilType
E_SUBMERGED_STIFF_CLAY_LAT: LateralSoilType
E_DRY_STIFF_CLAY_LAT: LateralSoilType
E_SAND_LAT: LateralSoilType
E_WEAK_ROCK_LAT: LateralSoilType
E_USER_DEFINED_LAT: LateralSoilType
E_SMALL_STRAIN_SAND: LateralSoilType
E_API_SAND_LAT: LateralSoilType
E_LOESS_LAT: LateralSoilType
E_LIQUEFIED_SAND_LAT: LateralSoilType
E_PIEDMONT_RESIDUAL_SOILS_LAT: LateralSoilType
E_STRONG_ROCK_LAT: LateralSoilType
E_MODIFIED_STIFF_CLAY_WITHOUT_FREE_WATER_LAT: LateralSoilType
E_SILT_LAT: LateralSoilType
E_SOFT_CLAY_WITH_USER_DEFINED_J_LAT: LateralSoilType
E_LAT_HYBRID_LIQUEFIED_SAND: LateralSoilType
E_LAT_MASSIVE_ROCK: LateralSoilType

class GetLateralSoilRequest(_message.Message):
    __slots__ = ("session_id", "soil_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    soil_id: str
    def __init__(self, session_id: _Optional[str] = ..., soil_id: _Optional[str] = ...) -> None: ...

class GetLateralSoilResponse(_message.Message):
    __slots__ = ("lateral_soil_props",)
    LATERAL_SOIL_PROPS_FIELD_NUMBER: _ClassVar[int]
    lateral_soil_props: LateralSoilProperties
    def __init__(self, lateral_soil_props: _Optional[_Union[LateralSoilProperties, _Mapping]] = ...) -> None: ...

class SetLateralSoilRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "soil_id", "lateral_soil_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    LATERAL_SOIL_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    soil_id: str
    lateral_soil_props: LateralSoilProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., soil_id: _Optional[str] = ..., lateral_soil_props: _Optional[_Union[LateralSoilProperties, _Mapping]] = ...) -> None: ...

class SetLateralSoilResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class LateralSoilProperties(_message.Message):
    __slots__ = ("lateral_soil_type",)
    LATERAL_SOIL_TYPE_FIELD_NUMBER: _ClassVar[int]
    lateral_soil_type: LateralSoilType
    def __init__(self, lateral_soil_type: _Optional[_Union[LateralSoilType, str]] = ...) -> None: ...
