from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetSquareHollowPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ...) -> None: ...

class GetSquareHollowPropertiesResponse(_message.Message):
    __slots__ = ("square_hollow_props",)
    SQUARE_HOLLOW_PROPS_FIELD_NUMBER: _ClassVar[int]
    square_hollow_props: SquareHollowProperties
    def __init__(self, square_hollow_props: _Optional[_Union[SquareHollowProperties, _Mapping]] = ...) -> None: ...

class SetSquareHollowPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id", "square_hollow_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    SQUARE_HOLLOW_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    square_hollow_props: SquareHollowProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ..., square_hollow_props: _Optional[_Union[SquareHollowProperties, _Mapping]] = ...) -> None: ...

class SetSquareHollowPropertiesResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SquareHollowProperties(_message.Message):
    __slots__ = ("outer_side_length", "square_thickness")
    OUTER_SIDE_LENGTH_FIELD_NUMBER: _ClassVar[int]
    SQUARE_THICKNESS_FIELD_NUMBER: _ClassVar[int]
    outer_side_length: float
    square_thickness: float
    def __init__(self, outer_side_length: _Optional[float] = ..., square_thickness: _Optional[float] = ...) -> None: ...
