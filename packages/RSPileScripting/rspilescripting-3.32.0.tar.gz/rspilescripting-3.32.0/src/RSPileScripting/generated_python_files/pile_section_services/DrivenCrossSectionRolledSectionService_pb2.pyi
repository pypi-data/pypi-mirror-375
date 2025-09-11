from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RolledSectionPerimeter(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PERIMETER_UNSPECIFIED: _ClassVar[RolledSectionPerimeter]
    E_H_PILE_PERIMETER: _ClassVar[RolledSectionPerimeter]
    E_H_BOX_PERIMETER: _ClassVar[RolledSectionPerimeter]

class RolledSectionArea(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AREA_UNSPECIFIED: _ClassVar[RolledSectionArea]
    E_H_PILE_AREA: _ClassVar[RolledSectionArea]
    E_H_BOX_AREA: _ClassVar[RolledSectionArea]
    E_H_USER_SELECT: _ClassVar[RolledSectionArea]
PERIMETER_UNSPECIFIED: RolledSectionPerimeter
E_H_PILE_PERIMETER: RolledSectionPerimeter
E_H_BOX_PERIMETER: RolledSectionPerimeter
AREA_UNSPECIFIED: RolledSectionArea
E_H_PILE_AREA: RolledSectionArea
E_H_BOX_AREA: RolledSectionArea
E_H_USER_SELECT: RolledSectionArea

class GetRolledSectionPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ...) -> None: ...

class GetRolledSectionPropertiesResponse(_message.Message):
    __slots__ = ("rolled_section_props",)
    ROLLED_SECTION_PROPS_FIELD_NUMBER: _ClassVar[int]
    rolled_section_props: RolledSectionProperties
    def __init__(self, rolled_section_props: _Optional[_Union[RolledSectionProperties, _Mapping]] = ...) -> None: ...

class SetRolledSectionPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id", "rolled_section_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    ROLLED_SECTION_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    rolled_section_props: RolledSectionProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ..., rolled_section_props: _Optional[_Union[RolledSectionProperties, _Mapping]] = ...) -> None: ...

class SetRolledSectionPropertiesResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class RolledSectionProperties(_message.Message):
    __slots__ = ("depth", "width", "section_area", "box_area", "section_perimeter", "box_perimeter", "minimum_moment_of_inertia", "maximum_moment_of_inertia", "weight", "web_thickness", "flange_thickness", "designation", "area_for_end_bearing", "perimeter_for_skin_friction", "shape", "type")
    DEPTH_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    SECTION_AREA_FIELD_NUMBER: _ClassVar[int]
    BOX_AREA_FIELD_NUMBER: _ClassVar[int]
    SECTION_PERIMETER_FIELD_NUMBER: _ClassVar[int]
    BOX_PERIMETER_FIELD_NUMBER: _ClassVar[int]
    MINIMUM_MOMENT_OF_INERTIA_FIELD_NUMBER: _ClassVar[int]
    MAXIMUM_MOMENT_OF_INERTIA_FIELD_NUMBER: _ClassVar[int]
    WEIGHT_FIELD_NUMBER: _ClassVar[int]
    WEB_THICKNESS_FIELD_NUMBER: _ClassVar[int]
    FLANGE_THICKNESS_FIELD_NUMBER: _ClassVar[int]
    DESIGNATION_FIELD_NUMBER: _ClassVar[int]
    AREA_FOR_END_BEARING_FIELD_NUMBER: _ClassVar[int]
    PERIMETER_FOR_SKIN_FRICTION_FIELD_NUMBER: _ClassVar[int]
    SHAPE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    depth: float
    width: float
    section_area: float
    box_area: float
    section_perimeter: float
    box_perimeter: float
    minimum_moment_of_inertia: float
    maximum_moment_of_inertia: float
    weight: float
    web_thickness: float
    flange_thickness: float
    designation: str
    area_for_end_bearing: RolledSectionArea
    perimeter_for_skin_friction: RolledSectionPerimeter
    shape: str
    type: str
    def __init__(self, depth: _Optional[float] = ..., width: _Optional[float] = ..., section_area: _Optional[float] = ..., box_area: _Optional[float] = ..., section_perimeter: _Optional[float] = ..., box_perimeter: _Optional[float] = ..., minimum_moment_of_inertia: _Optional[float] = ..., maximum_moment_of_inertia: _Optional[float] = ..., weight: _Optional[float] = ..., web_thickness: _Optional[float] = ..., flange_thickness: _Optional[float] = ..., designation: _Optional[str] = ..., area_for_end_bearing: _Optional[_Union[RolledSectionArea, str]] = ..., perimeter_for_skin_friction: _Optional[_Union[RolledSectionPerimeter, str]] = ..., shape: _Optional[str] = ..., type: _Optional[str] = ...) -> None: ...
