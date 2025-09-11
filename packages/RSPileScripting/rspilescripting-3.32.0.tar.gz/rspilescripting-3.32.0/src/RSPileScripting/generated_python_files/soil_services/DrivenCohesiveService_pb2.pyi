from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DrivenCohesiveType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    BORED_COHESIVE_TYPE_UNSPECIFIED: _ClassVar[DrivenCohesiveType]
    E_GENERAL_ADHESION_FOR_COHESIVE_SOILS: _ClassVar[DrivenCohesiveType]
    E_OVERLYING_SOFT_CLAY: _ClassVar[DrivenCohesiveType]
    E_OVERLYING_SANDS: _ClassVar[DrivenCohesiveType]
    E_WITHOUT_DIFF_OVERLYING_STRATA: _ClassVar[DrivenCohesiveType]
    E_USER_DEFINED_ADHESION: _ClassVar[DrivenCohesiveType]
BORED_COHESIVE_TYPE_UNSPECIFIED: DrivenCohesiveType
E_GENERAL_ADHESION_FOR_COHESIVE_SOILS: DrivenCohesiveType
E_OVERLYING_SOFT_CLAY: DrivenCohesiveType
E_OVERLYING_SANDS: DrivenCohesiveType
E_WITHOUT_DIFF_OVERLYING_STRATA: DrivenCohesiveType
E_USER_DEFINED_ADHESION: DrivenCohesiveType

class GetDrivenCohesiveRequest(_message.Message):
    __slots__ = ("session_id", "soil_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    soil_id: str
    def __init__(self, session_id: _Optional[str] = ..., soil_id: _Optional[str] = ...) -> None: ...

class GetDrivenCohesiveResponse(_message.Message):
    __slots__ = ("driven_cohesive_props",)
    DRIVEN_COHESIVE_PROPS_FIELD_NUMBER: _ClassVar[int]
    driven_cohesive_props: DrivenCohesiveProperties
    def __init__(self, driven_cohesive_props: _Optional[_Union[DrivenCohesiveProperties, _Mapping]] = ...) -> None: ...

class SetDrivenCohesiveRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "soil_id", "driven_cohesive_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    DRIVEN_COHESIVE_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    soil_id: str
    driven_cohesive_props: DrivenCohesiveProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., soil_id: _Optional[str] = ..., driven_cohesive_props: _Optional[_Union[DrivenCohesiveProperties, _Mapping]] = ...) -> None: ...

class SetDrivenCohesiveResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DrivenCohesiveProperties(_message.Message):
    __slots__ = ("driven_cohesive_type", "undrained_shear_strength")
    DRIVEN_COHESIVE_TYPE_FIELD_NUMBER: _ClassVar[int]
    UNDRAINED_SHEAR_STRENGTH_FIELD_NUMBER: _ClassVar[int]
    driven_cohesive_type: DrivenCohesiveType
    undrained_shear_strength: float
    def __init__(self, driven_cohesive_type: _Optional[_Union[DrivenCohesiveType, str]] = ..., undrained_shear_strength: _Optional[float] = ...) -> None: ...
