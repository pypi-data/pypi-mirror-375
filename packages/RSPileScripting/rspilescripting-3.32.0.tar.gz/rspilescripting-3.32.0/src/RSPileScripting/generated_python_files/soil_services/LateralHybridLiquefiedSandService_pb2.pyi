from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetHybridLiquefiedSandRequest(_message.Message):
    __slots__ = ("session_id", "soil_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    soil_id: str
    def __init__(self, session_id: _Optional[str] = ..., soil_id: _Optional[str] = ...) -> None: ...

class GetHybridLiquefiedSandResponse(_message.Message):
    __slots__ = ("hybrid_liquefied_sand_props",)
    HYBRID_LIQUEFIED_SAND_PROPS_FIELD_NUMBER: _ClassVar[int]
    hybrid_liquefied_sand_props: HybridLiquefiedSandProperties
    def __init__(self, hybrid_liquefied_sand_props: _Optional[_Union[HybridLiquefiedSandProperties, _Mapping]] = ...) -> None: ...

class SetHybridLiquefiedSandRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "soil_id", "hybrid_liquefied_sand_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    HYBRID_LIQUEFIED_SAND_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    soil_id: str
    hybrid_liquefied_sand_props: HybridLiquefiedSandProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., soil_id: _Optional[str] = ..., hybrid_liquefied_sand_props: _Optional[_Union[HybridLiquefiedSandProperties, _Mapping]] = ...) -> None: ...

class SetHybridLiquefiedSandResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class HybridLiquefiedSandProperties(_message.Message):
    __slots__ = ("hybrid_lsand_use_spt", "undrained_shear_strength_HLS", "strain_factor_HLS", "spt_value_HLS")
    HYBRID_LSAND_USE_SPT_FIELD_NUMBER: _ClassVar[int]
    UNDRAINED_SHEAR_STRENGTH_HLS_FIELD_NUMBER: _ClassVar[int]
    STRAIN_FACTOR_HLS_FIELD_NUMBER: _ClassVar[int]
    SPT_VALUE_HLS_FIELD_NUMBER: _ClassVar[int]
    hybrid_lsand_use_spt: bool
    undrained_shear_strength_HLS: float
    strain_factor_HLS: float
    spt_value_HLS: float
    def __init__(self, hybrid_lsand_use_spt: bool = ..., undrained_shear_strength_HLS: _Optional[float] = ..., strain_factor_HLS: _Optional[float] = ..., spt_value_HLS: _Optional[float] = ...) -> None: ...
