from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetClosedEndPipePropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ...) -> None: ...

class GetClosedEndPipePropertiesResponse(_message.Message):
    __slots__ = ("closed_end_pipe_props",)
    CLOSED_END_PIPE_PROPS_FIELD_NUMBER: _ClassVar[int]
    closed_end_pipe_props: ClosedEndPipeProperties
    def __init__(self, closed_end_pipe_props: _Optional[_Union[ClosedEndPipeProperties, _Mapping]] = ...) -> None: ...

class SetClosedEndPipePropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id", "closed_end_pipe_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    CLOSED_END_PIPE_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    closed_end_pipe_props: ClosedEndPipeProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ..., closed_end_pipe_props: _Optional[_Union[ClosedEndPipeProperties, _Mapping]] = ...) -> None: ...

class SetClosedEndPipePropertiesResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ClosedEndPipeProperties(_message.Message):
    __slots__ = ("diameter_ppc",)
    DIAMETER_PPC_FIELD_NUMBER: _ClassVar[int]
    diameter_ppc: float
    def __init__(self, diameter_ppc: _Optional[float] = ...) -> None: ...
