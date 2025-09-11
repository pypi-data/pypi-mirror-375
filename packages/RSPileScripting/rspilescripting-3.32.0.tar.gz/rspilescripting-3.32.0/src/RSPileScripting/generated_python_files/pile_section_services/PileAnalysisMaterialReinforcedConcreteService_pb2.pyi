from pile_section_services import CommonPileAnalysisCrossSectionTypes_pb2 as _CommonPileAnalysisCrossSectionTypes_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetReinforcedConcretePropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ...) -> None: ...

class GetReinforcedConcretePropertiesResponse(_message.Message):
    __slots__ = ("reinforced_concrete_props",)
    REINFORCED_CONCRETE_PROPS_FIELD_NUMBER: _ClassVar[int]
    reinforced_concrete_props: ReinforcedConcreteProperties
    def __init__(self, reinforced_concrete_props: _Optional[_Union[ReinforcedConcreteProperties, _Mapping]] = ...) -> None: ...

class SetReinforcedConcretePropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id", "reinforced_concrete_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    REINFORCED_CONCRETE_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    reinforced_concrete_props: ReinforcedConcreteProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ..., reinforced_concrete_props: _Optional[_Union[ReinforcedConcreteProperties, _Mapping]] = ...) -> None: ...

class SetReinforcedConcretePropertiesResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ReinforcedConcreteProperties(_message.Message):
    __slots__ = ("compressive_strength", "cross_section_type")
    COMPRESSIVE_STRENGTH_FIELD_NUMBER: _ClassVar[int]
    CROSS_SECTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    compressive_strength: float
    cross_section_type: _CommonPileAnalysisCrossSectionTypes_pb2.CrossSectionType
    def __init__(self, compressive_strength: _Optional[float] = ..., cross_section_type: _Optional[_Union[_CommonPileAnalysisCrossSectionTypes_pb2.CrossSectionType, str]] = ...) -> None: ...
