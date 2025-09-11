from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SkinResistanceType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SKIN_RESISTANCE_TYPE_UNSPECIFIED: _ClassVar[SkinResistanceType]
    E_WR_SR_WILLIAM_PELLS: _ClassVar[SkinResistanceType]
    E_WR_SR_KULHAWY_PHOON: _ClassVar[SkinResistanceType]
SKIN_RESISTANCE_TYPE_UNSPECIFIED: SkinResistanceType
E_WR_SR_WILLIAM_PELLS: SkinResistanceType
E_WR_SR_KULHAWY_PHOON: SkinResistanceType

class GetSkinResistanceRequest(_message.Message):
    __slots__ = ("session_id", "soil_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    soil_id: str
    def __init__(self, session_id: _Optional[str] = ..., soil_id: _Optional[str] = ...) -> None: ...

class GetSkinResistanceResponse(_message.Message):
    __slots__ = ("skin_resistance_props",)
    SKIN_RESISTANCE_PROPS_FIELD_NUMBER: _ClassVar[int]
    skin_resistance_props: SkinResistanceProperties
    def __init__(self, skin_resistance_props: _Optional[_Union[SkinResistanceProperties, _Mapping]] = ...) -> None: ...

class SetSkinResistanceRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "soil_id", "skin_resistance_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    SKIN_RESISTANCE_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    soil_id: str
    skin_resistance_props: SkinResistanceProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., soil_id: _Optional[str] = ..., skin_resistance_props: _Optional[_Union[SkinResistanceProperties, _Mapping]] = ...) -> None: ...

class SetSkinResistanceResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SkinResistanceProperties(_message.Message):
    __slots__ = ("skin_resistance_type",)
    SKIN_RESISTANCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    skin_resistance_type: SkinResistanceType
    def __init__(self, skin_resistance_type: _Optional[_Union[SkinResistanceType, str]] = ...) -> None: ...
