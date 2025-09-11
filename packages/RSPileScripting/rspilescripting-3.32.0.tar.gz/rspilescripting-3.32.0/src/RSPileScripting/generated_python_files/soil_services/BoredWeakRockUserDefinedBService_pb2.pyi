from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetUserDefinedBRequest(_message.Message):
    __slots__ = ("session_id", "soil_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    soil_id: str
    def __init__(self, session_id: _Optional[str] = ..., soil_id: _Optional[str] = ...) -> None: ...

class GetUserDefinedBResponse(_message.Message):
    __slots__ = ("user_defined_b_props",)
    USER_DEFINED_B_PROPS_FIELD_NUMBER: _ClassVar[int]
    user_defined_b_props: UserDefinedBProperties
    def __init__(self, user_defined_b_props: _Optional[_Union[UserDefinedBProperties, _Mapping]] = ...) -> None: ...

class SetUserDefinedBRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "soil_id", "user_defined_b_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_B_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    soil_id: str
    user_defined_b_props: UserDefinedBProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., soil_id: _Optional[str] = ..., user_defined_b_props: _Optional[_Union[UserDefinedBProperties, _Mapping]] = ...) -> None: ...

class SetUserDefinedBResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class UserDefinedBProperties(_message.Message):
    __slots__ = ("user_def_b",)
    USER_DEF_B_FIELD_NUMBER: _ClassVar[int]
    user_def_b: float
    def __init__(self, user_def_b: _Optional[float] = ...) -> None: ...
