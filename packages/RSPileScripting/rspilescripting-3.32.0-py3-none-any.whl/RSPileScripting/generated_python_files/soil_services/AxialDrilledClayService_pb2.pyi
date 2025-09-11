from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetDrilledClayRequest(_message.Message):
    __slots__ = ("session_id", "soil_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    soil_id: str
    def __init__(self, session_id: _Optional[str] = ..., soil_id: _Optional[str] = ...) -> None: ...

class GetDrilledClayResponse(_message.Message):
    __slots__ = ("drilled_clay_props",)
    DRILLED_CLAY_PROPS_FIELD_NUMBER: _ClassVar[int]
    drilled_clay_props: DrilledClayProperties
    def __init__(self, drilled_clay_props: _Optional[_Union[DrilledClayProperties, _Mapping]] = ...) -> None: ...

class SetDrilledClayRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "soil_id", "drilled_clay_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    DRILLED_CLAY_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    soil_id: str
    drilled_clay_props: DrilledClayProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., soil_id: _Optional[str] = ..., drilled_clay_props: _Optional[_Union[DrilledClayProperties, _Mapping]] = ...) -> None: ...

class SetDrilledClayResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DrilledClayProperties(_message.Message):
    __slots__ = ("drilled_clay_ultimate_shear_resistance", "drilled_clay_ultimate_end_bearing_resistance")
    DRILLED_CLAY_ULTIMATE_SHEAR_RESISTANCE_FIELD_NUMBER: _ClassVar[int]
    DRILLED_CLAY_ULTIMATE_END_BEARING_RESISTANCE_FIELD_NUMBER: _ClassVar[int]
    drilled_clay_ultimate_shear_resistance: float
    drilled_clay_ultimate_end_bearing_resistance: float
    def __init__(self, drilled_clay_ultimate_shear_resistance: _Optional[float] = ..., drilled_clay_ultimate_end_bearing_resistance: _Optional[float] = ...) -> None: ...
