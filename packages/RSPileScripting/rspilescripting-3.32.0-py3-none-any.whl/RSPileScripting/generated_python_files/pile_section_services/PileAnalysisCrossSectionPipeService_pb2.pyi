from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetPipePropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ...) -> None: ...

class GetPipePropertiesResponse(_message.Message):
    __slots__ = ("pipe_props",)
    PIPE_PROPS_FIELD_NUMBER: _ClassVar[int]
    pipe_props: PipeProperties
    def __init__(self, pipe_props: _Optional[_Union[PipeProperties, _Mapping]] = ...) -> None: ...

class SetPipePropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id", "pipe_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    PIPE_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    pipe_props: PipeProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ..., pipe_props: _Optional[_Union[PipeProperties, _Mapping]] = ...) -> None: ...

class SetPipePropertiesResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class PipeProperties(_message.Message):
    __slots__ = ("pipe_outside_diameter", "pipe_wall_thickness")
    PIPE_OUTSIDE_DIAMETER_FIELD_NUMBER: _ClassVar[int]
    PIPE_WALL_THICKNESS_FIELD_NUMBER: _ClassVar[int]
    pipe_outside_diameter: float
    pipe_wall_thickness: float
    def __init__(self, pipe_outside_diameter: _Optional[float] = ..., pipe_wall_thickness: _Optional[float] = ...) -> None: ...
