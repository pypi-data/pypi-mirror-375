from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class BoredSoilType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    BORED_TYPE_UNSPECIFIED: _ClassVar[BoredSoilType]
    E_BORED_COHESIONLESS: _ClassVar[BoredSoilType]
    E_BORED_COHESIVE: _ClassVar[BoredSoilType]
    E_BORED_WEAK_ROCK: _ClassVar[BoredSoilType]
BORED_TYPE_UNSPECIFIED: BoredSoilType
E_BORED_COHESIONLESS: BoredSoilType
E_BORED_COHESIVE: BoredSoilType
E_BORED_WEAK_ROCK: BoredSoilType

class GetBoredSoilRequest(_message.Message):
    __slots__ = ("session_id", "soil_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    soil_id: str
    def __init__(self, session_id: _Optional[str] = ..., soil_id: _Optional[str] = ...) -> None: ...

class GetBoredSoilResponse(_message.Message):
    __slots__ = ("bored_soil_props",)
    BORED_SOIL_PROPS_FIELD_NUMBER: _ClassVar[int]
    bored_soil_props: BoredSoilProperties
    def __init__(self, bored_soil_props: _Optional[_Union[BoredSoilProperties, _Mapping]] = ...) -> None: ...

class SetBoredSoilRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "soil_id", "bored_soil_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    BORED_SOIL_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    soil_id: str
    bored_soil_props: BoredSoilProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., soil_id: _Optional[str] = ..., bored_soil_props: _Optional[_Union[BoredSoilProperties, _Mapping]] = ...) -> None: ...

class SetBoredSoilResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class BoredSoilProperties(_message.Message):
    __slots__ = ("bored_soil_type", "enable_reductions_factor", "skin_resistance_loss", "end_bearing_loss")
    BORED_SOIL_TYPE_FIELD_NUMBER: _ClassVar[int]
    ENABLE_REDUCTIONS_FACTOR_FIELD_NUMBER: _ClassVar[int]
    SKIN_RESISTANCE_LOSS_FIELD_NUMBER: _ClassVar[int]
    END_BEARING_LOSS_FIELD_NUMBER: _ClassVar[int]
    bored_soil_type: BoredSoilType
    enable_reductions_factor: bool
    skin_resistance_loss: float
    end_bearing_loss: float
    def __init__(self, bored_soil_type: _Optional[_Union[BoredSoilType, str]] = ..., enable_reductions_factor: bool = ..., skin_resistance_loss: _Optional[float] = ..., end_bearing_loss: _Optional[float] = ...) -> None: ...
