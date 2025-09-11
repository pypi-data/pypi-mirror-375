from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetAPISandRequest(_message.Message):
    __slots__ = ("session_id", "soil_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    soil_id: str
    def __init__(self, session_id: _Optional[str] = ..., soil_id: _Optional[str] = ...) -> None: ...

class GetAPISandResponse(_message.Message):
    __slots__ = ("api_sand_props",)
    API_SAND_PROPS_FIELD_NUMBER: _ClassVar[int]
    api_sand_props: APISandProperties
    def __init__(self, api_sand_props: _Optional[_Union[APISandProperties, _Mapping]] = ...) -> None: ...

class SetAPISandRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "soil_id", "api_sand_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    API_SAND_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    soil_id: str
    api_sand_props: APISandProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., soil_id: _Optional[str] = ..., api_sand_props: _Optional[_Union[APISandProperties, _Mapping]] = ...) -> None: ...

class SetAPISandResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class APISandProperties(_message.Message):
    __slots__ = ("lateral_earth_pressure_coefficient_s", "bearing_capacity_factor_s", "friction_angle_s", "maximum_unit_side_friction_s", "maximum_tip_resistance_s")
    LATERAL_EARTH_PRESSURE_COEFFICIENT_S_FIELD_NUMBER: _ClassVar[int]
    BEARING_CAPACITY_FACTOR_S_FIELD_NUMBER: _ClassVar[int]
    FRICTION_ANGLE_S_FIELD_NUMBER: _ClassVar[int]
    MAXIMUM_UNIT_SIDE_FRICTION_S_FIELD_NUMBER: _ClassVar[int]
    MAXIMUM_TIP_RESISTANCE_S_FIELD_NUMBER: _ClassVar[int]
    lateral_earth_pressure_coefficient_s: float
    bearing_capacity_factor_s: float
    friction_angle_s: float
    maximum_unit_side_friction_s: float
    maximum_tip_resistance_s: float
    def __init__(self, lateral_earth_pressure_coefficient_s: _Optional[float] = ..., bearing_capacity_factor_s: _Optional[float] = ..., friction_angle_s: _Optional[float] = ..., maximum_unit_side_friction_s: _Optional[float] = ..., maximum_tip_resistance_s: _Optional[float] = ...) -> None: ...
