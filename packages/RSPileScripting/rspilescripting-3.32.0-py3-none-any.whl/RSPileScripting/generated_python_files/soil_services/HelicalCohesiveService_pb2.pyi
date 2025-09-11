from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetCohesiveRequest(_message.Message):
    __slots__ = ("session_id", "soil_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    soil_id: str
    def __init__(self, session_id: _Optional[str] = ..., soil_id: _Optional[str] = ...) -> None: ...

class GetCohesiveResponse(_message.Message):
    __slots__ = ("helical_cohesive_props",)
    HELICAL_COHESIVE_PROPS_FIELD_NUMBER: _ClassVar[int]
    helical_cohesive_props: CohesiveProperties
    def __init__(self, helical_cohesive_props: _Optional[_Union[CohesiveProperties, _Mapping]] = ...) -> None: ...

class SetCohesiveRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "soil_id", "helical_cohesive_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    HELICAL_COHESIVE_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    soil_id: str
    helical_cohesive_props: CohesiveProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., soil_id: _Optional[str] = ..., helical_cohesive_props: _Optional[_Union[CohesiveProperties, _Mapping]] = ...) -> None: ...

class SetCohesiveResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CohesiveProperties(_message.Message):
    __slots__ = ("undrained_shear_strength", "adhesion_factor", "NcPrime")
    UNDRAINED_SHEAR_STRENGTH_FIELD_NUMBER: _ClassVar[int]
    ADHESION_FACTOR_FIELD_NUMBER: _ClassVar[int]
    NCPRIME_FIELD_NUMBER: _ClassVar[int]
    undrained_shear_strength: float
    adhesion_factor: float
    NcPrime: float
    def __init__(self, undrained_shear_strength: _Optional[float] = ..., adhesion_factor: _Optional[float] = ..., NcPrime: _Optional[float] = ...) -> None: ...
