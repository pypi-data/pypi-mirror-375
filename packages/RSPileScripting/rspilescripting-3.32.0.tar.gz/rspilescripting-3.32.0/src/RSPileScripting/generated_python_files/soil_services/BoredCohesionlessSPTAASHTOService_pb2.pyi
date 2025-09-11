from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetSPTAASHTORequest(_message.Message):
    __slots__ = ("session_id", "soil_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    soil_id: str
    def __init__(self, session_id: _Optional[str] = ..., soil_id: _Optional[str] = ...) -> None: ...

class GetSPTAASHTOResponse(_message.Message):
    __slots__ = ("spt_aashto_props",)
    SPT_AASHTO_PROPS_FIELD_NUMBER: _ClassVar[int]
    spt_aashto_props: SPTAASHTOProperties
    def __init__(self, spt_aashto_props: _Optional[_Union[SPTAASHTOProperties, _Mapping]] = ...) -> None: ...

class SetSPTAASHTORequest(_message.Message):
    __slots__ = ("session_id", "model_id", "soil_id", "spt_aashto_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    SPT_AASHTO_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    soil_id: str
    spt_aashto_props: SPTAASHTOProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., soil_id: _Optional[str] = ..., spt_aashto_props: _Optional[_Union[SPTAASHTOProperties, _Mapping]] = ...) -> None: ...

class SetSPTAASHTOResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SPTAASHTOProperties(_message.Message):
    __slots__ = ("aashto_skin_friction_limit", "aashto_end_bearing_limit")
    AASHTO_SKIN_FRICTION_LIMIT_FIELD_NUMBER: _ClassVar[int]
    AASHTO_END_BEARING_LIMIT_FIELD_NUMBER: _ClassVar[int]
    aashto_skin_friction_limit: float
    aashto_end_bearing_limit: float
    def __init__(self, aashto_skin_friction_limit: _Optional[float] = ..., aashto_end_bearing_limit: _Optional[float] = ...) -> None: ...
