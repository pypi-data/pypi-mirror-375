from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetWeakRockRequest(_message.Message):
    __slots__ = ("session_id", "soil_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    soil_id: str
    def __init__(self, session_id: _Optional[str] = ..., soil_id: _Optional[str] = ...) -> None: ...

class GetWeakRockResponse(_message.Message):
    __slots__ = ("weak_rock_props",)
    WEAK_ROCK_PROPS_FIELD_NUMBER: _ClassVar[int]
    weak_rock_props: WeakRockProperties
    def __init__(self, weak_rock_props: _Optional[_Union[WeakRockProperties, _Mapping]] = ...) -> None: ...

class SetWeakRockRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "soil_id", "weak_rock_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    WEAK_ROCK_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    soil_id: str
    weak_rock_props: WeakRockProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., soil_id: _Optional[str] = ..., weak_rock_props: _Optional[_Union[WeakRockProperties, _Mapping]] = ...) -> None: ...

class SetWeakRockResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class WeakRockProperties(_message.Message):
    __slots__ = ("unconfined_compressive_strength_quc", "wr_skin_friction_limit", "wr_end_bearing_limit")
    UNCONFINED_COMPRESSIVE_STRENGTH_QUC_FIELD_NUMBER: _ClassVar[int]
    WR_SKIN_FRICTION_LIMIT_FIELD_NUMBER: _ClassVar[int]
    WR_END_BEARING_LIMIT_FIELD_NUMBER: _ClassVar[int]
    unconfined_compressive_strength_quc: float
    wr_skin_friction_limit: float
    wr_end_bearing_limit: float
    def __init__(self, unconfined_compressive_strength_quc: _Optional[float] = ..., wr_skin_friction_limit: _Optional[float] = ..., wr_end_bearing_limit: _Optional[float] = ...) -> None: ...
