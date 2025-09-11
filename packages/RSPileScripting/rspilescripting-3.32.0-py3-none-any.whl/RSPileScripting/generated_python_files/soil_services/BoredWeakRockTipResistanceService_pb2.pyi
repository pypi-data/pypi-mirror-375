from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TipResistanceType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TIP_RESISTANCE_TYPE_UNSPECIFIED: _ClassVar[TipResistanceType]
    E_WR_TP_USER_DEF: _ClassVar[TipResistanceType]
    E_WR_TP_ZHANG_EINSTEIN: _ClassVar[TipResistanceType]
    E_WR_TP_TOMLINSON: _ClassVar[TipResistanceType]
TIP_RESISTANCE_TYPE_UNSPECIFIED: TipResistanceType
E_WR_TP_USER_DEF: TipResistanceType
E_WR_TP_ZHANG_EINSTEIN: TipResistanceType
E_WR_TP_TOMLINSON: TipResistanceType

class GetTipResistanceRequest(_message.Message):
    __slots__ = ("session_id", "soil_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    soil_id: str
    def __init__(self, session_id: _Optional[str] = ..., soil_id: _Optional[str] = ...) -> None: ...

class GetTipResistanceResponse(_message.Message):
    __slots__ = ("tip_resistance_props",)
    TIP_RESISTANCE_PROPS_FIELD_NUMBER: _ClassVar[int]
    tip_resistance_props: TipResistanceProperties
    def __init__(self, tip_resistance_props: _Optional[_Union[TipResistanceProperties, _Mapping]] = ...) -> None: ...

class SetTipResistanceRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "soil_id", "tip_resistance_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    TIP_RESISTANCE_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    soil_id: str
    tip_resistance_props: TipResistanceProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., soil_id: _Optional[str] = ..., tip_resistance_props: _Optional[_Union[TipResistanceProperties, _Mapping]] = ...) -> None: ...

class SetTipResistanceResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class TipResistanceProperties(_message.Message):
    __slots__ = ("tip_resistance_type",)
    TIP_RESISTANCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    tip_resistance_type: TipResistanceType
    def __init__(self, tip_resistance_type: _Optional[_Union[TipResistanceType, str]] = ...) -> None: ...
