from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MaterialType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PILE_TYPE_UNSPECIFIED: _ClassVar[MaterialType]
    PILE_TYPE_ELASTIC: _ClassVar[MaterialType]
    PILE_TYPE_PLASTIC: _ClassVar[MaterialType]
    PILE_TYPE_REINF_CONCRETE: _ClassVar[MaterialType]
    PILE_TYPE_PRESTR_CONCRETE: _ClassVar[MaterialType]
PILE_TYPE_UNSPECIFIED: MaterialType
PILE_TYPE_ELASTIC: MaterialType
PILE_TYPE_PLASTIC: MaterialType
PILE_TYPE_REINF_CONCRETE: MaterialType
PILE_TYPE_PRESTR_CONCRETE: MaterialType

class GetMaterialPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ...) -> None: ...

class GetMaterialPropertiesResponse(_message.Message):
    __slots__ = ("material_props",)
    MATERIAL_PROPS_FIELD_NUMBER: _ClassVar[int]
    material_props: MaterialProperties
    def __init__(self, material_props: _Optional[_Union[MaterialProperties, _Mapping]] = ...) -> None: ...

class SetMaterialPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id", "material_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    MATERIAL_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    material_props: MaterialProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ..., material_props: _Optional[_Union[MaterialProperties, _Mapping]] = ...) -> None: ...

class SetMaterialPropertiesResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class MaterialProperties(_message.Message):
    __slots__ = ("material_type",)
    MATERIAL_TYPE_FIELD_NUMBER: _ClassVar[int]
    material_type: MaterialType
    def __init__(self, material_type: _Optional[_Union[MaterialType, str]] = ...) -> None: ...
