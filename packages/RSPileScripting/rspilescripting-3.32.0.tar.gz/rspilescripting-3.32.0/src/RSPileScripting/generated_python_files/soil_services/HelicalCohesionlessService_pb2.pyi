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
    __slots__ = ("helical_cohesionless_props",)
    HELICAL_COHESIONLESS_PROPS_FIELD_NUMBER: _ClassVar[int]
    helical_cohesionless_props: CohesionlessProperties
    def __init__(self, helical_cohesionless_props: _Optional[_Union[CohesionlessProperties, _Mapping]] = ...) -> None: ...

class SetCohesionlessRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "soil_id", "helical_cohesionless_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    HELICAL_COHESIONLESS_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    soil_id: str
    helical_cohesionless_props: CohesionlessProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., soil_id: _Optional[str] = ..., helical_cohesionless_props: _Optional[_Union[CohesionlessProperties, _Mapping]] = ...) -> None: ...

class SetCohesionlessResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CohesionlessProperties(_message.Message):
    __slots__ = ("phi", "k", "delta")
    PHI_FIELD_NUMBER: _ClassVar[int]
    K_FIELD_NUMBER: _ClassVar[int]
    DELTA_FIELD_NUMBER: _ClassVar[int]
    phi: float
    k: float
    delta: float
    def __init__(self, phi: _Optional[float] = ..., k: _Optional[float] = ..., delta: _Optional[float] = ...) -> None: ...
