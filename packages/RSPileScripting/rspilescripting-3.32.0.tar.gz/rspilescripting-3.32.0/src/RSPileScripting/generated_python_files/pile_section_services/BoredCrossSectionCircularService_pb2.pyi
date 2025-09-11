from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetCircularPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ...) -> None: ...

class GetCircularPropertiesResponse(_message.Message):
    __slots__ = ("circular_props",)
    CIRCULAR_PROPS_FIELD_NUMBER: _ClassVar[int]
    circular_props: CircularProperties
    def __init__(self, circular_props: _Optional[_Union[CircularProperties, _Mapping]] = ...) -> None: ...

class SetCircularPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id", "circular_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    CIRCULAR_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    circular_props: CircularProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ..., circular_props: _Optional[_Union[CircularProperties, _Mapping]] = ...) -> None: ...

class SetCircularPropertiesResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CircularProperties(_message.Message):
    __slots__ = ("diameter",)
    DIAMETER_FIELD_NUMBER: _ClassVar[int]
    diameter: float
    def __init__(self, diameter: _Optional[float] = ...) -> None: ...
