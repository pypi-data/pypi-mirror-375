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
    __slots__ = ("uses_py_curve_bottom", "py_curve", "py_curve_bottom")
    USES_PY_CURVE_BOTTOM_FIELD_NUMBER: _ClassVar[int]
    PY_CURVE_FIELD_NUMBER: _ClassVar[int]
    PY_CURVE_BOTTOM_FIELD_NUMBER: _ClassVar[int]
    uses_py_curve_bottom: bool
    py_curve: _containers.RepeatedCompositeFieldContainer[DPoint]
    py_curve_bottom: _containers.RepeatedCompositeFieldContainer[DPoint]
    def __init__(self, uses_py_curve_bottom: bool = ..., py_curve: _Optional[_Iterable[_Union[DPoint, _Mapping]]] = ..., py_curve_bottom: _Optional[_Iterable[_Union[DPoint, _Mapping]]] = ...) -> None: ...

class DPoint(_message.Message):
    __slots__ = ("x_value", "y_value")
    X_VALUE_FIELD_NUMBER: _ClassVar[int]
    Y_VALUE_FIELD_NUMBER: _ClassVar[int]
    x_value: float
    y_value: float
    def __init__(self, x_value: _Optional[float] = ..., y_value: _Optional[float] = ...) -> None: ...
