from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetRadialReinforcementPatternPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "pattern_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    PATTERN_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    pattern_id: str
    def __init__(self, session_id: _Optional[str] = ..., pattern_id: _Optional[str] = ...) -> None: ...

class GetRadialReinforcementPatternPropertiesResponse(_message.Message):
    __slots__ = ("radial_pattern_props",)
    RADIAL_PATTERN_PROPS_FIELD_NUMBER: _ClassVar[int]
    radial_pattern_props: RadialReinforcementPatternProperties
    def __init__(self, radial_pattern_props: _Optional[_Union[RadialReinforcementPatternProperties, _Mapping]] = ...) -> None: ...

class SetRadialReinforcementPatternPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pattern_id", "radial_pattern_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PATTERN_ID_FIELD_NUMBER: _ClassVar[int]
    RADIAL_PATTERN_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pattern_id: str
    radial_pattern_props: RadialReinforcementPatternProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pattern_id: _Optional[str] = ..., radial_pattern_props: _Optional[_Union[RadialReinforcementPatternProperties, _Mapping]] = ...) -> None: ...

class SetRadialReinforcementPatternPropertiesResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class RadialReinforcementPatternProperties(_message.Message):
    __slots__ = ("num_bars_radial", "rotation_angle", "use_cover_depth", "radial_cover_depth", "dist_from_center")
    NUM_BARS_RADIAL_FIELD_NUMBER: _ClassVar[int]
    ROTATION_ANGLE_FIELD_NUMBER: _ClassVar[int]
    USE_COVER_DEPTH_FIELD_NUMBER: _ClassVar[int]
    RADIAL_COVER_DEPTH_FIELD_NUMBER: _ClassVar[int]
    DIST_FROM_CENTER_FIELD_NUMBER: _ClassVar[int]
    num_bars_radial: int
    rotation_angle: float
    use_cover_depth: bool
    radial_cover_depth: float
    dist_from_center: float
    def __init__(self, num_bars_radial: _Optional[int] = ..., rotation_angle: _Optional[float] = ..., use_cover_depth: bool = ..., radial_cover_depth: _Optional[float] = ..., dist_from_center: _Optional[float] = ...) -> None: ...
