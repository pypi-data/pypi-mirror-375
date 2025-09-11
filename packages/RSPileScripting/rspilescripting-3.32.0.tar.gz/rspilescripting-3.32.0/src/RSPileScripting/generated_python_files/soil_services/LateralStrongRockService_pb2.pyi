from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetStrongRockRequest(_message.Message):
    __slots__ = ("session_id", "soil_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    soil_id: str
    def __init__(self, session_id: _Optional[str] = ..., soil_id: _Optional[str] = ...) -> None: ...

class GetStrongRockResponse(_message.Message):
    __slots__ = ("strong_rock_props",)
    STRONG_ROCK_PROPS_FIELD_NUMBER: _ClassVar[int]
    strong_rock_props: StrongRockProperties
    def __init__(self, strong_rock_props: _Optional[_Union[StrongRockProperties, _Mapping]] = ...) -> None: ...

class SetStrongRockRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "soil_id", "strong_rock_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    STRONG_ROCK_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    soil_id: str
    strong_rock_props: StrongRockProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., soil_id: _Optional[str] = ..., strong_rock_props: _Optional[_Union[StrongRockProperties, _Mapping]] = ...) -> None: ...

class SetStrongRockResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class StrongRockProperties(_message.Message):
    __slots__ = ("uniaxial_compressive_strength_SR",)
    UNIAXIAL_COMPRESSIVE_STRENGTH_SR_FIELD_NUMBER: _ClassVar[int]
    uniaxial_compressive_strength_SR: float
    def __init__(self, uniaxial_compressive_strength_SR: _Optional[float] = ...) -> None: ...
