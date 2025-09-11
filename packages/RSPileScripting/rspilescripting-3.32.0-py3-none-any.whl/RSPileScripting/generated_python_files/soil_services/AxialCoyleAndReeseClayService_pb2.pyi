from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetCoyleAndReeseClayRequest(_message.Message):
    __slots__ = ("session_id", "soil_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    soil_id: str
    def __init__(self, session_id: _Optional[str] = ..., soil_id: _Optional[str] = ...) -> None: ...

class GetCoyleAndReeseClayResponse(_message.Message):
    __slots__ = ("coyle_and_reese_props",)
    COYLE_AND_REESE_PROPS_FIELD_NUMBER: _ClassVar[int]
    coyle_and_reese_props: CoyleAndReeseClayProperties
    def __init__(self, coyle_and_reese_props: _Optional[_Union[CoyleAndReeseClayProperties, _Mapping]] = ...) -> None: ...

class SetCoyleAndReeseClayRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "soil_id", "coyle_and_reese_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    COYLE_AND_REESE_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    soil_id: str
    coyle_and_reese_props: CoyleAndReeseClayProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., soil_id: _Optional[str] = ..., coyle_and_reese_props: _Optional[_Union[CoyleAndReeseClayProperties, _Mapping]] = ...) -> None: ...

class SetCoyleAndReeseClayResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CoyleAndReeseClayProperties(_message.Message):
    __slots__ = ("coyle_reese_shear_strength", "coyle_reese_ultimate_shear_resistance", "coyle_reese_e50", "coyle_reese_ultimate_end_bearing_resistance")
    COYLE_REESE_SHEAR_STRENGTH_FIELD_NUMBER: _ClassVar[int]
    COYLE_REESE_ULTIMATE_SHEAR_RESISTANCE_FIELD_NUMBER: _ClassVar[int]
    COYLE_REESE_E50_FIELD_NUMBER: _ClassVar[int]
    COYLE_REESE_ULTIMATE_END_BEARING_RESISTANCE_FIELD_NUMBER: _ClassVar[int]
    coyle_reese_shear_strength: float
    coyle_reese_ultimate_shear_resistance: float
    coyle_reese_e50: float
    coyle_reese_ultimate_end_bearing_resistance: float
    def __init__(self, coyle_reese_shear_strength: _Optional[float] = ..., coyle_reese_ultimate_shear_resistance: _Optional[float] = ..., coyle_reese_e50: _Optional[float] = ..., coyle_reese_ultimate_end_bearing_resistance: _Optional[float] = ...) -> None: ...
