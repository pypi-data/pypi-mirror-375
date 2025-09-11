from pile_section_services import CommonPileAnalysisCrossSectionTypes_pb2 as _CommonPileAnalysisCrossSectionTypes_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetPlasticPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ...) -> None: ...

class GetPlasticPropertiesResponse(_message.Message):
    __slots__ = ("plastic_props",)
    PLASTIC_PROPS_FIELD_NUMBER: _ClassVar[int]
    plastic_props: PlasticProperties
    def __init__(self, plastic_props: _Optional[_Union[PlasticProperties, _Mapping]] = ...) -> None: ...

class SetPlasticPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id", "plastic_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    plastic_props: PlasticProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ..., plastic_props: _Optional[_Union[PlasticProperties, _Mapping]] = ...) -> None: ...

class SetPlasticPropertiesResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class PlasticProperties(_message.Message):
    __slots__ = ("elastic_modulus", "plastic_moment_capacity_mxy", "plastic_moment_capacity_mxz", "cross_section_type")
    ELASTIC_MODULUS_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_MOMENT_CAPACITY_MXY_FIELD_NUMBER: _ClassVar[int]
    PLASTIC_MOMENT_CAPACITY_MXZ_FIELD_NUMBER: _ClassVar[int]
    CROSS_SECTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    elastic_modulus: float
    plastic_moment_capacity_mxy: float
    plastic_moment_capacity_mxz: float
    cross_section_type: _CommonPileAnalysisCrossSectionTypes_pb2.CrossSectionType
    def __init__(self, elastic_modulus: _Optional[float] = ..., plastic_moment_capacity_mxy: _Optional[float] = ..., plastic_moment_capacity_mxz: _Optional[float] = ..., cross_section_type: _Optional[_Union[_CommonPileAnalysisCrossSectionTypes_pb2.CrossSectionType, str]] = ...) -> None: ...
