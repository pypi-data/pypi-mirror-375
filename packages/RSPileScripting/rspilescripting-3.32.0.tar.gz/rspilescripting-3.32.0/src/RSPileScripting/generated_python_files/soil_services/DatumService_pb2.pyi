from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetDatumRequest(_message.Message):
    __slots__ = ("session_id", "soil_id", "datum_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    DATUM_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    soil_id: str
    datum_props: DatumProperties
    def __init__(self, session_id: _Optional[str] = ..., soil_id: _Optional[str] = ..., datum_props: _Optional[_Union[DatumProperties, _Mapping]] = ...) -> None: ...

class GetDatumResponse(_message.Message):
    __slots__ = ("datum_bottom_val",)
    DATUM_BOTTOM_VAL_FIELD_NUMBER: _ClassVar[int]
    datum_bottom_val: float
    def __init__(self, datum_bottom_val: _Optional[float] = ...) -> None: ...

class RemoveDatumRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "soil_id", "datum_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    DATUM_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    soil_id: str
    datum_props: DatumProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., soil_id: _Optional[str] = ..., datum_props: _Optional[_Union[DatumProperties, _Mapping]] = ...) -> None: ...

class RemoveDatumResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SetDatumRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "soil_id", "datum_props", "datum_bottom_val")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    DATUM_PROPS_FIELD_NUMBER: _ClassVar[int]
    DATUM_BOTTOM_VAL_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    soil_id: str
    datum_props: DatumProperties
    datum_bottom_val: float
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., soil_id: _Optional[str] = ..., datum_props: _Optional[_Union[DatumProperties, _Mapping]] = ..., datum_bottom_val: _Optional[float] = ...) -> None: ...

class SetDatumResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DatumProperties(_message.Message):
    __slots__ = ("datum_property_enum", "datum_group_enum")
    DATUM_PROPERTY_ENUM_FIELD_NUMBER: _ClassVar[int]
    DATUM_GROUP_ENUM_FIELD_NUMBER: _ClassVar[int]
    datum_property_enum: str
    datum_group_enum: str
    def __init__(self, datum_property_enum: _Optional[str] = ..., datum_group_enum: _Optional[str] = ...) -> None: ...
