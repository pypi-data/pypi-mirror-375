from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class GetNumberOfReinforcementPatternsRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ...) -> None: ...

class GetNumberOfReinforcementPatternsResponse(_message.Message):
    __slots__ = ("number_of_reinforcement_patterns",)
    NUMBER_OF_REINFORCEMENT_PATTERNS_FIELD_NUMBER: _ClassVar[int]
    number_of_reinforcement_patterns: int
    def __init__(self, number_of_reinforcement_patterns: _Optional[int] = ...) -> None: ...

class GetReinforcementPatternRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id", "pattern_index")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    PATTERN_INDEX_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    pattern_index: int
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ..., pattern_index: _Optional[int] = ...) -> None: ...

class GetReinforcementPatternResponse(_message.Message):
    __slots__ = ("pattern_id",)
    PATTERN_ID_FIELD_NUMBER: _ClassVar[int]
    pattern_id: str
    def __init__(self, pattern_id: _Optional[str] = ...) -> None: ...

class AddReinforcementPatternRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id", "name")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    name: str
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...

class AddReinforcementPatternResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class RemoveReinforcementPatternRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id", "name")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    name: str
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...

class RemoveReinforcementPatternResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
