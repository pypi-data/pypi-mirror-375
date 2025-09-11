from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetOpenEndPipePropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ...) -> None: ...

class GetOpenEndPipePropertiesResponse(_message.Message):
    __slots__ = ("open_end_pipe_props",)
    OPEN_END_PIPE_PROPS_FIELD_NUMBER: _ClassVar[int]
    open_end_pipe_props: OpenEndPipeProperties
    def __init__(self, open_end_pipe_props: _Optional[_Union[OpenEndPipeProperties, _Mapping]] = ...) -> None: ...

class SetOpenEndPipePropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id", "open_end_pipe_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    OPEN_END_PIPE_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    open_end_pipe_props: OpenEndPipeProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ..., open_end_pipe_props: _Optional[_Union[OpenEndPipeProperties, _Mapping]] = ...) -> None: ...

class SetOpenEndPipePropertiesResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class OpenEndPipeProperties(_message.Message):
    __slots__ = ("diameter_ppo", "shell_thickness_ppo")
    DIAMETER_PPO_FIELD_NUMBER: _ClassVar[int]
    SHELL_THICKNESS_PPO_FIELD_NUMBER: _ClassVar[int]
    diameter_ppo: float
    shell_thickness_ppo: float
    def __init__(self, diameter_ppo: _Optional[float] = ..., shell_thickness_ppo: _Optional[float] = ...) -> None: ...
