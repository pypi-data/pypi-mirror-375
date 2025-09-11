from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetMassiveRockRequest(_message.Message):
    __slots__ = ("session_id", "soil_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    soil_id: str
    def __init__(self, session_id: _Optional[str] = ..., soil_id: _Optional[str] = ...) -> None: ...

class GetMassiveRockResponse(_message.Message):
    __slots__ = ("massive_rock_props",)
    MASSIVE_ROCK_PROPS_FIELD_NUMBER: _ClassVar[int]
    massive_rock_props: MassiveRockProperties
    def __init__(self, massive_rock_props: _Optional[_Union[MassiveRockProperties, _Mapping]] = ...) -> None: ...

class SetMassiveRockRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "soil_id", "massive_rock_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    MASSIVE_ROCK_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    soil_id: str
    massive_rock_props: MassiveRockProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., soil_id: _Optional[str] = ..., massive_rock_props: _Optional[_Union[MassiveRockProperties, _Mapping]] = ...) -> None: ...

class SetMassiveRockResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class MassiveRockProperties(_message.Message):
    __slots__ = ("use_Erm_MassRock", "mi_MassRock", "GSI_MassRock", "UCS_MassRock", "Ei_MassRock", "Erm_MassRock", "poisson_ratio_MassRock")
    USE_ERM_MASSROCK_FIELD_NUMBER: _ClassVar[int]
    MI_MASSROCK_FIELD_NUMBER: _ClassVar[int]
    GSI_MASSROCK_FIELD_NUMBER: _ClassVar[int]
    UCS_MASSROCK_FIELD_NUMBER: _ClassVar[int]
    EI_MASSROCK_FIELD_NUMBER: _ClassVar[int]
    ERM_MASSROCK_FIELD_NUMBER: _ClassVar[int]
    POISSON_RATIO_MASSROCK_FIELD_NUMBER: _ClassVar[int]
    use_Erm_MassRock: bool
    mi_MassRock: float
    GSI_MassRock: float
    UCS_MassRock: float
    Ei_MassRock: float
    Erm_MassRock: float
    poisson_ratio_MassRock: float
    def __init__(self, use_Erm_MassRock: bool = ..., mi_MassRock: _Optional[float] = ..., GSI_MassRock: _Optional[float] = ..., UCS_MassRock: _Optional[float] = ..., Ei_MassRock: _Optional[float] = ..., Erm_MassRock: _Optional[float] = ..., poisson_ratio_MassRock: _Optional[float] = ...) -> None: ...
