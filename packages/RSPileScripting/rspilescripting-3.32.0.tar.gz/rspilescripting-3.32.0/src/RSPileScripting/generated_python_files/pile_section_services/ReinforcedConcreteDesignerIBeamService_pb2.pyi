from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetIBeamPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ...) -> None: ...

class GetIBeamPropertiesResponse(_message.Message):
    __slots__ = ("ibeam_props",)
    IBEAM_PROPS_FIELD_NUMBER: _ClassVar[int]
    ibeam_props: IBeamProperties
    def __init__(self, ibeam_props: _Optional[_Union[IBeamProperties, _Mapping]] = ...) -> None: ...

class SetIBeamPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id", "ibeam_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    IBEAM_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    ibeam_props: IBeamProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ..., ibeam_props: _Optional[_Union[IBeamProperties, _Mapping]] = ...) -> None: ...

class SetIBeamPropertiesResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class IBeamProperties(_message.Message):
    __slots__ = ("yield_stress_of_beam", "elastic_modulus_of_beam", "ibeam_type", "is_canadian_steel", "has_ibeam")
    YIELD_STRESS_OF_BEAM_FIELD_NUMBER: _ClassVar[int]
    ELASTIC_MODULUS_OF_BEAM_FIELD_NUMBER: _ClassVar[int]
    IBEAM_TYPE_FIELD_NUMBER: _ClassVar[int]
    IS_CANADIAN_STEEL_FIELD_NUMBER: _ClassVar[int]
    HAS_IBEAM_FIELD_NUMBER: _ClassVar[int]
    yield_stress_of_beam: float
    elastic_modulus_of_beam: float
    ibeam_type: str
    is_canadian_steel: bool
    has_ibeam: bool
    def __init__(self, yield_stress_of_beam: _Optional[float] = ..., elastic_modulus_of_beam: _Optional[float] = ..., ibeam_type: _Optional[str] = ..., is_canadian_steel: bool = ..., has_ibeam: bool = ...) -> None: ...
