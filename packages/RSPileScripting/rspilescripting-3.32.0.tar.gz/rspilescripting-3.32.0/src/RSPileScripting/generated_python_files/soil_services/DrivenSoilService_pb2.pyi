from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DrivenSoilType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DRIVEN_TYPE_UNSPECIFIED: _ClassVar[DrivenSoilType]
    E_COHESIONLESS: _ClassVar[DrivenSoilType]
    E_COHESIVE: _ClassVar[DrivenSoilType]
DRIVEN_TYPE_UNSPECIFIED: DrivenSoilType
E_COHESIONLESS: DrivenSoilType
E_COHESIVE: DrivenSoilType

class GetDrivenSoilRequest(_message.Message):
    __slots__ = ("session_id", "soil_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    soil_id: str
    def __init__(self, session_id: _Optional[str] = ..., soil_id: _Optional[str] = ...) -> None: ...

class GetDrivenSoilResponse(_message.Message):
    __slots__ = ("driven_soil_props",)
    DRIVEN_SOIL_PROPS_FIELD_NUMBER: _ClassVar[int]
    driven_soil_props: DrivenSoilProperties
    def __init__(self, driven_soil_props: _Optional[_Union[DrivenSoilProperties, _Mapping]] = ...) -> None: ...

class SetDrivenSoilRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "soil_id", "driven_soil_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    DRIVEN_SOIL_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    soil_id: str
    driven_soil_props: DrivenSoilProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., soil_id: _Optional[str] = ..., driven_soil_props: _Optional[_Union[DrivenSoilProperties, _Mapping]] = ...) -> None: ...

class SetDrivenSoilResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DrivenSoilProperties(_message.Message):
    __slots__ = ("driven_soil_type", "driving_strength_loss")
    DRIVEN_SOIL_TYPE_FIELD_NUMBER: _ClassVar[int]
    DRIVING_STRENGTH_LOSS_FIELD_NUMBER: _ClassVar[int]
    driven_soil_type: DrivenSoilType
    driving_strength_loss: float
    def __init__(self, driven_soil_type: _Optional[_Union[DrivenSoilType, str]] = ..., driving_strength_loss: _Optional[float] = ...) -> None: ...
