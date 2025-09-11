from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CohesiveType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    BORED_COHESIVE_TYPE_UNSPECIFIED: _ClassVar[CohesiveType]
    E_SR_ALPHA: _ClassVar[CohesiveType]
    E_SR_BETA: _ClassVar[CohesiveType]
BORED_COHESIVE_TYPE_UNSPECIFIED: CohesiveType
E_SR_ALPHA: CohesiveType
E_SR_BETA: CohesiveType

class GetCohesiveRequest(_message.Message):
    __slots__ = ("session_id", "soil_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    soil_id: str
    def __init__(self, session_id: _Optional[str] = ..., soil_id: _Optional[str] = ...) -> None: ...

class GetCohesiveResponse(_message.Message):
    __slots__ = ("cohesive_props",)
    COHESIVE_PROPS_FIELD_NUMBER: _ClassVar[int]
    cohesive_props: CohesiveProperties
    def __init__(self, cohesive_props: _Optional[_Union[CohesiveProperties, _Mapping]] = ...) -> None: ...

class SetCohesiveRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "soil_id", "cohesive_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    COHESIVE_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    soil_id: str
    cohesive_props: CohesiveProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., soil_id: _Optional[str] = ..., cohesive_props: _Optional[_Union[CohesiveProperties, _Mapping]] = ...) -> None: ...

class SetCohesiveResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CohesiveProperties(_message.Message):
    __slots__ = ("cohesive_type",)
    COHESIVE_TYPE_FIELD_NUMBER: _ClassVar[int]
    cohesive_type: CohesiveType
    def __init__(self, cohesive_type: _Optional[_Union[CohesiveType, str]] = ...) -> None: ...
