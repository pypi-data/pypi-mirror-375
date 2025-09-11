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
    __slots__ = ("compressive_strength_WR", "reaction_modulus_WR", "rock_quality_designation_WR", "krm_WR")
    COMPRESSIVE_STRENGTH_WR_FIELD_NUMBER: _ClassVar[int]
    REACTION_MODULUS_WR_FIELD_NUMBER: _ClassVar[int]
    ROCK_QUALITY_DESIGNATION_WR_FIELD_NUMBER: _ClassVar[int]
    KRM_WR_FIELD_NUMBER: _ClassVar[int]
    compressive_strength_WR: float
    reaction_modulus_WR: float
    rock_quality_designation_WR: float
    krm_WR: float
    def __init__(self, compressive_strength_WR: _Optional[float] = ..., reaction_modulus_WR: _Optional[float] = ..., rock_quality_designation_WR: _Optional[float] = ..., krm_WR: _Optional[float] = ...) -> None: ...
