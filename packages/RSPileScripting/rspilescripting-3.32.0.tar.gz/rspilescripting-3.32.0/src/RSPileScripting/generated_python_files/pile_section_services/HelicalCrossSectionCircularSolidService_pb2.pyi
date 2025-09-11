from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetCircularSolidPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ...) -> None: ...

class GetCircularSolidPropertiesResponse(_message.Message):
    __slots__ = ("circular_solid_props",)
    CIRCULAR_SOLID_PROPS_FIELD_NUMBER: _ClassVar[int]
    circular_solid_props: CircularSolidProperties
    def __init__(self, circular_solid_props: _Optional[_Union[CircularSolidProperties, _Mapping]] = ...) -> None: ...

class SetCircularSolidPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id", "circular_solid_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    CIRCULAR_SOLID_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    circular_solid_props: CircularSolidProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ..., circular_solid_props: _Optional[_Union[CircularSolidProperties, _Mapping]] = ...) -> None: ...

class SetCircularSolidPropertiesResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CircularSolidProperties(_message.Message):
    __slots__ = ("diameter",)
    DIAMETER_FIELD_NUMBER: _ClassVar[int]
    diameter: float
    def __init__(self, diameter: _Optional[float] = ...) -> None: ...
