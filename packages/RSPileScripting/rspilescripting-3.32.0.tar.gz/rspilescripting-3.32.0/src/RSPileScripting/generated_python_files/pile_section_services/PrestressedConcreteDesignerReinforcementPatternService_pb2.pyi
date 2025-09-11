from pile_section_services import CommonReinforcementPattern_pb2 as _CommonReinforcementPattern_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class StrandType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    STRAND_TYPE_UNSPECIFIED: _ClassVar[StrandType]
    STRAND_TYPE_GRADE_250_KSI_LOLAX: _ClassVar[StrandType]
    STRAND_TYPE_GRADE_270_KSI_LOLAX: _ClassVar[StrandType]
    STRAND_TYPE_GRADE_300_KSI_LOLAX: _ClassVar[StrandType]
    STRAND_TYPE_SMOOTH_BARS_145_KSI: _ClassVar[StrandType]
    STRAND_TYPE_SMOOTH_BARS_160_KSI: _ClassVar[StrandType]
    STRAND_TYPE_DEFORMED_BARS_150_160_KSI: _ClassVar[StrandType]

class StrandSize(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    STRAND_SIZE_UNSPECIFIED: _ClassVar[StrandSize]
    STRAND_SIZE_250_5_16_3_WIRE: _ClassVar[StrandSize]
    STRAND_SIZE_250_1_4_7_WIRE: _ClassVar[StrandSize]
    STRAND_SIZE_250_5_16_7_WIRE: _ClassVar[StrandSize]
    STRAND_SIZE_250_3_8_7_WIRE: _ClassVar[StrandSize]
    STRAND_SIZE_250_7_16_7_WIRE: _ClassVar[StrandSize]
    STRAND_SIZE_250_1_2_7_WIRE: _ClassVar[StrandSize]
    STRAND_SIZE_250_06_7_WIRE: _ClassVar[StrandSize]
    STRAND_SIZE_270_5_16_7_WIRE: _ClassVar[StrandSize]
    STRAND_SIZE_270_3_8_7_WIRE: _ClassVar[StrandSize]
    STRAND_SIZE_270_7_16_7_WIRE: _ClassVar[StrandSize]
    STRAND_SIZE_270_1_2_7_WIRE: _ClassVar[StrandSize]
    STRAND_SIZE_270_1_2_7_W_SPEC: _ClassVar[StrandSize]
    STRAND_SIZE_270_9_16_7_WIRE: _ClassVar[StrandSize]
    STRAND_SIZE_270_0_6_7_WIRE: _ClassVar[StrandSize]
    STRAND_SIZE_270_0_7_7_WIRE: _ClassVar[StrandSize]
    STRAND_SIZE_300_3_8_7_WIRE: _ClassVar[StrandSize]
    STRAND_SIZE_300_7_16_7_WIRE: _ClassVar[StrandSize]
    STRAND_SIZE_300_1_2_7_WIRE: _ClassVar[StrandSize]
    STRAND_SIZE_300_1_2_SUPER: _ClassVar[StrandSize]
    STRAND_SIZE_300_0_6_7_WIRE: _ClassVar[StrandSize]
    STRAND_SIZE_145_3_4_SMOOTH: _ClassVar[StrandSize]
    STRAND_SIZE_145_7_8_SMOOTH: _ClassVar[StrandSize]
    STRAND_SIZE_145_1_SMOOTH: _ClassVar[StrandSize]
    STRAND_SIZE_145_1_1_8_SMOOTH: _ClassVar[StrandSize]
    STRAND_SIZE_145_1_1_4_SMOOTH: _ClassVar[StrandSize]
    STRAND_SIZE_145_1_3_8_SMOOTH: _ClassVar[StrandSize]
    STRAND_SIZE_160_3_4_SMOOTH: _ClassVar[StrandSize]
    STRAND_SIZE_160_7_8_SMOOTH: _ClassVar[StrandSize]
    STRAND_SIZE_160_1_SMOOTH: _ClassVar[StrandSize]
    STRAND_SIZE_160_1_1_8_SMOOTH: _ClassVar[StrandSize]
    STRAND_SIZE_160_1_1_4_SMOOTH: _ClassVar[StrandSize]
    STRAND_SIZE_160_1_3_8_SMOOTH: _ClassVar[StrandSize]
    STRAND_SIZE_157_5_8_DEF_BAR: _ClassVar[StrandSize]
    STRAND_SIZE_150_1_DEF_BAR: _ClassVar[StrandSize]
    STRAND_SIZE_160_1_DEF_BAR: _ClassVar[StrandSize]
    STRAND_SIZE_150_1_1_4_DEF_BAR: _ClassVar[StrandSize]
    STRAND_SIZE_160_1_1_4_DEF_BAR: _ClassVar[StrandSize]
    STRAND_SIZE_160_1_3_8_DEF_BAR: _ClassVar[StrandSize]
STRAND_TYPE_UNSPECIFIED: StrandType
STRAND_TYPE_GRADE_250_KSI_LOLAX: StrandType
STRAND_TYPE_GRADE_270_KSI_LOLAX: StrandType
STRAND_TYPE_GRADE_300_KSI_LOLAX: StrandType
STRAND_TYPE_SMOOTH_BARS_145_KSI: StrandType
STRAND_TYPE_SMOOTH_BARS_160_KSI: StrandType
STRAND_TYPE_DEFORMED_BARS_150_160_KSI: StrandType
STRAND_SIZE_UNSPECIFIED: StrandSize
STRAND_SIZE_250_5_16_3_WIRE: StrandSize
STRAND_SIZE_250_1_4_7_WIRE: StrandSize
STRAND_SIZE_250_5_16_7_WIRE: StrandSize
STRAND_SIZE_250_3_8_7_WIRE: StrandSize
STRAND_SIZE_250_7_16_7_WIRE: StrandSize
STRAND_SIZE_250_1_2_7_WIRE: StrandSize
STRAND_SIZE_250_06_7_WIRE: StrandSize
STRAND_SIZE_270_5_16_7_WIRE: StrandSize
STRAND_SIZE_270_3_8_7_WIRE: StrandSize
STRAND_SIZE_270_7_16_7_WIRE: StrandSize
STRAND_SIZE_270_1_2_7_WIRE: StrandSize
STRAND_SIZE_270_1_2_7_W_SPEC: StrandSize
STRAND_SIZE_270_9_16_7_WIRE: StrandSize
STRAND_SIZE_270_0_6_7_WIRE: StrandSize
STRAND_SIZE_270_0_7_7_WIRE: StrandSize
STRAND_SIZE_300_3_8_7_WIRE: StrandSize
STRAND_SIZE_300_7_16_7_WIRE: StrandSize
STRAND_SIZE_300_1_2_7_WIRE: StrandSize
STRAND_SIZE_300_1_2_SUPER: StrandSize
STRAND_SIZE_300_0_6_7_WIRE: StrandSize
STRAND_SIZE_145_3_4_SMOOTH: StrandSize
STRAND_SIZE_145_7_8_SMOOTH: StrandSize
STRAND_SIZE_145_1_SMOOTH: StrandSize
STRAND_SIZE_145_1_1_8_SMOOTH: StrandSize
STRAND_SIZE_145_1_1_4_SMOOTH: StrandSize
STRAND_SIZE_145_1_3_8_SMOOTH: StrandSize
STRAND_SIZE_160_3_4_SMOOTH: StrandSize
STRAND_SIZE_160_7_8_SMOOTH: StrandSize
STRAND_SIZE_160_1_SMOOTH: StrandSize
STRAND_SIZE_160_1_1_8_SMOOTH: StrandSize
STRAND_SIZE_160_1_1_4_SMOOTH: StrandSize
STRAND_SIZE_160_1_3_8_SMOOTH: StrandSize
STRAND_SIZE_157_5_8_DEF_BAR: StrandSize
STRAND_SIZE_150_1_DEF_BAR: StrandSize
STRAND_SIZE_160_1_DEF_BAR: StrandSize
STRAND_SIZE_150_1_1_4_DEF_BAR: StrandSize
STRAND_SIZE_160_1_1_4_DEF_BAR: StrandSize
STRAND_SIZE_160_1_3_8_DEF_BAR: StrandSize

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
    __slots__ = ("name", "strand_type", "strand_size", "pattern_type", "bundled_bars", "num_bundled")
    NAME_FIELD_NUMBER: _ClassVar[int]
    STRAND_TYPE_FIELD_NUMBER: _ClassVar[int]
    STRAND_SIZE_FIELD_NUMBER: _ClassVar[int]
    PATTERN_TYPE_FIELD_NUMBER: _ClassVar[int]
    BUNDLED_BARS_FIELD_NUMBER: _ClassVar[int]
    NUM_BUNDLED_FIELD_NUMBER: _ClassVar[int]
    name: str
    strand_type: StrandType
    strand_size: StrandSize
    pattern_type: _CommonReinforcementPattern_pb2.PatternType
    bundled_bars: bool
    num_bundled: int
    def __init__(self, name: _Optional[str] = ..., strand_type: _Optional[_Union[StrandType, str]] = ..., strand_size: _Optional[_Union[StrandSize, str]] = ..., pattern_type: _Optional[_Union[_CommonReinforcementPattern_pb2.PatternType, str]] = ..., bundled_bars: bool = ..., num_bundled: _Optional[int] = ...) -> None: ...
