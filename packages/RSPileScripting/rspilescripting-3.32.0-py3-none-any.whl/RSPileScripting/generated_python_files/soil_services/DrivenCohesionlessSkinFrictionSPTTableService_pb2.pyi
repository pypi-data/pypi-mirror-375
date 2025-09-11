from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetSPTTableRequest(_message.Message):
    __slots__ = ("session_id", "soil_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    soil_id: str
    def __init__(self, session_id: _Optional[str] = ..., soil_id: _Optional[str] = ...) -> None: ...

class GetSPTTableResponse(_message.Message):
    __slots__ = ("spt_table_props",)
    SPT_TABLE_PROPS_FIELD_NUMBER: _ClassVar[int]
    spt_table_props: SPTTableProperties
    def __init__(self, spt_table_props: _Optional[_Union[SPTTableProperties, _Mapping]] = ...) -> None: ...

class SetSPTTableRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "soil_id", "spt_table_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    SPT_TABLE_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    soil_id: str
    spt_table_props: SPTTableProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., soil_id: _Optional[str] = ..., spt_table_props: _Optional[_Union[SPTTableProperties, _Mapping]] = ...) -> None: ...

class SetSPTTableResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SPTTableProperties(_message.Message):
    __slots__ = ("sptn_array_skin_friction", "spt_depth_array_skin_friction", "spt_correction_skin_friction")
    SPTN_ARRAY_SKIN_FRICTION_FIELD_NUMBER: _ClassVar[int]
    SPT_DEPTH_ARRAY_SKIN_FRICTION_FIELD_NUMBER: _ClassVar[int]
    SPT_CORRECTION_SKIN_FRICTION_FIELD_NUMBER: _ClassVar[int]
    sptn_array_skin_friction: _containers.RepeatedScalarFieldContainer[float]
    spt_depth_array_skin_friction: _containers.RepeatedScalarFieldContainer[float]
    spt_correction_skin_friction: bool
    def __init__(self, sptn_array_skin_friction: _Optional[_Iterable[float]] = ..., spt_depth_array_skin_friction: _Optional[_Iterable[float]] = ..., spt_correction_skin_friction: bool = ...) -> None: ...
