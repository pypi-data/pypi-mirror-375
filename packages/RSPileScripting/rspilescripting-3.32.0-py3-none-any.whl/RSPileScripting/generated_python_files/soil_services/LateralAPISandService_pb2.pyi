from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetAPISandRequest(_message.Message):
    __slots__ = ("session_id", "soil_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    soil_id: str
    def __init__(self, session_id: _Optional[str] = ..., soil_id: _Optional[str] = ...) -> None: ...

class GetAPISandResponse(_message.Message):
    __slots__ = ("api_sand_props",)
    API_SAND_PROPS_FIELD_NUMBER: _ClassVar[int]
    api_sand_props: APISandProperties
    def __init__(self, api_sand_props: _Optional[_Union[APISandProperties, _Mapping]] = ...) -> None: ...

class SetAPISandRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "soil_id", "api_sand_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    API_SAND_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    soil_id: str
    api_sand_props: APISandProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., soil_id: _Optional[str] = ..., api_sand_props: _Optional[_Union[APISandProperties, _Mapping]] = ...) -> None: ...

class SetAPISandResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class APISandProperties(_message.Message):
    __slots__ = ("friction_angle_api_sand", "initial_modulus_of_subgrade_reaction")
    FRICTION_ANGLE_API_SAND_FIELD_NUMBER: _ClassVar[int]
    INITIAL_MODULUS_OF_SUBGRADE_REACTION_FIELD_NUMBER: _ClassVar[int]
    friction_angle_api_sand: float
    initial_modulus_of_subgrade_reaction: float
    def __init__(self, friction_angle_api_sand: _Optional[float] = ..., initial_modulus_of_subgrade_reaction: _Optional[float] = ...) -> None: ...
