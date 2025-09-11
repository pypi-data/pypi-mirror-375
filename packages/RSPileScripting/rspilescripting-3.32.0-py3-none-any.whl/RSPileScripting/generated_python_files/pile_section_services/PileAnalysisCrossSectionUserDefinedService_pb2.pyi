from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetUserDefinedPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ...) -> None: ...

class GetUserDefinedPropertiesResponse(_message.Message):
    __slots__ = ("user_defined_props",)
    USER_DEFINED_PROPS_FIELD_NUMBER: _ClassVar[int]
    user_defined_props: UserDefinedProperties
    def __init__(self, user_defined_props: _Optional[_Union[UserDefinedProperties, _Mapping]] = ...) -> None: ...

class SetUserDefinedPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id", "user_defined_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    user_defined_props: UserDefinedProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ..., user_defined_props: _Optional[_Union[UserDefinedProperties, _Mapping]] = ...) -> None: ...

class SetUserDefinedPropertiesResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class UserDefinedProperties(_message.Message):
    __slots__ = ("diameter", "perimeter", "area", "Iy", "Iz")
    DIAMETER_FIELD_NUMBER: _ClassVar[int]
    PERIMETER_FIELD_NUMBER: _ClassVar[int]
    AREA_FIELD_NUMBER: _ClassVar[int]
    IY_FIELD_NUMBER: _ClassVar[int]
    IZ_FIELD_NUMBER: _ClassVar[int]
    diameter: float
    perimeter: float
    area: float
    Iy: float
    Iz: float
    def __init__(self, diameter: _Optional[float] = ..., perimeter: _Optional[float] = ..., area: _Optional[float] = ..., Iy: _Optional[float] = ..., Iz: _Optional[float] = ...) -> None: ...
