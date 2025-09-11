from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CrossSectionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CROSS_SECTION_UNSPECIFIED: _ClassVar[CrossSectionType]
    E_CIRCULAR: _ClassVar[CrossSectionType]
    E_SQUARE: _ClassVar[CrossSectionType]
    E_RECTANGLE: _ClassVar[CrossSectionType]
CROSS_SECTION_UNSPECIFIED: CrossSectionType
E_CIRCULAR: CrossSectionType
E_SQUARE: CrossSectionType
E_RECTANGLE: CrossSectionType

class GetBoredPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ...) -> None: ...

class GetBoredPropertiesResponse(_message.Message):
    __slots__ = ("bored_props",)
    BORED_PROPS_FIELD_NUMBER: _ClassVar[int]
    bored_props: BoredProperties
    def __init__(self, bored_props: _Optional[_Union[BoredProperties, _Mapping]] = ...) -> None: ...

class SetBoredPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id", "bored_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    BORED_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    bored_props: BoredProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ..., bored_props: _Optional[_Union[BoredProperties, _Mapping]] = ...) -> None: ...

class SetBoredPropertiesResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class BoredProperties(_message.Message):
    __slots__ = ("cross_section_type", "concrete_cylinder_strength")
    CROSS_SECTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_CYLINDER_STRENGTH_FIELD_NUMBER: _ClassVar[int]
    cross_section_type: CrossSectionType
    concrete_cylinder_strength: float
    def __init__(self, cross_section_type: _Optional[_Union[CrossSectionType, str]] = ..., concrete_cylinder_strength: _Optional[float] = ...) -> None: ...
