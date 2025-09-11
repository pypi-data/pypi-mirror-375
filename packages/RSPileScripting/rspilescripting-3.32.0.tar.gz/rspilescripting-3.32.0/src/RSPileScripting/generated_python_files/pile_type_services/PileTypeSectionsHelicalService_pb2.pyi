from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetHelixPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "pile_type_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_TYPE_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    pile_type_id: str
    def __init__(self, session_id: _Optional[str] = ..., pile_type_id: _Optional[str] = ...) -> None: ...

class GetHelixPropertiesResponse(_message.Message):
    __slots__ = ("helix_props",)
    HELIX_PROPS_FIELD_NUMBER: _ClassVar[int]
    helix_props: HelixProperties
    def __init__(self, helix_props: _Optional[_Union[HelixProperties, _Mapping]] = ...) -> None: ...

class SetHelixPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_type_id", "helix_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_TYPE_ID_FIELD_NUMBER: _ClassVar[int]
    HELIX_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_type_id: str
    helix_props: HelixProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_type_id: _Optional[str] = ..., helix_props: _Optional[_Union[HelixProperties, _Mapping]] = ...) -> None: ...

class SetHelixPropertiesResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SetHelicesBySpacingRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_type_id", "helices_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_TYPE_ID_FIELD_NUMBER: _ClassVar[int]
    HELICES_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_type_id: str
    helices_props: HelicesBySpacingProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_type_id: _Optional[str] = ..., helices_props: _Optional[_Union[HelicesBySpacingProperties, _Mapping]] = ...) -> None: ...

class SetHelicesBySpacingResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetHelicesBySpacingRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_type_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_TYPE_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_type_id: str
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_type_id: _Optional[str] = ...) -> None: ...

class GetHelicesBySpacingResponse(_message.Message):
    __slots__ = ("helices_props",)
    HELICES_PROPS_FIELD_NUMBER: _ClassVar[int]
    helices_props: HelicesBySpacingProperties
    def __init__(self, helices_props: _Optional[_Union[HelicesBySpacingProperties, _Mapping]] = ...) -> None: ...

class SetHelicesByDepthRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_type_id", "helices_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_TYPE_ID_FIELD_NUMBER: _ClassVar[int]
    HELICES_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_type_id: str
    helices_props: HelicesByDepthProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_type_id: _Optional[str] = ..., helices_props: _Optional[_Union[HelicesByDepthProperties, _Mapping]] = ...) -> None: ...

class SetHelicesByDepthResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetHelicesByDepthRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_type_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_TYPE_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_type_id: str
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_type_id: _Optional[str] = ...) -> None: ...

class GetHelicesByDepthResponse(_message.Message):
    __slots__ = ("helices_props",)
    HELICES_PROPS_FIELD_NUMBER: _ClassVar[int]
    helices_props: HelicesByDepthProperties
    def __init__(self, helices_props: _Optional[_Union[HelicesByDepthProperties, _Mapping]] = ...) -> None: ...

class HelixProperties(_message.Message):
    __slots__ = ("m_heightReductionFactor",)
    M_HEIGHTREDUCTIONFACTOR_FIELD_NUMBER: _ClassVar[int]
    m_heightReductionFactor: float
    def __init__(self, m_heightReductionFactor: _Optional[float] = ...) -> None: ...

class HelicesBySpacingProperties(_message.Message):
    __slots__ = ("m_helixEmbedmentDepth", "helices_list")
    M_HELIXEMBEDMENTDEPTH_FIELD_NUMBER: _ClassVar[int]
    HELICES_LIST_FIELD_NUMBER: _ClassVar[int]
    m_helixEmbedmentDepth: float
    helices_list: _containers.RepeatedCompositeFieldContainer[HelicesBySpacingList]
    def __init__(self, m_helixEmbedmentDepth: _Optional[float] = ..., helices_list: _Optional[_Iterable[_Union[HelicesBySpacingList, _Mapping]]] = ...) -> None: ...

class HelicesByDepthProperties(_message.Message):
    __slots__ = ("helices_list",)
    HELICES_LIST_FIELD_NUMBER: _ClassVar[int]
    helices_list: _containers.RepeatedCompositeFieldContainer[HelicesByDepthList]
    def __init__(self, helices_list: _Optional[_Iterable[_Union[HelicesByDepthList, _Mapping]]] = ...) -> None: ...

class HelicesBySpacingList(_message.Message):
    __slots__ = ("m_pitch", "m_diameter", "m_spacing")
    M_PITCH_FIELD_NUMBER: _ClassVar[int]
    M_DIAMETER_FIELD_NUMBER: _ClassVar[int]
    M_SPACING_FIELD_NUMBER: _ClassVar[int]
    m_pitch: float
    m_diameter: float
    m_spacing: float
    def __init__(self, m_pitch: _Optional[float] = ..., m_diameter: _Optional[float] = ..., m_spacing: _Optional[float] = ...) -> None: ...

class HelicesByDepthList(_message.Message):
    __slots__ = ("m_pitch", "m_diameter", "m_depth_from_pile_head")
    M_PITCH_FIELD_NUMBER: _ClassVar[int]
    M_DIAMETER_FIELD_NUMBER: _ClassVar[int]
    M_DEPTH_FROM_PILE_HEAD_FIELD_NUMBER: _ClassVar[int]
    m_pitch: float
    m_diameter: float
    m_depth_from_pile_head: float
    def __init__(self, m_pitch: _Optional[float] = ..., m_diameter: _Optional[float] = ..., m_depth_from_pile_head: _Optional[float] = ...) -> None: ...
