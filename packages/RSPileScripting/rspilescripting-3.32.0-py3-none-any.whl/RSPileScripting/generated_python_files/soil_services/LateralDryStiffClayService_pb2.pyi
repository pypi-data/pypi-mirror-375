from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetDryStiffClayRequest(_message.Message):
    __slots__ = ("session_id", "soil_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    soil_id: str
    def __init__(self, session_id: _Optional[str] = ..., soil_id: _Optional[str] = ...) -> None: ...

class GetDryStiffClayResponse(_message.Message):
    __slots__ = ("dry_stiff_clay_props",)
    DRY_STIFF_CLAY_PROPS_FIELD_NUMBER: _ClassVar[int]
    dry_stiff_clay_props: DryStiffClayProperties
    def __init__(self, dry_stiff_clay_props: _Optional[_Union[DryStiffClayProperties, _Mapping]] = ...) -> None: ...

class SetDryStiffClayRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "soil_id", "dry_stiff_clay_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    DRY_STIFF_CLAY_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    soil_id: str
    dry_stiff_clay_props: DryStiffClayProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., soil_id: _Optional[str] = ..., dry_stiff_clay_props: _Optional[_Union[DryStiffClayProperties, _Mapping]] = ...) -> None: ...

class SetDryStiffClayResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DryStiffClayProperties(_message.Message):
    __slots__ = ("shear_strength_DSC", "strain_factor_DSC")
    SHEAR_STRENGTH_DSC_FIELD_NUMBER: _ClassVar[int]
    STRAIN_FACTOR_DSC_FIELD_NUMBER: _ClassVar[int]
    shear_strength_DSC: float
    strain_factor_DSC: float
    def __init__(self, shear_strength_DSC: _Optional[float] = ..., strain_factor_DSC: _Optional[float] = ...) -> None: ...
