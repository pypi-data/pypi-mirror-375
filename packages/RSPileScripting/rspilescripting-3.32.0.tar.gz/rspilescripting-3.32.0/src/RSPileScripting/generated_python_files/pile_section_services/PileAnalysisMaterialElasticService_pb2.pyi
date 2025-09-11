from pile_section_services import CommonPileAnalysisCrossSectionTypes_pb2 as _CommonPileAnalysisCrossSectionTypes_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetElasticPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ...) -> None: ...

class GetElasticPropertiesResponse(_message.Message):
    __slots__ = ("elastic_props",)
    ELASTIC_PROPS_FIELD_NUMBER: _ClassVar[int]
    elastic_props: ElasticProperties
    def __init__(self, elastic_props: _Optional[_Union[ElasticProperties, _Mapping]] = ...) -> None: ...

class SetElasticPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id", "elastic_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    ELASTIC_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    elastic_props: ElasticProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ..., elastic_props: _Optional[_Union[ElasticProperties, _Mapping]] = ...) -> None: ...

class SetElasticPropertiesResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ElasticProperties(_message.Message):
    __slots__ = ("elastic_modulus", "cross_section_type")
    ELASTIC_MODULUS_FIELD_NUMBER: _ClassVar[int]
    CROSS_SECTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    elastic_modulus: float
    cross_section_type: _CommonPileAnalysisCrossSectionTypes_pb2.CrossSectionType
    def __init__(self, elastic_modulus: _Optional[float] = ..., cross_section_type: _Optional[_Union[_CommonPileAnalysisCrossSectionTypes_pb2.CrossSectionType, str]] = ...) -> None: ...
