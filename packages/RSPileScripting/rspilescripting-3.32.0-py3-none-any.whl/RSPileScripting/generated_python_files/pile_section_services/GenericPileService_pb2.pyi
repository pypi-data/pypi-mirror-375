from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetGenericPilePropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ...) -> None: ...

class GetGenericPilePropertiesResponse(_message.Message):
    __slots__ = ("generic_pile_props",)
    GENERIC_PILE_PROPS_FIELD_NUMBER: _ClassVar[int]
    generic_pile_props: GenericPileProperties
    def __init__(self, generic_pile_props: _Optional[_Union[GenericPileProperties, _Mapping]] = ...) -> None: ...

class SetGenericPilePropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id", "generic_pile_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    GENERIC_PILE_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    generic_pile_props: GenericPileProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ..., generic_pile_props: _Optional[_Union[GenericPileProperties, _Mapping]] = ...) -> None: ...

class SetGenericPilePropertiesResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GenericPileProperties(_message.Message):
    __slots__ = ("pile_name", "pile_color")
    PILE_NAME_FIELD_NUMBER: _ClassVar[int]
    PILE_COLOR_FIELD_NUMBER: _ClassVar[int]
    pile_name: str
    pile_color: int
    def __init__(self, pile_name: _Optional[str] = ..., pile_color: _Optional[int] = ...) -> None: ...
