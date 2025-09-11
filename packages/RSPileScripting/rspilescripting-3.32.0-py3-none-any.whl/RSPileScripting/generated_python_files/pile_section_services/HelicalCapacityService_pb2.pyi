from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetHelicalPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ...) -> None: ...

class GetHelicalPropertiesResponse(_message.Message):
    __slots__ = ("helical_props",)
    HELICAL_PROPS_FIELD_NUMBER: _ClassVar[int]
    helical_props: HelicalProperties
    def __init__(self, helical_props: _Optional[_Union[HelicalProperties, _Mapping]] = ...) -> None: ...

class SetHelicalPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id", "helical_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    HELICAL_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    helical_props: HelicalProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ..., helical_props: _Optional[_Union[HelicalProperties, _Mapping]] = ...) -> None: ...

class SetHelicalPropertiesResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class HelicalProperties(_message.Message):
    __slots__ = ("cross_section_type",)
    CROSS_SECTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    cross_section_type: str
    def __init__(self, cross_section_type: _Optional[str] = ...) -> None: ...
