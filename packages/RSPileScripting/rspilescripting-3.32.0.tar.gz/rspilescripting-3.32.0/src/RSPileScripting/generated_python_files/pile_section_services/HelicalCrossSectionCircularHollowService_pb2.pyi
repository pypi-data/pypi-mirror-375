from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetCircularHollowPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ...) -> None: ...

class GetCircularHollowPropertiesResponse(_message.Message):
    __slots__ = ("circular_hollow_props",)
    CIRCULAR_HOLLOW_PROPS_FIELD_NUMBER: _ClassVar[int]
    circular_hollow_props: CircularHollowProperties
    def __init__(self, circular_hollow_props: _Optional[_Union[CircularHollowProperties, _Mapping]] = ...) -> None: ...

class SetCircularHollowPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id", "circular_hollow_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    CIRCULAR_HOLLOW_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    circular_hollow_props: CircularHollowProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ..., circular_hollow_props: _Optional[_Union[CircularHollowProperties, _Mapping]] = ...) -> None: ...

class SetCircularHollowPropertiesResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CircularHollowProperties(_message.Message):
    __slots__ = ("outer_diameter", "circular_thickness")
    OUTER_DIAMETER_FIELD_NUMBER: _ClassVar[int]
    CIRCULAR_THICKNESS_FIELD_NUMBER: _ClassVar[int]
    outer_diameter: float
    circular_thickness: float
    def __init__(self, outer_diameter: _Optional[float] = ..., circular_thickness: _Optional[float] = ...) -> None: ...
