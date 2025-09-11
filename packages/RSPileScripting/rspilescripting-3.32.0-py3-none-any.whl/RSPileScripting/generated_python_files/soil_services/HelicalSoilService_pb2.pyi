from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetHelicalSoilRequest(_message.Message):
    __slots__ = ("session_id", "soil_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    soil_id: str
    def __init__(self, session_id: _Optional[str] = ..., soil_id: _Optional[str] = ...) -> None: ...

class GetHelicalSoilResponse(_message.Message):
    __slots__ = ("helical_soil_props",)
    HELICAL_SOIL_PROPS_FIELD_NUMBER: _ClassVar[int]
    helical_soil_props: HelicalSoilProperties
    def __init__(self, helical_soil_props: _Optional[_Union[HelicalSoilProperties, _Mapping]] = ...) -> None: ...

class SetHelicalSoilRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "soil_id", "helical_soil_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    HELICAL_SOIL_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    soil_id: str
    helical_soil_props: HelicalSoilProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., soil_id: _Optional[str] = ..., helical_soil_props: _Optional[_Union[HelicalSoilProperties, _Mapping]] = ...) -> None: ...

class SetHelicalSoilResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class HelicalSoilProperties(_message.Message):
    __slots__ = ("m_soilType",)
    M_SOILTYPE_FIELD_NUMBER: _ClassVar[int]
    m_soilType: str
    def __init__(self, m_soilType: _Optional[str] = ...) -> None: ...
