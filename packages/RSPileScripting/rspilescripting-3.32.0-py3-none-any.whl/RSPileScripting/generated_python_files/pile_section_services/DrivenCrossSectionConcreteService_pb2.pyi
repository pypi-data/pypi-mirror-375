from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetConcretePropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ...) -> None: ...

class GetConcretePropertiesResponse(_message.Message):
    __slots__ = ("concrete_props",)
    CONCRETE_PROPS_FIELD_NUMBER: _ClassVar[int]
    concrete_props: ConcreteProperties
    def __init__(self, concrete_props: _Optional[_Union[ConcreteProperties, _Mapping]] = ...) -> None: ...

class SetConcretePropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id", "concrete_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    concrete_props: ConcreteProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ..., concrete_props: _Optional[_Union[ConcreteProperties, _Mapping]] = ...) -> None: ...

class SetConcretePropertiesResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ConcreteProperties(_message.Message):
    __slots__ = ("side_c",)
    SIDE_C_FIELD_NUMBER: _ClassVar[int]
    side_c: float
    def __init__(self, side_c: _Optional[float] = ...) -> None: ...
