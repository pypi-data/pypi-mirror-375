from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OrientationType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ORIENTATION_UNSPECIFIED: _ClassVar[OrientationType]
    OT_TREND_PLUNGE: _ClassVar[OrientationType]
    OT_VECTOR: _ClassVar[OrientationType]
ORIENTATION_UNSPECIFIED: OrientationType
OT_TREND_PLUNGE: OrientationType
OT_VECTOR: OrientationType

class GetOrientationPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "pile_type_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_TYPE_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    pile_type_id: str
    def __init__(self, session_id: _Optional[str] = ..., pile_type_id: _Optional[str] = ...) -> None: ...

class GetOrientationPropertiesResponse(_message.Message):
    __slots__ = ("orientation_props",)
    ORIENTATION_PROPS_FIELD_NUMBER: _ClassVar[int]
    orientation_props: OrientationProperties
    def __init__(self, orientation_props: _Optional[_Union[OrientationProperties, _Mapping]] = ...) -> None: ...

class SetOrientationPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_type_id", "orientation_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_TYPE_ID_FIELD_NUMBER: _ClassVar[int]
    ORIENTATION_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_type_id: str
    orientation_props: OrientationProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_type_id: _Optional[str] = ..., orientation_props: _Optional[_Union[OrientationProperties, _Mapping]] = ...) -> None: ...

class SetOrientationPropertiesResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class OrientationProperties(_message.Message):
    __slots__ = ("rotation_angle", "m_orientation_type")
    ROTATION_ANGLE_FIELD_NUMBER: _ClassVar[int]
    M_ORIENTATION_TYPE_FIELD_NUMBER: _ClassVar[int]
    rotation_angle: float
    m_orientation_type: OrientationType
    def __init__(self, rotation_angle: _Optional[float] = ..., m_orientation_type: _Optional[_Union[OrientationType, str]] = ...) -> None: ...
