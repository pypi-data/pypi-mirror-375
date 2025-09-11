from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetAlphaBetaPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "pile_type_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_TYPE_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    pile_type_id: str
    def __init__(self, session_id: _Optional[str] = ..., pile_type_id: _Optional[str] = ...) -> None: ...

class GetAlphaBetaPropertiesResponse(_message.Message):
    __slots__ = ("alpha_beta_props",)
    ALPHA_BETA_PROPS_FIELD_NUMBER: _ClassVar[int]
    alpha_beta_props: AlphaBetaProperties
    def __init__(self, alpha_beta_props: _Optional[_Union[AlphaBetaProperties, _Mapping]] = ...) -> None: ...

class SetAlphaBetaPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_type_id", "alpha_beta_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_TYPE_ID_FIELD_NUMBER: _ClassVar[int]
    ALPHA_BETA_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_type_id: str
    alpha_beta_props: AlphaBetaProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_type_id: _Optional[str] = ..., alpha_beta_props: _Optional[_Union[AlphaBetaProperties, _Mapping]] = ...) -> None: ...

class SetAlphaBetaPropertiesResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class AlphaBetaProperties(_message.Message):
    __slots__ = ("alpha_trend", "beta_plunge")
    ALPHA_TREND_FIELD_NUMBER: _ClassVar[int]
    BETA_PLUNGE_FIELD_NUMBER: _ClassVar[int]
    alpha_trend: float
    beta_plunge: float
    def __init__(self, alpha_trend: _Optional[float] = ..., beta_plunge: _Optional[float] = ...) -> None: ...
