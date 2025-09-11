from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetSquareSolidPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ...) -> None: ...

class GetSquareSolidPropertiesResponse(_message.Message):
    __slots__ = ("square_solid_props",)
    SQUARE_SOLID_PROPS_FIELD_NUMBER: _ClassVar[int]
    square_solid_props: SquareSolidProperties
    def __init__(self, square_solid_props: _Optional[_Union[SquareSolidProperties, _Mapping]] = ...) -> None: ...

class SetSquareSolidPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id", "square_solid_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    SQUARE_SOLID_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    square_solid_props: SquareSolidProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ..., square_solid_props: _Optional[_Union[SquareSolidProperties, _Mapping]] = ...) -> None: ...

class SetSquareSolidPropertiesResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SquareSolidProperties(_message.Message):
    __slots__ = ("side_length",)
    SIDE_LENGTH_FIELD_NUMBER: _ClassVar[int]
    side_length: float
    def __init__(self, side_length: _Optional[float] = ...) -> None: ...
