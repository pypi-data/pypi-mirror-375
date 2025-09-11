from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetUserDefinedAdhesionRequest(_message.Message):
    __slots__ = ("session_id", "soil_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    soil_id: str
    def __init__(self, session_id: _Optional[str] = ..., soil_id: _Optional[str] = ...) -> None: ...

class GetUserDefinedAdhesionResponse(_message.Message):
    __slots__ = ("user_defined_adhesion_props",)
    USER_DEFINED_ADHESION_PROPS_FIELD_NUMBER: _ClassVar[int]
    user_defined_adhesion_props: UserDefinedAdhesionProperties
    def __init__(self, user_defined_adhesion_props: _Optional[_Union[UserDefinedAdhesionProperties, _Mapping]] = ...) -> None: ...

class SetUserDefinedAdhesionRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "soil_id", "user_defined_adhesion_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_ADHESION_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    soil_id: str
    user_defined_adhesion_props: UserDefinedAdhesionProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., soil_id: _Optional[str] = ..., user_defined_adhesion_props: _Optional[_Union[UserDefinedAdhesionProperties, _Mapping]] = ...) -> None: ...

class SetUserDefinedAdhesionResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class UserDefinedAdhesionProperties(_message.Message):
    __slots__ = ("user_defined_adhesion",)
    USER_DEFINED_ADHESION_FIELD_NUMBER: _ClassVar[int]
    user_defined_adhesion: float
    def __init__(self, user_defined_adhesion: _Optional[float] = ...) -> None: ...
