from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetBetaNQRequest(_message.Message):
    __slots__ = ("session_id", "soil_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    soil_id: str
    def __init__(self, session_id: _Optional[str] = ..., soil_id: _Optional[str] = ...) -> None: ...

class GetBetaNQResponse(_message.Message):
    __slots__ = ("beta_nq_props",)
    BETA_NQ_PROPS_FIELD_NUMBER: _ClassVar[int]
    beta_nq_props: BetaNQProperties
    def __init__(self, beta_nq_props: _Optional[_Union[BetaNQProperties, _Mapping]] = ...) -> None: ...

class SetBetaNQRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "soil_id", "beta_nq_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    BETA_NQ_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    soil_id: str
    beta_nq_props: BetaNQProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., soil_id: _Optional[str] = ..., beta_nq_props: _Optional[_Union[BetaNQProperties, _Mapping]] = ...) -> None: ...

class SetBetaNQResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class BetaNQProperties(_message.Message):
    __slots__ = ("beta_nq_beta", "beta_nq_bearing_capacity_factor_nq", "beta_nq_nq_auto", "beta_nq_skin_friction_limit", "beta_nq_end_bearing_limit")
    BETA_NQ_BETA_FIELD_NUMBER: _ClassVar[int]
    BETA_NQ_BEARING_CAPACITY_FACTOR_NQ_FIELD_NUMBER: _ClassVar[int]
    BETA_NQ_NQ_AUTO_FIELD_NUMBER: _ClassVar[int]
    BETA_NQ_SKIN_FRICTION_LIMIT_FIELD_NUMBER: _ClassVar[int]
    BETA_NQ_END_BEARING_LIMIT_FIELD_NUMBER: _ClassVar[int]
    beta_nq_beta: float
    beta_nq_bearing_capacity_factor_nq: float
    beta_nq_nq_auto: bool
    beta_nq_skin_friction_limit: float
    beta_nq_end_bearing_limit: float
    def __init__(self, beta_nq_beta: _Optional[float] = ..., beta_nq_bearing_capacity_factor_nq: _Optional[float] = ..., beta_nq_nq_auto: bool = ..., beta_nq_skin_friction_limit: _Optional[float] = ..., beta_nq_end_bearing_limit: _Optional[float] = ...) -> None: ...
