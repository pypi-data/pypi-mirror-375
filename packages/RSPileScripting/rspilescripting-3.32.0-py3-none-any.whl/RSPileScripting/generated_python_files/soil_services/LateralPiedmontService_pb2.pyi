from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PiedmontAnalysisType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    LAT_TYPE_UNSPECIFIED: _ClassVar[PiedmontAnalysisType]
    E_DILATOMETER_MODULUS: _ClassVar[PiedmontAnalysisType]
    E_CONE_PENETRATION_TIP_RESISTANCE: _ClassVar[PiedmontAnalysisType]
    E_STANDARD_PENETRATION_BLOW_COUNT: _ClassVar[PiedmontAnalysisType]
    E_MENARD_PRESSUREMETER_MODULUS: _ClassVar[PiedmontAnalysisType]
LAT_TYPE_UNSPECIFIED: PiedmontAnalysisType
E_DILATOMETER_MODULUS: PiedmontAnalysisType
E_CONE_PENETRATION_TIP_RESISTANCE: PiedmontAnalysisType
E_STANDARD_PENETRATION_BLOW_COUNT: PiedmontAnalysisType
E_MENARD_PRESSUREMETER_MODULUS: PiedmontAnalysisType

class GetPiedmontRequest(_message.Message):
    __slots__ = ("session_id", "soil_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    soil_id: str
    def __init__(self, session_id: _Optional[str] = ..., soil_id: _Optional[str] = ...) -> None: ...

class GetPiedmontResponse(_message.Message):
    __slots__ = ("piedmont_props",)
    PIEDMONT_PROPS_FIELD_NUMBER: _ClassVar[int]
    piedmont_props: PiedmontProperties
    def __init__(self, piedmont_props: _Optional[_Union[PiedmontProperties, _Mapping]] = ...) -> None: ...

class SetPiedmontRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "soil_id", "piedmont_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    PIEDMONT_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    soil_id: str
    piedmont_props: PiedmontProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., soil_id: _Optional[str] = ..., piedmont_props: _Optional[_Union[PiedmontProperties, _Mapping]] = ...) -> None: ...

class SetPiedmontResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class PiedmontProperties(_message.Message):
    __slots__ = ("piedmont_analysis_type", "dilatometer_modulus", "cone_penetration_piedmont", "standard_penetration_blow_count", "menard_pressuremeter_modulus")
    PIEDMONT_ANALYSIS_TYPE_FIELD_NUMBER: _ClassVar[int]
    DILATOMETER_MODULUS_FIELD_NUMBER: _ClassVar[int]
    CONE_PENETRATION_PIEDMONT_FIELD_NUMBER: _ClassVar[int]
    STANDARD_PENETRATION_BLOW_COUNT_FIELD_NUMBER: _ClassVar[int]
    MENARD_PRESSUREMETER_MODULUS_FIELD_NUMBER: _ClassVar[int]
    piedmont_analysis_type: PiedmontAnalysisType
    dilatometer_modulus: float
    cone_penetration_piedmont: float
    standard_penetration_blow_count: float
    menard_pressuremeter_modulus: float
    def __init__(self, piedmont_analysis_type: _Optional[_Union[PiedmontAnalysisType, str]] = ..., dilatometer_modulus: _Optional[float] = ..., cone_penetration_piedmont: _Optional[float] = ..., standard_penetration_blow_count: _Optional[float] = ..., menard_pressuremeter_modulus: _Optional[float] = ...) -> None: ...
