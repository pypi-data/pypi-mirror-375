from pile_section_services import CommonPileAnalysisCrossSectionTypes_pb2 as _CommonPileAnalysisCrossSectionTypes_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetPrestressedConcretePropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ...) -> None: ...

class GetPrestressedConcretePropertiesResponse(_message.Message):
    __slots__ = ("prestressed_concrete_props",)
    PRESTRESSED_CONCRETE_PROPS_FIELD_NUMBER: _ClassVar[int]
    prestressed_concrete_props: PrestressedConcreteProperties
    def __init__(self, prestressed_concrete_props: _Optional[_Union[PrestressedConcreteProperties, _Mapping]] = ...) -> None: ...

class SetPrestressedConcretePropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id", "prestressed_concrete_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    PRESTRESSED_CONCRETE_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    prestressed_concrete_props: PrestressedConcreteProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ..., prestressed_concrete_props: _Optional[_Union[PrestressedConcreteProperties, _Mapping]] = ...) -> None: ...

class SetPrestressedConcretePropertiesResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class PrestressedConcreteProperties(_message.Message):
    __slots__ = ("compressive_strength", "cross_section_type")
    COMPRESSIVE_STRENGTH_FIELD_NUMBER: _ClassVar[int]
    CROSS_SECTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    compressive_strength: float
    cross_section_type: _CommonPileAnalysisCrossSectionTypes_pb2.CrossSectionType
    def __init__(self, compressive_strength: _Optional[float] = ..., cross_section_type: _Optional[_Union[_CommonPileAnalysisCrossSectionTypes_pb2.CrossSectionType, str]] = ...) -> None: ...
