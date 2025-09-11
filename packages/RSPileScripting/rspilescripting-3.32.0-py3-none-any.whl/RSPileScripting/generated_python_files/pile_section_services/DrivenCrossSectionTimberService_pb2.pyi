from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetTimberPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ...) -> None: ...

class GetTimberPropertiesResponse(_message.Message):
    __slots__ = ("timber_props",)
    TIMBER_PROPS_FIELD_NUMBER: _ClassVar[int]
    timber_props: TimberProperties
    def __init__(self, timber_props: _Optional[_Union[TimberProperties, _Mapping]] = ...) -> None: ...

class SetTimberPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id", "timber_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    TIMBER_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    timber_props: TimberProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ..., timber_props: _Optional[_Union[TimberProperties, _Mapping]] = ...) -> None: ...

class SetTimberPropertiesResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class TimberProperties(_message.Message):
    __slots__ = ("diameter_top_t",)
    DIAMETER_TOP_T_FIELD_NUMBER: _ClassVar[int]
    diameter_top_t: float
    def __init__(self, diameter_top_t: _Optional[float] = ...) -> None: ...
