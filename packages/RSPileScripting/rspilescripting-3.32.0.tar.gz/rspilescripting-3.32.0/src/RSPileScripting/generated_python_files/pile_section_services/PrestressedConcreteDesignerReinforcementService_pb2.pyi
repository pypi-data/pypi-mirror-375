from pile_section_services import CommonReinforcement_pb2 as _CommonReinforcement_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetReinforcementPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ...) -> None: ...

class GetReinforcementPropertiesResponse(_message.Message):
    __slots__ = ("reinforcement_props",)
    REINFORCEMENT_PROPS_FIELD_NUMBER: _ClassVar[int]
    reinforcement_props: ReinforcementProperties
    def __init__(self, reinforcement_props: _Optional[_Union[ReinforcementProperties, _Mapping]] = ...) -> None: ...

class SetReinforcementPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id", "reinforcement_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    REINFORCEMENT_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    reinforcement_props: ReinforcementProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ..., reinforcement_props: _Optional[_Union[ReinforcementProperties, _Mapping]] = ...) -> None: ...

class SetReinforcementPropertiesResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ReinforcementProperties(_message.Message):
    __slots__ = ("prestress_force_before_losses", "fraction_of_loss_of_prestress")
    PRESTRESS_FORCE_BEFORE_LOSSES_FIELD_NUMBER: _ClassVar[int]
    FRACTION_OF_LOSS_OF_PRESTRESS_FIELD_NUMBER: _ClassVar[int]
    prestress_force_before_losses: float
    fraction_of_loss_of_prestress: float
    def __init__(self, prestress_force_before_losses: _Optional[float] = ..., fraction_of_loss_of_prestress: _Optional[float] = ...) -> None: ...
