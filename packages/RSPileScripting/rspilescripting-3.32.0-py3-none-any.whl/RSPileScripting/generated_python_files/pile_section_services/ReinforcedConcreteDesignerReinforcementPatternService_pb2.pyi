from pile_section_services import CommonReinforcementPattern_pb2 as _CommonReinforcementPattern_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RebarSize(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    REBAR_SIZE_UNSPECIFIED: _ClassVar[RebarSize]
    REBAR_US_STD_3: _ClassVar[RebarSize]
    REBAR_US_STD_4: _ClassVar[RebarSize]
    REBAR_US_STD_5: _ClassVar[RebarSize]
    REBAR_US_STD_6: _ClassVar[RebarSize]
    REBAR_US_STD_7: _ClassVar[RebarSize]
    REBAR_US_STD_8: _ClassVar[RebarSize]
    REBAR_US_STD_9: _ClassVar[RebarSize]
    REBAR_US_STD_10: _ClassVar[RebarSize]
    REBAR_US_STD_11: _ClassVar[RebarSize]
    REBAR_US_STD_14: _ClassVar[RebarSize]
    REBAR_US_STD_18: _ClassVar[RebarSize]
    REBAR_ASTM_10M: _ClassVar[RebarSize]
    REBAR_ASTM_15M: _ClassVar[RebarSize]
    REBAR_ASTM_20M: _ClassVar[RebarSize]
    REBAR_ASTM_25M: _ClassVar[RebarSize]
    REBAR_ASTM_30M: _ClassVar[RebarSize]
    REBAR_ASTM_35M: _ClassVar[RebarSize]
    REBAR_ASTM_45M: _ClassVar[RebarSize]
    REBAR_ASTM_55M: _ClassVar[RebarSize]
    REBAR_CEB_6_MM: _ClassVar[RebarSize]
    REBAR_CEB_8_MM: _ClassVar[RebarSize]
    REBAR_CEB_10_MM: _ClassVar[RebarSize]
    REBAR_CEB_12_MM: _ClassVar[RebarSize]
    REBAR_CEB_14_MM: _ClassVar[RebarSize]
    REBAR_CEB_16_MM: _ClassVar[RebarSize]
    REBAR_CEB_20_MM: _ClassVar[RebarSize]
    REBAR_CEB_25_MM: _ClassVar[RebarSize]
    REBAR_CEB_32_MM: _ClassVar[RebarSize]
    REBAR_CEB_40_MM: _ClassVar[RebarSize]
    REBAR_BS4449_6a: _ClassVar[RebarSize]
    REBAR_BS4449_7a: _ClassVar[RebarSize]
    REBAR_BS4449_8: _ClassVar[RebarSize]
    REBAR_BS4449_9a: _ClassVar[RebarSize]
    REBAR_BS4449_10: _ClassVar[RebarSize]
    REBAR_BS4449_12: _ClassVar[RebarSize]
    REBAR_BS4449_16: _ClassVar[RebarSize]
    REBAR_BS4449_20: _ClassVar[RebarSize]
    REBAR_BS4449_25: _ClassVar[RebarSize]
    REBAR_BS4449_32: _ClassVar[RebarSize]
    REBAR_BS4449_40: _ClassVar[RebarSize]
    REBAR_BS4449_50: _ClassVar[RebarSize]
    REBAR_JD_6: _ClassVar[RebarSize]
    REBAR_JD_8: _ClassVar[RebarSize]
    REBAR_JD_10: _ClassVar[RebarSize]
    REBAR_JD_13: _ClassVar[RebarSize]
    REBAR_JD_16: _ClassVar[RebarSize]
    REBAR_JD_19: _ClassVar[RebarSize]
    REBAR_JD_22: _ClassVar[RebarSize]
    REBAR_JD_25: _ClassVar[RebarSize]
    REBAR_JD_29: _ClassVar[RebarSize]
    REBAR_JD_32: _ClassVar[RebarSize]
    REBAR_JD_35: _ClassVar[RebarSize]
    REBAR_JD_38: _ClassVar[RebarSize]
    REBAR_JD_41: _ClassVar[RebarSize]
    REBAR_AS_12: _ClassVar[RebarSize]
    REBAR_AS_16: _ClassVar[RebarSize]
    REBAR_AS_20: _ClassVar[RebarSize]
    REBAR_AS_24: _ClassVar[RebarSize]
    REBAR_AS_28: _ClassVar[RebarSize]
    REBAR_AS_32: _ClassVar[RebarSize]
    REBAR_AS_36: _ClassVar[RebarSize]
    REBAR_NZ_6: _ClassVar[RebarSize]
    REBAR_NZ_10: _ClassVar[RebarSize]
    REBAR_NZ_12: _ClassVar[RebarSize]
    REBAR_NZ_16: _ClassVar[RebarSize]
    REBAR_NZ_20: _ClassVar[RebarSize]
    REBAR_NZ_25: _ClassVar[RebarSize]
    REBAR_NZ_32: _ClassVar[RebarSize]
    REBAR_NZ_40: _ClassVar[RebarSize]
    REBAR_CUSTOM: _ClassVar[RebarSize]
REBAR_SIZE_UNSPECIFIED: RebarSize
REBAR_US_STD_3: RebarSize
REBAR_US_STD_4: RebarSize
REBAR_US_STD_5: RebarSize
REBAR_US_STD_6: RebarSize
REBAR_US_STD_7: RebarSize
REBAR_US_STD_8: RebarSize
REBAR_US_STD_9: RebarSize
REBAR_US_STD_10: RebarSize
REBAR_US_STD_11: RebarSize
REBAR_US_STD_14: RebarSize
REBAR_US_STD_18: RebarSize
REBAR_ASTM_10M: RebarSize
REBAR_ASTM_15M: RebarSize
REBAR_ASTM_20M: RebarSize
REBAR_ASTM_25M: RebarSize
REBAR_ASTM_30M: RebarSize
REBAR_ASTM_35M: RebarSize
REBAR_ASTM_45M: RebarSize
REBAR_ASTM_55M: RebarSize
REBAR_CEB_6_MM: RebarSize
REBAR_CEB_8_MM: RebarSize
REBAR_CEB_10_MM: RebarSize
REBAR_CEB_12_MM: RebarSize
REBAR_CEB_14_MM: RebarSize
REBAR_CEB_16_MM: RebarSize
REBAR_CEB_20_MM: RebarSize
REBAR_CEB_25_MM: RebarSize
REBAR_CEB_32_MM: RebarSize
REBAR_CEB_40_MM: RebarSize
REBAR_BS4449_6a: RebarSize
REBAR_BS4449_7a: RebarSize
REBAR_BS4449_8: RebarSize
REBAR_BS4449_9a: RebarSize
REBAR_BS4449_10: RebarSize
REBAR_BS4449_12: RebarSize
REBAR_BS4449_16: RebarSize
REBAR_BS4449_20: RebarSize
REBAR_BS4449_25: RebarSize
REBAR_BS4449_32: RebarSize
REBAR_BS4449_40: RebarSize
REBAR_BS4449_50: RebarSize
REBAR_JD_6: RebarSize
REBAR_JD_8: RebarSize
REBAR_JD_10: RebarSize
REBAR_JD_13: RebarSize
REBAR_JD_16: RebarSize
REBAR_JD_19: RebarSize
REBAR_JD_22: RebarSize
REBAR_JD_25: RebarSize
REBAR_JD_29: RebarSize
REBAR_JD_32: RebarSize
REBAR_JD_35: RebarSize
REBAR_JD_38: RebarSize
REBAR_JD_41: RebarSize
REBAR_AS_12: RebarSize
REBAR_AS_16: RebarSize
REBAR_AS_20: RebarSize
REBAR_AS_24: RebarSize
REBAR_AS_28: RebarSize
REBAR_AS_32: RebarSize
REBAR_AS_36: RebarSize
REBAR_NZ_6: RebarSize
REBAR_NZ_10: RebarSize
REBAR_NZ_12: RebarSize
REBAR_NZ_16: RebarSize
REBAR_NZ_20: RebarSize
REBAR_NZ_25: RebarSize
REBAR_NZ_32: RebarSize
REBAR_NZ_40: RebarSize
REBAR_CUSTOM: RebarSize

class GetReinforcementPatternPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "pattern_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    PATTERN_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    pattern_id: str
    def __init__(self, session_id: _Optional[str] = ..., pattern_id: _Optional[str] = ...) -> None: ...

class GetReinforcementPatternPropertiesResponse(_message.Message):
    __slots__ = ("pattern_props",)
    PATTERN_PROPS_FIELD_NUMBER: _ClassVar[int]
    pattern_props: ReinforcementPatternProperties
    def __init__(self, pattern_props: _Optional[_Union[ReinforcementPatternProperties, _Mapping]] = ...) -> None: ...

class SetReinforcementPatternPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pattern_id", "pattern_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PATTERN_ID_FIELD_NUMBER: _ClassVar[int]
    PATTERN_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pattern_id: str
    pattern_props: ReinforcementPatternProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pattern_id: _Optional[str] = ..., pattern_props: _Optional[_Union[ReinforcementPatternProperties, _Mapping]] = ...) -> None: ...

class SetReinforcementPatternPropertiesResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ReinforcementPatternProperties(_message.Message):
    __slots__ = ("name", "rebar_size", "pattern_type", "m_custom_rebar_size", "bundled_bars", "num_bundled", "yield_stress_rebar", "elastic_modulus_rebar")
    NAME_FIELD_NUMBER: _ClassVar[int]
    REBAR_SIZE_FIELD_NUMBER: _ClassVar[int]
    PATTERN_TYPE_FIELD_NUMBER: _ClassVar[int]
    M_CUSTOM_REBAR_SIZE_FIELD_NUMBER: _ClassVar[int]
    BUNDLED_BARS_FIELD_NUMBER: _ClassVar[int]
    NUM_BUNDLED_FIELD_NUMBER: _ClassVar[int]
    YIELD_STRESS_REBAR_FIELD_NUMBER: _ClassVar[int]
    ELASTIC_MODULUS_REBAR_FIELD_NUMBER: _ClassVar[int]
    name: str
    rebar_size: RebarSize
    pattern_type: _CommonReinforcementPattern_pb2.PatternType
    m_custom_rebar_size: float
    bundled_bars: bool
    num_bundled: int
    yield_stress_rebar: float
    elastic_modulus_rebar: float
    def __init__(self, name: _Optional[str] = ..., rebar_size: _Optional[_Union[RebarSize, str]] = ..., pattern_type: _Optional[_Union[_CommonReinforcementPattern_pb2.PatternType, str]] = ..., m_custom_rebar_size: _Optional[float] = ..., bundled_bars: bool = ..., num_bundled: _Optional[int] = ..., yield_stress_rebar: _Optional[float] = ..., elastic_modulus_rebar: _Optional[float] = ...) -> None: ...
