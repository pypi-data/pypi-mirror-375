from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetKsDeltaRequest(_message.Message):
    __slots__ = ("session_id", "soil_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    soil_id: str
    def __init__(self, session_id: _Optional[str] = ..., soil_id: _Optional[str] = ...) -> None: ...

class GetKsDeltaResponse(_message.Message):
    __slots__ = ("ks_delta_props",)
    KS_DELTA_PROPS_FIELD_NUMBER: _ClassVar[int]
    ks_delta_props: KsDeltaProperties
    def __init__(self, ks_delta_props: _Optional[_Union[KsDeltaProperties, _Mapping]] = ...) -> None: ...

class SetKsDeltaRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "soil_id", "ks_delta_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    KS_DELTA_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    soil_id: str
    ks_delta_props: KsDeltaProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., soil_id: _Optional[str] = ..., ks_delta_props: _Optional[_Union[KsDeltaProperties, _Mapping]] = ...) -> None: ...

class SetKsDeltaResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class KsDeltaProperties(_message.Message):
    __slots__ = ("ocr", "ks_ko", "delta_phi", "use_auto_bearing_capacity_factor", "bearing_capacity_factor", "ksdelta_skin_friction_limit", "ksdelta_end_bearing_limit")
    OCR_FIELD_NUMBER: _ClassVar[int]
    KS_KO_FIELD_NUMBER: _ClassVar[int]
    DELTA_PHI_FIELD_NUMBER: _ClassVar[int]
    USE_AUTO_BEARING_CAPACITY_FACTOR_FIELD_NUMBER: _ClassVar[int]
    BEARING_CAPACITY_FACTOR_FIELD_NUMBER: _ClassVar[int]
    KSDELTA_SKIN_FRICTION_LIMIT_FIELD_NUMBER: _ClassVar[int]
    KSDELTA_END_BEARING_LIMIT_FIELD_NUMBER: _ClassVar[int]
    ocr: float
    ks_ko: float
    delta_phi: float
    use_auto_bearing_capacity_factor: bool
    bearing_capacity_factor: float
    ksdelta_skin_friction_limit: float
    ksdelta_end_bearing_limit: float
    def __init__(self, ocr: _Optional[float] = ..., ks_ko: _Optional[float] = ..., delta_phi: _Optional[float] = ..., use_auto_bearing_capacity_factor: bool = ..., bearing_capacity_factor: _Optional[float] = ..., ksdelta_skin_friction_limit: _Optional[float] = ..., ksdelta_end_bearing_limit: _Optional[float] = ...) -> None: ...
