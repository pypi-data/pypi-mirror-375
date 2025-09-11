from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetKulhawyAndPhoonRequest(_message.Message):
    __slots__ = ("session_id", "soil_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    soil_id: str
    def __init__(self, session_id: _Optional[str] = ..., soil_id: _Optional[str] = ...) -> None: ...

class GetKulhawyAndPhoonResponse(_message.Message):
    __slots__ = ("kulhawy_and_phoon_props",)
    KULHAWY_AND_PHOON_PROPS_FIELD_NUMBER: _ClassVar[int]
    kulhawy_and_phoon_props: KulhawyAndPhoonProperties
    def __init__(self, kulhawy_and_phoon_props: _Optional[_Union[KulhawyAndPhoonProperties, _Mapping]] = ...) -> None: ...

class SetKulhawyAndPhoonRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "soil_id", "kulhawy_and_phoon_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    KULHAWY_AND_PHOON_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    soil_id: str
    kulhawy_and_phoon_props: KulhawyAndPhoonProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., soil_id: _Optional[str] = ..., kulhawy_and_phoon_props: _Optional[_Union[KulhawyAndPhoonProperties, _Mapping]] = ...) -> None: ...

class SetKulhawyAndPhoonResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class KulhawyAndPhoonProperties(_message.Message):
    __slots__ = ("val_omega",)
    VAL_OMEGA_FIELD_NUMBER: _ClassVar[int]
    val_omega: float
    def __init__(self, val_omega: _Optional[float] = ...) -> None: ...
