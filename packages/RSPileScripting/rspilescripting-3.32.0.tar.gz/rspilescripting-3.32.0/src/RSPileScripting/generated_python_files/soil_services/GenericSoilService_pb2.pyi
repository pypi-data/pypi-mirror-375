from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class HatchStyles(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    HATCH_UNSPECIFIED: _ClassVar[HatchStyles]
    HORIZONTAL: _ClassVar[HatchStyles]
    VERTICAL: _ClassVar[HatchStyles]
    FDIAGONAL: _ClassVar[HatchStyles]
    BDIAGONAL: _ClassVar[HatchStyles]
    CROSS: _ClassVar[HatchStyles]
    DIAGCROSS: _ClassVar[HatchStyles]
    SOLID_FILL: _ClassVar[HatchStyles]
HATCH_UNSPECIFIED: HatchStyles
HORIZONTAL: HatchStyles
VERTICAL: HatchStyles
FDIAGONAL: HatchStyles
BDIAGONAL: HatchStyles
CROSS: HatchStyles
DIAGCROSS: HatchStyles
SOLID_FILL: HatchStyles

class GetGenericSoilRequest(_message.Message):
    __slots__ = ("session_id", "soil_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    soil_id: str
    def __init__(self, session_id: _Optional[str] = ..., soil_id: _Optional[str] = ...) -> None: ...

class GetGenericSoilResponse(_message.Message):
    __slots__ = ("generic_soil_props",)
    GENERIC_SOIL_PROPS_FIELD_NUMBER: _ClassVar[int]
    generic_soil_props: GenericSoilProperties
    def __init__(self, generic_soil_props: _Optional[_Union[GenericSoilProperties, _Mapping]] = ...) -> None: ...

class SetGenericSoilRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "soil_id", "generic_soil_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    GENERIC_SOIL_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    soil_id: str
    generic_soil_props: GenericSoilProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., soil_id: _Optional[str] = ..., generic_soil_props: _Optional[_Union[GenericSoilProperties, _Mapping]] = ...) -> None: ...

class SetGenericSoilResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GenericSoilProperties(_message.Message):
    __slots__ = ("soil_name", "soil_color", "hatch_style", "soil_unit_weight", "use_saturated_unit_weight", "saturated_unit_weight", "m_consider_datum_dependency")
    SOIL_NAME_FIELD_NUMBER: _ClassVar[int]
    SOIL_COLOR_FIELD_NUMBER: _ClassVar[int]
    HATCH_STYLE_FIELD_NUMBER: _ClassVar[int]
    SOIL_UNIT_WEIGHT_FIELD_NUMBER: _ClassVar[int]
    USE_SATURATED_UNIT_WEIGHT_FIELD_NUMBER: _ClassVar[int]
    SATURATED_UNIT_WEIGHT_FIELD_NUMBER: _ClassVar[int]
    M_CONSIDER_DATUM_DEPENDENCY_FIELD_NUMBER: _ClassVar[int]
    soil_name: str
    soil_color: int
    hatch_style: HatchStyles
    soil_unit_weight: float
    use_saturated_unit_weight: bool
    saturated_unit_weight: float
    m_consider_datum_dependency: bool
    def __init__(self, soil_name: _Optional[str] = ..., soil_color: _Optional[int] = ..., hatch_style: _Optional[_Union[HatchStyles, str]] = ..., soil_unit_weight: _Optional[float] = ..., use_saturated_unit_weight: bool = ..., saturated_unit_weight: _Optional[float] = ..., m_consider_datum_dependency: bool = ...) -> None: ...
