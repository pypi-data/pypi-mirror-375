from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetTomlinsonAndWoodwardRequest(_message.Message):
    __slots__ = ("session_id", "soil_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    soil_id: str
    def __init__(self, session_id: _Optional[str] = ..., soil_id: _Optional[str] = ...) -> None: ...

class GetTomlinsonAndWoodwardResponse(_message.Message):
    __slots__ = ("tomlinson_and_woodward_props",)
    TOMLINSON_AND_WOODWARD_PROPS_FIELD_NUMBER: _ClassVar[int]
    tomlinson_and_woodward_props: TomlinsonAndWoodwardProperties
    def __init__(self, tomlinson_and_woodward_props: _Optional[_Union[TomlinsonAndWoodwardProperties, _Mapping]] = ...) -> None: ...

class SetTomlinsonAndWoodwardRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "soil_id", "tomlinson_and_woodward_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    TOMLINSON_AND_WOODWARD_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    soil_id: str
    tomlinson_and_woodward_props: TomlinsonAndWoodwardProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., soil_id: _Optional[str] = ..., tomlinson_and_woodward_props: _Optional[_Union[TomlinsonAndWoodwardProperties, _Mapping]] = ...) -> None: ...

class SetTomlinsonAndWoodwardResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class TomlinsonAndWoodwardProperties(_message.Message):
    __slots__ = ("angle_of_friction",)
    ANGLE_OF_FRICTION_FIELD_NUMBER: _ClassVar[int]
    angle_of_friction: float
    def __init__(self, angle_of_friction: _Optional[float] = ...) -> None: ...
