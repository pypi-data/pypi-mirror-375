from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetRolledSectionUserSelectedAreaPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ...) -> None: ...

class GetRolledSectionUserSelectedAreaPropertiesResponse(_message.Message):
    __slots__ = ("rolled_section_user_selected_area_props",)
    ROLLED_SECTION_USER_SELECTED_AREA_PROPS_FIELD_NUMBER: _ClassVar[int]
    rolled_section_user_selected_area_props: RolledSectionUserSelectedAreaProperties
    def __init__(self, rolled_section_user_selected_area_props: _Optional[_Union[RolledSectionUserSelectedAreaProperties, _Mapping]] = ...) -> None: ...

class SetRolledSectionUserSelectedAreaPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_id", "rolled_section_user_selected_area_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    ROLLED_SECTION_USER_SELECTED_AREA_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_id: str
    rolled_section_user_selected_area_props: RolledSectionUserSelectedAreaProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_id: _Optional[str] = ..., rolled_section_user_selected_area_props: _Optional[_Union[RolledSectionUserSelectedAreaProperties, _Mapping]] = ...) -> None: ...

class SetRolledSectionUserSelectedAreaPropertiesResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class RolledSectionUserSelectedAreaProperties(_message.Message):
    __slots__ = ("rolled_section_area_user_select",)
    ROLLED_SECTION_AREA_USER_SELECT_FIELD_NUMBER: _ClassVar[int]
    rolled_section_area_user_select: float
    def __init__(self, rolled_section_area_user_select: _Optional[float] = ...) -> None: ...
