from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetCorePropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ...) -> None: ...

class GetCorePropertiesResponse(_message.Message):
    __slots__ = ("core_props",)
    CORE_PROPS_FIELD_NUMBER: _ClassVar[int]
    core_props: CoreProperties
    def __init__(self, core_props: _Optional[_Union[CoreProperties, _Mapping]] = ...) -> None: ...

class SetCorePropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id", "core_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    CORE_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    core_props: CoreProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ..., core_props: _Optional[_Union[CoreProperties, _Mapping]] = ...) -> None: ...

class SetCorePropertiesResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CoreProperties(_message.Message):
    __slots__ = ("has_core", "is_filled_core", "yield_stress_of_core", "elastic_modulus_of_core", "diameter_of_core", "thickness_of_core")
    HAS_CORE_FIELD_NUMBER: _ClassVar[int]
    IS_FILLED_CORE_FIELD_NUMBER: _ClassVar[int]
    YIELD_STRESS_OF_CORE_FIELD_NUMBER: _ClassVar[int]
    ELASTIC_MODULUS_OF_CORE_FIELD_NUMBER: _ClassVar[int]
    DIAMETER_OF_CORE_FIELD_NUMBER: _ClassVar[int]
    THICKNESS_OF_CORE_FIELD_NUMBER: _ClassVar[int]
    has_core: bool
    is_filled_core: bool
    yield_stress_of_core: float
    elastic_modulus_of_core: float
    diameter_of_core: float
    thickness_of_core: float
    def __init__(self, has_core: bool = ..., is_filled_core: bool = ..., yield_stress_of_core: _Optional[float] = ..., elastic_modulus_of_core: _Optional[float] = ..., diameter_of_core: _Optional[float] = ..., thickness_of_core: _Optional[float] = ...) -> None: ...
