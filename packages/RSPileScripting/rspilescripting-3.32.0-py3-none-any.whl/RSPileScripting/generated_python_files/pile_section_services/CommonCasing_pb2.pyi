from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetCasingPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ...) -> None: ...

class GetCasingPropertiesResponse(_message.Message):
    __slots__ = ("casing_props",)
    CASING_PROPS_FIELD_NUMBER: _ClassVar[int]
    casing_props: CasingProperties
    def __init__(self, casing_props: _Optional[_Union[CasingProperties, _Mapping]] = ...) -> None: ...

class SetCasingPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id", "casing_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    CASING_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    casing_props: CasingProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ..., casing_props: _Optional[_Union[CasingProperties, _Mapping]] = ...) -> None: ...

class SetCasingPropertiesResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CasingProperties(_message.Message):
    __slots__ = ("has_casing", "yield_stress_of_casing", "elastic_modulus_of_casing", "thickness_of_casing")
    HAS_CASING_FIELD_NUMBER: _ClassVar[int]
    YIELD_STRESS_OF_CASING_FIELD_NUMBER: _ClassVar[int]
    ELASTIC_MODULUS_OF_CASING_FIELD_NUMBER: _ClassVar[int]
    THICKNESS_OF_CASING_FIELD_NUMBER: _ClassVar[int]
    has_casing: bool
    yield_stress_of_casing: float
    elastic_modulus_of_casing: float
    thickness_of_casing: float
    def __init__(self, has_casing: bool = ..., yield_stress_of_casing: _Optional[float] = ..., elastic_modulus_of_casing: _Optional[float] = ..., thickness_of_casing: _Optional[float] = ...) -> None: ...
