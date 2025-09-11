from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetCustomReinforcementPatternPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "pattern_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    PATTERN_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    pattern_id: str
    def __init__(self, session_id: _Optional[str] = ..., pattern_id: _Optional[str] = ...) -> None: ...

class GetCustomReinforcementPatternPropertiesResponse(_message.Message):
    __slots__ = ("custom_pattern_props",)
    CUSTOM_PATTERN_PROPS_FIELD_NUMBER: _ClassVar[int]
    custom_pattern_props: CustomReinforcementPatternProperties
    def __init__(self, custom_pattern_props: _Optional[_Union[CustomReinforcementPatternProperties, _Mapping]] = ...) -> None: ...

class SetCustomReinforcementPatternPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pattern_id", "custom_pattern_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PATTERN_ID_FIELD_NUMBER: _ClassVar[int]
    CUSTOM_PATTERN_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pattern_id: str
    custom_pattern_props: CustomReinforcementPatternProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pattern_id: _Optional[str] = ..., custom_pattern_props: _Optional[_Union[CustomReinforcementPatternProperties, _Mapping]] = ...) -> None: ...

class SetCustomReinforcementPatternPropertiesResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CustomReinforcementPatternProperties(_message.Message):
    __slots__ = ("custom_locations",)
    CUSTOM_LOCATIONS_FIELD_NUMBER: _ClassVar[int]
    custom_locations: _containers.RepeatedCompositeFieldContainer[BarLocations]
    def __init__(self, custom_locations: _Optional[_Iterable[_Union[BarLocations, _Mapping]]] = ...) -> None: ...

class BarLocations(_message.Message):
    __slots__ = ("x_coordinate", "y_coordinate")
    X_COORDINATE_FIELD_NUMBER: _ClassVar[int]
    Y_COORDINATE_FIELD_NUMBER: _ClassVar[int]
    x_coordinate: float
    y_coordinate: float
    def __init__(self, x_coordinate: _Optional[float] = ..., y_coordinate: _Optional[float] = ...) -> None: ...
