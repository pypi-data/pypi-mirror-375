from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetEffectiveStressRequest(_message.Message):
    __slots__ = ("session_id", "soil_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    soil_id: str
    def __init__(self, session_id: _Optional[str] = ..., soil_id: _Optional[str] = ...) -> None: ...

class GetEffectiveStressResponse(_message.Message):
    __slots__ = ("effective_stress_props",)
    EFFECTIVE_STRESS_PROPS_FIELD_NUMBER: _ClassVar[int]
    effective_stress_props: EffectiveStressProperties
    def __init__(self, effective_stress_props: _Optional[_Union[EffectiveStressProperties, _Mapping]] = ...) -> None: ...

class SetEffectiveStressRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "soil_id", "effective_stress_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    EFFECTIVE_STRESS_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    soil_id: str
    effective_stress_props: EffectiveStressProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., soil_id: _Optional[str] = ..., effective_stress_props: _Optional[_Union[EffectiveStressProperties, _Mapping]] = ...) -> None: ...

class SetEffectiveStressResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class EffectiveStressProperties(_message.Message):
    __slots__ = ("beta", "limit_skin_resitance_beta", "end_bearing_limit_beta", "effective_cohesion_c_beta", "bearing_capacity_factor_nc_beta", "bearing_capacity_factor_nq_beta")
    BETA_FIELD_NUMBER: _ClassVar[int]
    LIMIT_SKIN_RESITANCE_BETA_FIELD_NUMBER: _ClassVar[int]
    END_BEARING_LIMIT_BETA_FIELD_NUMBER: _ClassVar[int]
    EFFECTIVE_COHESION_C_BETA_FIELD_NUMBER: _ClassVar[int]
    BEARING_CAPACITY_FACTOR_NC_BETA_FIELD_NUMBER: _ClassVar[int]
    BEARING_CAPACITY_FACTOR_NQ_BETA_FIELD_NUMBER: _ClassVar[int]
    beta: float
    limit_skin_resitance_beta: float
    end_bearing_limit_beta: float
    effective_cohesion_c_beta: float
    bearing_capacity_factor_nc_beta: float
    bearing_capacity_factor_nq_beta: float
    def __init__(self, beta: _Optional[float] = ..., limit_skin_resitance_beta: _Optional[float] = ..., end_bearing_limit_beta: _Optional[float] = ..., effective_cohesion_c_beta: _Optional[float] = ..., bearing_capacity_factor_nc_beta: _Optional[float] = ..., bearing_capacity_factor_nq_beta: _Optional[float] = ...) -> None: ...
