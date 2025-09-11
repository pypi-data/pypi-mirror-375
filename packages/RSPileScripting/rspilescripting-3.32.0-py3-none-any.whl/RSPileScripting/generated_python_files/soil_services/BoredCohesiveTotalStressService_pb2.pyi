from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetTotalStressRequest(_message.Message):
    __slots__ = ("session_id", "soil_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    soil_id: str
    def __init__(self, session_id: _Optional[str] = ..., soil_id: _Optional[str] = ...) -> None: ...

class GetTotalStressResponse(_message.Message):
    __slots__ = ("total_stress_props",)
    TOTAL_STRESS_PROPS_FIELD_NUMBER: _ClassVar[int]
    total_stress_props: TotalStressProperties
    def __init__(self, total_stress_props: _Optional[_Union[TotalStressProperties, _Mapping]] = ...) -> None: ...

class SetTotalStressRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "soil_id", "total_stress_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    TOTAL_STRESS_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    soil_id: str
    total_stress_props: TotalStressProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., soil_id: _Optional[str] = ..., total_stress_props: _Optional[_Union[TotalStressProperties, _Mapping]] = ...) -> None: ...

class SetTotalStressResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class TotalStressProperties(_message.Message):
    __slots__ = ("undrained_shear_strength_su_alpha", "alpha", "skin_friction_limit_alpha", "end_bearing_limit_alpha", "bearing_capacity_factor_nc_alpha")
    UNDRAINED_SHEAR_STRENGTH_SU_ALPHA_FIELD_NUMBER: _ClassVar[int]
    ALPHA_FIELD_NUMBER: _ClassVar[int]
    SKIN_FRICTION_LIMIT_ALPHA_FIELD_NUMBER: _ClassVar[int]
    END_BEARING_LIMIT_ALPHA_FIELD_NUMBER: _ClassVar[int]
    BEARING_CAPACITY_FACTOR_NC_ALPHA_FIELD_NUMBER: _ClassVar[int]
    undrained_shear_strength_su_alpha: float
    alpha: float
    skin_friction_limit_alpha: float
    end_bearing_limit_alpha: float
    bearing_capacity_factor_nc_alpha: float
    def __init__(self, undrained_shear_strength_su_alpha: _Optional[float] = ..., alpha: _Optional[float] = ..., skin_friction_limit_alpha: _Optional[float] = ..., end_bearing_limit_alpha: _Optional[float] = ..., bearing_capacity_factor_nc_alpha: _Optional[float] = ...) -> None: ...
