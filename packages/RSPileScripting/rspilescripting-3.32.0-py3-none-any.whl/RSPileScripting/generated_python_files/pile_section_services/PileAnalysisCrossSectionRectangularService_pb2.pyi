from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetRectangularPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ...) -> None: ...

class GetRectangularPropertiesResponse(_message.Message):
    __slots__ = ("rectangular_props",)
    RECTANGULAR_PROPS_FIELD_NUMBER: _ClassVar[int]
    rectangular_props: RectangularProperties
    def __init__(self, rectangular_props: _Optional[_Union[RectangularProperties, _Mapping]] = ...) -> None: ...

class SetRectangularPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id", "rectangular_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    RECTANGULAR_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    rectangular_props: RectangularProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ..., rectangular_props: _Optional[_Union[RectangularProperties, _Mapping]] = ...) -> None: ...

class SetRectangularPropertiesResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class RectangularProperties(_message.Message):
    __slots__ = ("width", "depth")
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    DEPTH_FIELD_NUMBER: _ClassVar[int]
    width: float
    depth: float
    def __init__(self, width: _Optional[float] = ..., depth: _Optional[float] = ...) -> None: ...
