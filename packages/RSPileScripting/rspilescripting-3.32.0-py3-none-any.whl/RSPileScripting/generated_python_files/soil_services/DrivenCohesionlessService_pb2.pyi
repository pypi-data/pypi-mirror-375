from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetCohesionlessRequest(_message.Message):
    __slots__ = ("session_id", "soil_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    soil_id: str
    def __init__(self, session_id: _Optional[str] = ..., soil_id: _Optional[str] = ...) -> None: ...

class GetCohesionlessResponse(_message.Message):
    __slots__ = ("driven_cohesionless_props",)
    DRIVEN_COHESIONLESS_PROPS_FIELD_NUMBER: _ClassVar[int]
    driven_cohesionless_props: DrivenCohesionlessProperties
    def __init__(self, driven_cohesionless_props: _Optional[_Union[DrivenCohesionlessProperties, _Mapping]] = ...) -> None: ...

class SetCohesionlessRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "soil_id", "driven_cohesionless_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    DRIVEN_COHESIONLESS_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    soil_id: str
    driven_cohesionless_props: DrivenCohesionlessProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., soil_id: _Optional[str] = ..., driven_cohesionless_props: _Optional[_Union[DrivenCohesionlessProperties, _Mapping]] = ...) -> None: ...

class SetCohesionlessResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DrivenCohesionlessProperties(_message.Message):
    __slots__ = ("use_sptn_test_skin_friction", "use_sptn_test_end_bearing", "skin_friction_angle", "end_bearing_angle")
    USE_SPTN_TEST_SKIN_FRICTION_FIELD_NUMBER: _ClassVar[int]
    USE_SPTN_TEST_END_BEARING_FIELD_NUMBER: _ClassVar[int]
    SKIN_FRICTION_ANGLE_FIELD_NUMBER: _ClassVar[int]
    END_BEARING_ANGLE_FIELD_NUMBER: _ClassVar[int]
    use_sptn_test_skin_friction: bool
    use_sptn_test_end_bearing: bool
    skin_friction_angle: float
    end_bearing_angle: float
    def __init__(self, use_sptn_test_skin_friction: bool = ..., use_sptn_test_end_bearing: bool = ..., skin_friction_angle: _Optional[float] = ..., end_bearing_angle: _Optional[float] = ...) -> None: ...
