from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetAPIClayRequest(_message.Message):
    __slots__ = ("session_id", "soil_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    soil_id: str
    def __init__(self, session_id: _Optional[str] = ..., soil_id: _Optional[str] = ...) -> None: ...

class GetAPIClayResponse(_message.Message):
    __slots__ = ("api_clay_props",)
    API_CLAY_PROPS_FIELD_NUMBER: _ClassVar[int]
    api_clay_props: APIClayProperties
    def __init__(self, api_clay_props: _Optional[_Union[APIClayProperties, _Mapping]] = ...) -> None: ...

class SetAPIClayRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "soil_id", "api_clay_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    API_CLAY_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    soil_id: str
    api_clay_props: APIClayProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., soil_id: _Optional[str] = ..., api_clay_props: _Optional[_Union[APIClayProperties, _Mapping]] = ...) -> None: ...

class SetAPIClayResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class APIClayProperties(_message.Message):
    __slots__ = ("maximum_unit_side_friction_c", "maximum_tip_resistance_c", "undrained_shear_strength_c", "remolded_undrained_shear_strength_c")
    MAXIMUM_UNIT_SIDE_FRICTION_C_FIELD_NUMBER: _ClassVar[int]
    MAXIMUM_TIP_RESISTANCE_C_FIELD_NUMBER: _ClassVar[int]
    UNDRAINED_SHEAR_STRENGTH_C_FIELD_NUMBER: _ClassVar[int]
    REMOLDED_UNDRAINED_SHEAR_STRENGTH_C_FIELD_NUMBER: _ClassVar[int]
    maximum_unit_side_friction_c: float
    maximum_tip_resistance_c: float
    undrained_shear_strength_c: float
    remolded_undrained_shear_strength_c: float
    def __init__(self, maximum_unit_side_friction_c: _Optional[float] = ..., maximum_tip_resistance_c: _Optional[float] = ..., undrained_shear_strength_c: _Optional[float] = ..., remolded_undrained_shear_strength_c: _Optional[float] = ...) -> None: ...
