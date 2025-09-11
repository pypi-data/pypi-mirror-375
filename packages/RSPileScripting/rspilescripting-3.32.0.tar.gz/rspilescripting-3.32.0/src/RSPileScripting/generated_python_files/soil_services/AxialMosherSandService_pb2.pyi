from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetMosherSandRequest(_message.Message):
    __slots__ = ("session_id", "soil_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    soil_id: str
    def __init__(self, session_id: _Optional[str] = ..., soil_id: _Optional[str] = ...) -> None: ...

class GetMosherSandResponse(_message.Message):
    __slots__ = ("mosher_sand_props",)
    MOSHER_SAND_PROPS_FIELD_NUMBER: _ClassVar[int]
    mosher_sand_props: MosherSandProperties
    def __init__(self, mosher_sand_props: _Optional[_Union[MosherSandProperties, _Mapping]] = ...) -> None: ...

class SetMosherSandRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "soil_id", "mosher_sand_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    MOSHER_SAND_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    soil_id: str
    mosher_sand_props: MosherSandProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., soil_id: _Optional[str] = ..., mosher_sand_props: _Optional[_Union[MosherSandProperties, _Mapping]] = ...) -> None: ...

class SetMosherSandResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class MosherSandProperties(_message.Message):
    __slots__ = ("mosher_phi", "mosher_use_user_def_es", "mosher_user_def_es", "mosher_ultimate_shear_resistance", "mosher_ultimate_end_bearing_resistance")
    MOSHER_PHI_FIELD_NUMBER: _ClassVar[int]
    MOSHER_USE_USER_DEF_ES_FIELD_NUMBER: _ClassVar[int]
    MOSHER_USER_DEF_ES_FIELD_NUMBER: _ClassVar[int]
    MOSHER_ULTIMATE_SHEAR_RESISTANCE_FIELD_NUMBER: _ClassVar[int]
    MOSHER_ULTIMATE_END_BEARING_RESISTANCE_FIELD_NUMBER: _ClassVar[int]
    mosher_phi: float
    mosher_use_user_def_es: bool
    mosher_user_def_es: float
    mosher_ultimate_shear_resistance: float
    mosher_ultimate_end_bearing_resistance: float
    def __init__(self, mosher_phi: _Optional[float] = ..., mosher_use_user_def_es: bool = ..., mosher_user_def_es: _Optional[float] = ..., mosher_ultimate_shear_resistance: _Optional[float] = ..., mosher_ultimate_end_bearing_resistance: _Optional[float] = ...) -> None: ...
