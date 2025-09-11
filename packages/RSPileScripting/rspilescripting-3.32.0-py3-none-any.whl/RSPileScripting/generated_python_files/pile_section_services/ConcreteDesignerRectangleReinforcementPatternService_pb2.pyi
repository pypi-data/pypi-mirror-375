from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetRectangleReinforcementPatternPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "pattern_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    PATTERN_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    pattern_id: str
    def __init__(self, session_id: _Optional[str] = ..., pattern_id: _Optional[str] = ...) -> None: ...

class GetRectangleReinforcementPatternPropertiesResponse(_message.Message):
    __slots__ = ("rectangle_pattern_props",)
    RECTANGLE_PATTERN_PROPS_FIELD_NUMBER: _ClassVar[int]
    rectangle_pattern_props: RectangleReinforcementPatternProperties
    def __init__(self, rectangle_pattern_props: _Optional[_Union[RectangleReinforcementPatternProperties, _Mapping]] = ...) -> None: ...

class SetRectangleReinforcementPatternPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pattern_id", "rectangle_pattern_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PATTERN_ID_FIELD_NUMBER: _ClassVar[int]
    RECTANGLE_PATTERN_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pattern_id: str
    rectangle_pattern_props: RectangleReinforcementPatternProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pattern_id: _Optional[str] = ..., rectangle_pattern_props: _Optional[_Union[RectangleReinforcementPatternProperties, _Mapping]] = ...) -> None: ...

class SetRectangleReinforcementPatternPropertiesResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class RectangleReinforcementPatternProperties(_message.Message):
    __slots__ = ("peripheral_bars", "num_bars_x", "num_bars_y", "min_cover_depth")
    PERIPHERAL_BARS_FIELD_NUMBER: _ClassVar[int]
    NUM_BARS_X_FIELD_NUMBER: _ClassVar[int]
    NUM_BARS_Y_FIELD_NUMBER: _ClassVar[int]
    MIN_COVER_DEPTH_FIELD_NUMBER: _ClassVar[int]
    peripheral_bars: bool
    num_bars_x: int
    num_bars_y: int
    min_cover_depth: float
    def __init__(self, peripheral_bars: bool = ..., num_bars_x: _Optional[int] = ..., num_bars_y: _Optional[int] = ..., min_cover_depth: _Optional[float] = ...) -> None: ...
