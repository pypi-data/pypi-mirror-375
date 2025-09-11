from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class BoredCohesionlessType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    E_SF_KS_DELTA: _ClassVar[BoredCohesionlessType]
    E_SF_SPT_AASHTO: _ClassVar[BoredCohesionlessType]
    E_SF_SPT_USER_FACTORS: _ClassVar[BoredCohesionlessType]
    E_SF_BETA_NQ: _ClassVar[BoredCohesionlessType]
E_SF_KS_DELTA: BoredCohesionlessType
E_SF_SPT_AASHTO: BoredCohesionlessType
E_SF_SPT_USER_FACTORS: BoredCohesionlessType
E_SF_BETA_NQ: BoredCohesionlessType

class GetCohesionlessRequest(_message.Message):
    __slots__ = ("session_id", "soil_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    soil_id: str
    def __init__(self, session_id: _Optional[str] = ..., soil_id: _Optional[str] = ...) -> None: ...

class GetCohesionlessResponse(_message.Message):
    __slots__ = ("bored_cohesionless_props",)
    BORED_COHESIONLESS_PROPS_FIELD_NUMBER: _ClassVar[int]
    bored_cohesionless_props: BoredCohesionlessProperties
    def __init__(self, bored_cohesionless_props: _Optional[_Union[BoredCohesionlessProperties, _Mapping]] = ...) -> None: ...

class SetCohesionlessRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "soil_id", "bored_cohesionless_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    BORED_COHESIONLESS_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    soil_id: str
    bored_cohesionless_props: BoredCohesionlessProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., soil_id: _Optional[str] = ..., bored_cohesionless_props: _Optional[_Union[BoredCohesionlessProperties, _Mapping]] = ...) -> None: ...

class SetCohesionlessResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class BoredCohesionlessProperties(_message.Message):
    __slots__ = ("bored_cohesionless_type", "use_sptn_test_skin_friction", "skin_friction_angle", "end_bearing_angle")
    BORED_COHESIONLESS_TYPE_FIELD_NUMBER: _ClassVar[int]
    USE_SPTN_TEST_SKIN_FRICTION_FIELD_NUMBER: _ClassVar[int]
    SKIN_FRICTION_ANGLE_FIELD_NUMBER: _ClassVar[int]
    END_BEARING_ANGLE_FIELD_NUMBER: _ClassVar[int]
    bored_cohesionless_type: BoredCohesionlessType
    use_sptn_test_skin_friction: bool
    skin_friction_angle: float
    end_bearing_angle: float
    def __init__(self, bored_cohesionless_type: _Optional[_Union[BoredCohesionlessType, str]] = ..., use_sptn_test_skin_friction: bool = ..., skin_friction_angle: _Optional[float] = ..., end_bearing_angle: _Optional[float] = ...) -> None: ...
