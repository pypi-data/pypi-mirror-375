from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetElasticRequest(_message.Message):
    __slots__ = ("session_id", "soil_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    soil_id: str
    def __init__(self, session_id: _Optional[str] = ..., soil_id: _Optional[str] = ...) -> None: ...

class GetElasticResponse(_message.Message):
    __slots__ = ("elastic_props",)
    ELASTIC_PROPS_FIELD_NUMBER: _ClassVar[int]
    elastic_props: ElasticProperties
    def __init__(self, elastic_props: _Optional[_Union[ElasticProperties, _Mapping]] = ...) -> None: ...

class SetElasticRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "soil_id", "elastic_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    ELASTIC_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    soil_id: str
    elastic_props: ElasticProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., soil_id: _Optional[str] = ..., elastic_props: _Optional[_Union[ElasticProperties, _Mapping]] = ...) -> None: ...

class SetElasticResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ElasticProperties(_message.Message):
    __slots__ = ("elastic_shear_mod", "elastic_end_bearing_mod")
    ELASTIC_SHEAR_MOD_FIELD_NUMBER: _ClassVar[int]
    ELASTIC_END_BEARING_MOD_FIELD_NUMBER: _ClassVar[int]
    elastic_shear_mod: float
    elastic_end_bearing_mod: float
    def __init__(self, elastic_shear_mod: _Optional[float] = ..., elastic_end_bearing_mod: _Optional[float] = ...) -> None: ...
