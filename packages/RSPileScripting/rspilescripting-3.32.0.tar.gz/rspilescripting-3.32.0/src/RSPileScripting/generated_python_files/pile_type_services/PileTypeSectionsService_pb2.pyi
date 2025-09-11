from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CrossSectionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CROSS_SECTION_UNSPECIFIED: _ClassVar[CrossSectionType]
    E_CROSS_SECTION_UNIFORM: _ClassVar[CrossSectionType]
    E_CROSS_SECTION_TAPERED: _ClassVar[CrossSectionType]
    E_CROSS_SECTION_BELL: _ClassVar[CrossSectionType]
CROSS_SECTION_UNSPECIFIED: CrossSectionType
E_CROSS_SECTION_UNIFORM: CrossSectionType
E_CROSS_SECTION_TAPERED: CrossSectionType
E_CROSS_SECTION_BELL: CrossSectionType

class GetSectionsPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "pile_type_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_TYPE_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    pile_type_id: str
    def __init__(self, session_id: _Optional[str] = ..., pile_type_id: _Optional[str] = ...) -> None: ...

class GetSectionsPropertiesResponse(_message.Message):
    __slots__ = ("sections_props",)
    SECTIONS_PROPS_FIELD_NUMBER: _ClassVar[int]
    sections_props: SectionsProperties
    def __init__(self, sections_props: _Optional[_Union[SectionsProperties, _Mapping]] = ...) -> None: ...

class SetSectionsPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_type_id", "sections_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_TYPE_ID_FIELD_NUMBER: _ClassVar[int]
    SECTIONS_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_type_id: str
    sections_props: SectionsProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_type_id: _Optional[str] = ..., sections_props: _Optional[_Union[SectionsProperties, _Mapping]] = ...) -> None: ...

class SetSectionsPropertiesResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SetPileSegmentsByLengthRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_type_id", "segment_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_TYPE_ID_FIELD_NUMBER: _ClassVar[int]
    SEGMENT_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_type_id: str
    segment_props: PileSegmentsByLengthProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_type_id: _Optional[str] = ..., segment_props: _Optional[_Union[PileSegmentsByLengthProperties, _Mapping]] = ...) -> None: ...

class SetPileSegmentsByLengthResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetPileSegmentsByLengthRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_type_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_TYPE_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_type_id: str
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_type_id: _Optional[str] = ...) -> None: ...

class GetPileSegmentsByLengthResponse(_message.Message):
    __slots__ = ("segment_props",)
    SEGMENT_PROPS_FIELD_NUMBER: _ClassVar[int]
    segment_props: PileSegmentsByLengthProperties
    def __init__(self, segment_props: _Optional[_Union[PileSegmentsByLengthProperties, _Mapping]] = ...) -> None: ...

class SetPileSegmentsByBottomElevationRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_type_id", "segment_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_TYPE_ID_FIELD_NUMBER: _ClassVar[int]
    SEGMENT_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_type_id: str
    segment_props: PileSegmentsByBottomElevationProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_type_id: _Optional[str] = ..., segment_props: _Optional[_Union[PileSegmentsByBottomElevationProperties, _Mapping]] = ...) -> None: ...

class SetPileSegmentsByBottomElevationResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetPileSegmentsByBottomElevationRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_type_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_TYPE_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_type_id: str
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_type_id: _Optional[str] = ...) -> None: ...

class GetPileSegmentsByBottomElevationResponse(_message.Message):
    __slots__ = ("segment_props",)
    SEGMENT_PROPS_FIELD_NUMBER: _ClassVar[int]
    segment_props: PileSegmentsByBottomElevationProperties
    def __init__(self, segment_props: _Optional[_Union[PileSegmentsByBottomElevationProperties, _Mapping]] = ...) -> None: ...

class SectionsProperties(_message.Message):
    __slots__ = ("m_cross_section_type", "m_taper_angle")
    M_CROSS_SECTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    M_TAPER_ANGLE_FIELD_NUMBER: _ClassVar[int]
    m_cross_section_type: CrossSectionType
    m_taper_angle: float
    def __init__(self, m_cross_section_type: _Optional[_Union[CrossSectionType, str]] = ..., m_taper_angle: _Optional[float] = ...) -> None: ...

class PileSegmentsByLengthProperties(_message.Message):
    __slots__ = ("m_pile_head_elevation", "segment_list")
    M_PILE_HEAD_ELEVATION_FIELD_NUMBER: _ClassVar[int]
    SEGMENT_LIST_FIELD_NUMBER: _ClassVar[int]
    m_pile_head_elevation: float
    segment_list: _containers.RepeatedCompositeFieldContainer[PileSegmentsByLengthList]
    def __init__(self, m_pile_head_elevation: _Optional[float] = ..., segment_list: _Optional[_Iterable[_Union[PileSegmentsByLengthList, _Mapping]]] = ...) -> None: ...

class PileSegmentsByBottomElevationProperties(_message.Message):
    __slots__ = ("m_pile_head_elevation", "segment_list")
    M_PILE_HEAD_ELEVATION_FIELD_NUMBER: _ClassVar[int]
    SEGMENT_LIST_FIELD_NUMBER: _ClassVar[int]
    m_pile_head_elevation: float
    segment_list: _containers.RepeatedCompositeFieldContainer[PileSegmentsByBottomElevationList]
    def __init__(self, m_pile_head_elevation: _Optional[float] = ..., segment_list: _Optional[_Iterable[_Union[PileSegmentsByBottomElevationList, _Mapping]]] = ...) -> None: ...

class PileSegmentsByLengthList(_message.Message):
    __slots__ = ("segment_name", "m_length")
    SEGMENT_NAME_FIELD_NUMBER: _ClassVar[int]
    M_LENGTH_FIELD_NUMBER: _ClassVar[int]
    segment_name: str
    m_length: float
    def __init__(self, segment_name: _Optional[str] = ..., m_length: _Optional[float] = ...) -> None: ...

class PileSegmentsByBottomElevationList(_message.Message):
    __slots__ = ("segment_name", "m_bottom_elevation")
    SEGMENT_NAME_FIELD_NUMBER: _ClassVar[int]
    M_BOTTOM_ELEVATION_FIELD_NUMBER: _ClassVar[int]
    segment_name: str
    m_bottom_elevation: float
    def __init__(self, segment_name: _Optional[str] = ..., m_bottom_elevation: _Optional[float] = ...) -> None: ...
