from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class BellBaseDiameterDefinedBy(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    BELL_DIAMETER_UNSPECIFIED: _ClassVar[BellBaseDiameterDefinedBy]
    E_FACTOR_OF_TOP_DIAMETER: _ClassVar[BellBaseDiameterDefinedBy]
    E_VALUE: _ClassVar[BellBaseDiameterDefinedBy]
BELL_DIAMETER_UNSPECIFIED: BellBaseDiameterDefinedBy
E_FACTOR_OF_TOP_DIAMETER: BellBaseDiameterDefinedBy
E_VALUE: BellBaseDiameterDefinedBy

class GetBellPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "pile_type_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_TYPE_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    pile_type_id: str
    def __init__(self, session_id: _Optional[str] = ..., pile_type_id: _Optional[str] = ...) -> None: ...

class GetBellPropertiesResponse(_message.Message):
    __slots__ = ("bell_props",)
    BELL_PROPS_FIELD_NUMBER: _ClassVar[int]
    bell_props: BellProperties
    def __init__(self, bell_props: _Optional[_Union[BellProperties, _Mapping]] = ...) -> None: ...

class SetBellPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_type_id", "bell_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_TYPE_ID_FIELD_NUMBER: _ClassVar[int]
    BELL_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_type_id: str
    bell_props: BellProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_type_id: _Optional[str] = ..., bell_props: _Optional[_Union[BellProperties, _Mapping]] = ...) -> None: ...

class SetBellPropertiesResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class BellProperties(_message.Message):
    __slots__ = ("length_above_bell", "bell_angle", "bell_base_thickness", "bell_base_diameter_defined_by", "base_diameter", "factor")
    LENGTH_ABOVE_BELL_FIELD_NUMBER: _ClassVar[int]
    BELL_ANGLE_FIELD_NUMBER: _ClassVar[int]
    BELL_BASE_THICKNESS_FIELD_NUMBER: _ClassVar[int]
    BELL_BASE_DIAMETER_DEFINED_BY_FIELD_NUMBER: _ClassVar[int]
    BASE_DIAMETER_FIELD_NUMBER: _ClassVar[int]
    FACTOR_FIELD_NUMBER: _ClassVar[int]
    length_above_bell: float
    bell_angle: float
    bell_base_thickness: float
    bell_base_diameter_defined_by: BellBaseDiameterDefinedBy
    base_diameter: float
    factor: float
    def __init__(self, length_above_bell: _Optional[float] = ..., bell_angle: _Optional[float] = ..., bell_base_thickness: _Optional[float] = ..., bell_base_diameter_defined_by: _Optional[_Union[BellBaseDiameterDefinedBy, str]] = ..., base_diameter: _Optional[float] = ..., factor: _Optional[float] = ...) -> None: ...
