from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetRaymondPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ...) -> None: ...

class GetRaymondPropertiesResponse(_message.Message):
    __slots__ = ("raymond_props",)
    RAYMOND_PROPS_FIELD_NUMBER: _ClassVar[int]
    raymond_props: RaymondProperties
    def __init__(self, raymond_props: _Optional[_Union[RaymondProperties, _Mapping]] = ...) -> None: ...

class SetRaymondPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id", "raymond_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    RAYMOND_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    raymond_props: RaymondProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ..., raymond_props: _Optional[_Union[RaymondProperties, _Mapping]] = ...) -> None: ...

class SetRaymondPropertiesResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class RaymondProperties(_message.Message):
    __slots__ = ("diameter_raymond",)
    DIAMETER_RAYMOND_FIELD_NUMBER: _ClassVar[int]
    diameter_raymond: float
    def __init__(self, diameter_raymond: _Optional[float] = ...) -> None: ...
