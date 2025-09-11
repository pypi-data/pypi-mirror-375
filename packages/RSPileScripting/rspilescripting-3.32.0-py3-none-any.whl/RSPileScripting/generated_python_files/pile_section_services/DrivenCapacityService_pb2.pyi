from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CrossSectionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CROSS_SECTION_UNSPECIFIED: _ClassVar[CrossSectionType]
    E_PIPE_PILE_CLOSED_END: _ClassVar[CrossSectionType]
    E_PIPE_PILE_OPEN_END: _ClassVar[CrossSectionType]
    E_TIMBER_PILE: _ClassVar[CrossSectionType]
    E_CONCRETE_PILE: _ClassVar[CrossSectionType]
    E_H_PILE: _ClassVar[CrossSectionType]
    E_RAYMOND_PILE: _ClassVar[CrossSectionType]
CROSS_SECTION_UNSPECIFIED: CrossSectionType
E_PIPE_PILE_CLOSED_END: CrossSectionType
E_PIPE_PILE_OPEN_END: CrossSectionType
E_TIMBER_PILE: CrossSectionType
E_CONCRETE_PILE: CrossSectionType
E_H_PILE: CrossSectionType
E_RAYMOND_PILE: CrossSectionType

class GetDrivenPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ...) -> None: ...

class GetDrivenPropertiesResponse(_message.Message):
    __slots__ = ("driven_props",)
    DRIVEN_PROPS_FIELD_NUMBER: _ClassVar[int]
    driven_props: DrivenProperties
    def __init__(self, driven_props: _Optional[_Union[DrivenProperties, _Mapping]] = ...) -> None: ...

class SetDrivenPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id", "driven_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    DRIVEN_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    driven_props: DrivenProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ..., driven_props: _Optional[_Union[DrivenProperties, _Mapping]] = ...) -> None: ...

class SetDrivenPropertiesResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DrivenProperties(_message.Message):
    __slots__ = ("cross_section_type",)
    CROSS_SECTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    cross_section_type: CrossSectionType
    def __init__(self, cross_section_type: _Optional[_Union[CrossSectionType, str]] = ...) -> None: ...
