from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetSPTUserFactorsRequest(_message.Message):
    __slots__ = ("session_id", "soil_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    soil_id: str
    def __init__(self, session_id: _Optional[str] = ..., soil_id: _Optional[str] = ...) -> None: ...

class GetSPTUserFactorsResponse(_message.Message):
    __slots__ = ("spt_user_factors_props",)
    SPT_USER_FACTORS_PROPS_FIELD_NUMBER: _ClassVar[int]
    spt_user_factors_props: SPTUserFactorsProperties
    def __init__(self, spt_user_factors_props: _Optional[_Union[SPTUserFactorsProperties, _Mapping]] = ...) -> None: ...

class SetSPTUserFactorsRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "soil_id", "spt_user_factors_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    SPT_USER_FACTORS_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    soil_id: str
    spt_user_factors_props: SPTUserFactorsProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., soil_id: _Optional[str] = ..., spt_user_factors_props: _Optional[_Union[SPTUserFactorsProperties, _Mapping]] = ...) -> None: ...

class SetSPTUserFactorsResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SPTUserFactorsProperties(_message.Message):
    __slots__ = ("a", "b", "c", "d", "user_fs_limit", "user_qb_limit")
    A_FIELD_NUMBER: _ClassVar[int]
    B_FIELD_NUMBER: _ClassVar[int]
    C_FIELD_NUMBER: _ClassVar[int]
    D_FIELD_NUMBER: _ClassVar[int]
    USER_FS_LIMIT_FIELD_NUMBER: _ClassVar[int]
    USER_QB_LIMIT_FIELD_NUMBER: _ClassVar[int]
    a: float
    b: float
    c: float
    d: float
    user_fs_limit: float
    user_qb_limit: float
    def __init__(self, a: _Optional[float] = ..., b: _Optional[float] = ..., c: _Optional[float] = ..., d: _Optional[float] = ..., user_fs_limit: _Optional[float] = ..., user_qb_limit: _Optional[float] = ...) -> None: ...
