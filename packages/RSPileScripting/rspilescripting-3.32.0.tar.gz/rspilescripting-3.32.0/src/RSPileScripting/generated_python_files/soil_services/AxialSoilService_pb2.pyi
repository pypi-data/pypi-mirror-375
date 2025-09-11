from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AxialSoilType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AXIAL_TYPE_UNSPECIFIED: _ClassVar[AxialSoilType]
    E_SAND_TZ_PILE: _ClassVar[AxialSoilType]
    E_CLAY_TZ_PILE: _ClassVar[AxialSoilType]
    E_USER_DEFINED_TZ_PILE: _ClassVar[AxialSoilType]
    E_TZ_ELASTIC: _ClassVar[AxialSoilType]
    E_COYLE_REESE_CLAY_TZ_PILE: _ClassVar[AxialSoilType]
    E_MOSHER_SAND_TZ_PILE: _ClassVar[AxialSoilType]
    E_DRILLED_CLAY_TZ_PILE: _ClassVar[AxialSoilType]
    E_DRILLED_SAND_TZ_PILE: _ClassVar[AxialSoilType]
AXIAL_TYPE_UNSPECIFIED: AxialSoilType
E_SAND_TZ_PILE: AxialSoilType
E_CLAY_TZ_PILE: AxialSoilType
E_USER_DEFINED_TZ_PILE: AxialSoilType
E_TZ_ELASTIC: AxialSoilType
E_COYLE_REESE_CLAY_TZ_PILE: AxialSoilType
E_MOSHER_SAND_TZ_PILE: AxialSoilType
E_DRILLED_CLAY_TZ_PILE: AxialSoilType
E_DRILLED_SAND_TZ_PILE: AxialSoilType

class GetAxialSoilRequest(_message.Message):
    __slots__ = ("session_id", "soil_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    soil_id: str
    def __init__(self, session_id: _Optional[str] = ..., soil_id: _Optional[str] = ...) -> None: ...

class GetAxialSoilResponse(_message.Message):
    __slots__ = ("axial_soil_props",)
    AXIAL_SOIL_PROPS_FIELD_NUMBER: _ClassVar[int]
    axial_soil_props: AxialSoilProperties
    def __init__(self, axial_soil_props: _Optional[_Union[AxialSoilProperties, _Mapping]] = ...) -> None: ...

class SetAxialSoilRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "soil_id", "axial_soil_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    AXIAL_SOIL_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    soil_id: str
    axial_soil_props: AxialSoilProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., soil_id: _Optional[str] = ..., axial_soil_props: _Optional[_Union[AxialSoilProperties, _Mapping]] = ...) -> None: ...

class SetAxialSoilResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class AxialSoilProperties(_message.Message):
    __slots__ = ("axial_soil_type",)
    AXIAL_SOIL_TYPE_FIELD_NUMBER: _ClassVar[int]
    axial_soil_type: AxialSoilType
    def __init__(self, axial_soil_type: _Optional[_Union[AxialSoilType, str]] = ...) -> None: ...
