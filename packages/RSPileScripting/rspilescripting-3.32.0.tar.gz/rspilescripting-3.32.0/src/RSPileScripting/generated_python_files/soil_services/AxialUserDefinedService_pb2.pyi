from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetUserDefinedRequest(_message.Message):
    __slots__ = ("session_id", "soil_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    soil_id: str
    def __init__(self, session_id: _Optional[str] = ..., soil_id: _Optional[str] = ...) -> None: ...

class GetUserDefinedResponse(_message.Message):
    __slots__ = ("user_defined_props",)
    USER_DEFINED_PROPS_FIELD_NUMBER: _ClassVar[int]
    user_defined_props: UserDefinedProperties
    def __init__(self, user_defined_props: _Optional[_Union[UserDefinedProperties, _Mapping]] = ...) -> None: ...

class SetUserDefinedRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "soil_id", "user_defined_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    soil_id: str
    user_defined_props: UserDefinedProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., soil_id: _Optional[str] = ..., user_defined_props: _Optional[_Union[UserDefinedProperties, _Mapping]] = ...) -> None: ...

class SetUserDefinedResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class UserDefinedProperties(_message.Message):
    __slots__ = ("ultimate_unit_side_friction_top_u", "ultimate_tip_resistance_top_u", "tz_curve", "qz_curve")
    ULTIMATE_UNIT_SIDE_FRICTION_TOP_U_FIELD_NUMBER: _ClassVar[int]
    ULTIMATE_TIP_RESISTANCE_TOP_U_FIELD_NUMBER: _ClassVar[int]
    TZ_CURVE_FIELD_NUMBER: _ClassVar[int]
    QZ_CURVE_FIELD_NUMBER: _ClassVar[int]
    ultimate_unit_side_friction_top_u: float
    ultimate_tip_resistance_top_u: float
    tz_curve: _containers.RepeatedCompositeFieldContainer[DPoint]
    qz_curve: _containers.RepeatedCompositeFieldContainer[DPoint]
    def __init__(self, ultimate_unit_side_friction_top_u: _Optional[float] = ..., ultimate_tip_resistance_top_u: _Optional[float] = ..., tz_curve: _Optional[_Iterable[_Union[DPoint, _Mapping]]] = ..., qz_curve: _Optional[_Iterable[_Union[DPoint, _Mapping]]] = ...) -> None: ...

class DPoint(_message.Message):
    __slots__ = ("x_value", "y_value")
    X_VALUE_FIELD_NUMBER: _ClassVar[int]
    Y_VALUE_FIELD_NUMBER: _ClassVar[int]
    x_value: float
    y_value: float
    def __init__(self, x_value: _Optional[float] = ..., y_value: _Optional[float] = ...) -> None: ...
