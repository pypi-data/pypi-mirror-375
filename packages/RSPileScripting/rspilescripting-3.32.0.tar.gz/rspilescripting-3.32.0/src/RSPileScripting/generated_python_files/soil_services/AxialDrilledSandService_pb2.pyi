from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetDrilledSandRequest(_message.Message):
    __slots__ = ("session_id", "soil_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    soil_id: str
    def __init__(self, session_id: _Optional[str] = ..., soil_id: _Optional[str] = ...) -> None: ...

class GetDrilledSandResponse(_message.Message):
    __slots__ = ("drilled_sand_props",)
    DRILLED_SAND_PROPS_FIELD_NUMBER: _ClassVar[int]
    drilled_sand_props: DrilledSandProperties
    def __init__(self, drilled_sand_props: _Optional[_Union[DrilledSandProperties, _Mapping]] = ...) -> None: ...

class SetDrilledSandRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "soil_id", "drilled_sand_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    DRILLED_SAND_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    soil_id: str
    drilled_sand_props: DrilledSandProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., soil_id: _Optional[str] = ..., drilled_sand_props: _Optional[_Union[DrilledSandProperties, _Mapping]] = ...) -> None: ...

class SetDrilledSandResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DrilledSandProperties(_message.Message):
    __slots__ = ("drilled_sand_ultimate_shear_resistance", "drilled_sand_ultimate_end_bearing_resistance")
    DRILLED_SAND_ULTIMATE_SHEAR_RESISTANCE_FIELD_NUMBER: _ClassVar[int]
    DRILLED_SAND_ULTIMATE_END_BEARING_RESISTANCE_FIELD_NUMBER: _ClassVar[int]
    drilled_sand_ultimate_shear_resistance: float
    drilled_sand_ultimate_end_bearing_resistance: float
    def __init__(self, drilled_sand_ultimate_shear_resistance: _Optional[float] = ..., drilled_sand_ultimate_end_bearing_resistance: _Optional[float] = ...) -> None: ...
