from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetSquarePropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ...) -> None: ...

class GetSquarePropertiesResponse(_message.Message):
    __slots__ = ("square_props",)
    SQUARE_PROPS_FIELD_NUMBER: _ClassVar[int]
    square_props: SquareProperties
    def __init__(self, square_props: _Optional[_Union[SquareProperties, _Mapping]] = ...) -> None: ...

class SetSquarePropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id", "square_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    SQUARE_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    square_props: SquareProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ..., square_props: _Optional[_Union[SquareProperties, _Mapping]] = ...) -> None: ...

class SetSquarePropertiesResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SquareProperties(_message.Message):
    __slots__ = ("side_length",)
    SIDE_LENGTH_FIELD_NUMBER: _ClassVar[int]
    side_length: float
    def __init__(self, side_length: _Optional[float] = ...) -> None: ...
