from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetGenericPileTypePropertiesRequest(_message.Message):
    __slots__ = ("session_id", "pile_type_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_TYPE_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    pile_type_id: str
    def __init__(self, session_id: _Optional[str] = ..., pile_type_id: _Optional[str] = ...) -> None: ...

class GetGenericPileTypePropertiesResponse(_message.Message):
    __slots__ = ("generic_pile_type_props",)
    GENERIC_PILE_TYPE_PROPS_FIELD_NUMBER: _ClassVar[int]
    generic_pile_type_props: GenericPileTypeProperties
    def __init__(self, generic_pile_type_props: _Optional[_Union[GenericPileTypeProperties, _Mapping]] = ...) -> None: ...

class SetGenericPileTypePropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_type_id", "generic_pile_type_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_TYPE_ID_FIELD_NUMBER: _ClassVar[int]
    GENERIC_PILE_TYPE_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_type_id: str
    generic_pile_type_props: GenericPileTypeProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_type_id: _Optional[str] = ..., generic_pile_type_props: _Optional[_Union[GenericPileTypeProperties, _Mapping]] = ...) -> None: ...

class SetGenericPileTypePropertiesResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GenericPileTypeProperties(_message.Message):
    __slots__ = ("pile_type_name", "pile_type_color")
    PILE_TYPE_NAME_FIELD_NUMBER: _ClassVar[int]
    PILE_TYPE_COLOR_FIELD_NUMBER: _ClassVar[int]
    pile_type_name: str
    pile_type_color: int
    def __init__(self, pile_type_name: _Optional[str] = ..., pile_type_color: _Optional[int] = ...) -> None: ...
