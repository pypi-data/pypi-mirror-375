from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetWilliamAndPellsRequest(_message.Message):
    __slots__ = ("session_id", "soil_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    soil_id: str
    def __init__(self, session_id: _Optional[str] = ..., soil_id: _Optional[str] = ...) -> None: ...

class GetWilliamAndPellsResponse(_message.Message):
    __slots__ = ("william_and_pells_props",)
    WILLIAM_AND_PELLS_PROPS_FIELD_NUMBER: _ClassVar[int]
    william_and_pells_props: WilliamAndPellsProperties
    def __init__(self, william_and_pells_props: _Optional[_Union[WilliamAndPellsProperties, _Mapping]] = ...) -> None: ...

class SetWilliamAndPellsRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "soil_id", "william_and_pells_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    WILLIAM_AND_PELLS_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    soil_id: str
    william_and_pells_props: WilliamAndPellsProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., soil_id: _Optional[str] = ..., william_and_pells_props: _Optional[_Union[WilliamAndPellsProperties, _Mapping]] = ...) -> None: ...

class SetWilliamAndPellsResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class WilliamAndPellsProperties(_message.Message):
    __slots__ = ("average_rqd",)
    AVERAGE_RQD_FIELD_NUMBER: _ClassVar[int]
    average_rqd: float
    def __init__(self, average_rqd: _Optional[float] = ...) -> None: ...
