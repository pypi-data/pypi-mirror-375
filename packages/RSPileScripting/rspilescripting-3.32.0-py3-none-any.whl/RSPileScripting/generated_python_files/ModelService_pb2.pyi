from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetNumberOfActiveSoilPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ...) -> None: ...

class GetNumberOfActiveSoilPropertiesResponse(_message.Message):
    __slots__ = ("number_of_soil_props",)
    NUMBER_OF_SOIL_PROPS_FIELD_NUMBER: _ClassVar[int]
    number_of_soil_props: int
    def __init__(self, number_of_soil_props: _Optional[int] = ...) -> None: ...

class GetSoilPropertyRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "soil_index")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    SOIL_INDEX_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    soil_index: int
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., soil_index: _Optional[int] = ...) -> None: ...

class GetSoilPropertyResponse(_message.Message):
    __slots__ = ("soil_id",)
    SOIL_ID_FIELD_NUMBER: _ClassVar[int]
    soil_id: str
    def __init__(self, soil_id: _Optional[str] = ...) -> None: ...

class GetNumberOfActivePilePropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ...) -> None: ...

class GetNumberOfActivePilePropertiesResponse(_message.Message):
    __slots__ = ("number_of_pile_props",)
    NUMBER_OF_PILE_PROPS_FIELD_NUMBER: _ClassVar[int]
    number_of_pile_props: int
    def __init__(self, number_of_pile_props: _Optional[int] = ...) -> None: ...

class GetPilePropertyRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_index")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_INDEX_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_index: int
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_index: _Optional[int] = ...) -> None: ...

class GetPilePropertyResponse(_message.Message):
    __slots__ = ("pile_id",)
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    pile_id: str
    def __init__(self, pile_id: _Optional[str] = ...) -> None: ...

class GetNumberOfActivePileTypesRequest(_message.Message):
    __slots__ = ("session_id", "model_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ...) -> None: ...

class GetNumberOfActivePileTypesResponse(_message.Message):
    __slots__ = ("number_of_pile_types",)
    NUMBER_OF_PILE_TYPES_FIELD_NUMBER: _ClassVar[int]
    number_of_pile_types: int
    def __init__(self, number_of_pile_types: _Optional[int] = ...) -> None: ...

class GetPileTypeRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_type_index")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_TYPE_INDEX_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_type_index: int
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_type_index: _Optional[int] = ...) -> None: ...

class GetPileTypeResponse(_message.Message):
    __slots__ = ("pile_type_id",)
    PILE_TYPE_ID_FIELD_NUMBER: _ClassVar[int]
    pile_type_id: str
    def __init__(self, pile_type_id: _Optional[str] = ...) -> None: ...

class ComputeRequest(_message.Message):
    __slots__ = ("session_id", "model_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ...) -> None: ...

class ComputeResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetPileResultsTablesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "var_list")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    VAR_LIST_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    var_list: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., var_list: _Optional[_Iterable[str]] = ...) -> None: ...

class GetPileResultsTablesResponse(_message.Message):
    __slots__ = ("tables", "enum_to_header")
    class EnumToHeaderEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    TABLES_FIELD_NUMBER: _ClassVar[int]
    ENUM_TO_HEADER_FIELD_NUMBER: _ClassVar[int]
    tables: _containers.RepeatedCompositeFieldContainer[Table]
    enum_to_header: _containers.ScalarMap[str, str]
    def __init__(self, tables: _Optional[_Iterable[_Union[Table, _Mapping]]] = ..., enum_to_header: _Optional[_Mapping[str, str]] = ...) -> None: ...

class SaveRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "file_name")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    FILE_NAME_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    file_name: str
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., file_name: _Optional[str] = ...) -> None: ...

class SaveResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CloseRequest(_message.Message):
    __slots__ = ("session_id", "model_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ...) -> None: ...

class CloseResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Table(_message.Message):
    __slots__ = ("pile_id", "rows")
    PILE_ID_FIELD_NUMBER: _ClassVar[int]
    ROWS_FIELD_NUMBER: _ClassVar[int]
    pile_id: str
    rows: _containers.RepeatedCompositeFieldContainer[Row]
    def __init__(self, pile_id: _Optional[str] = ..., rows: _Optional[_Iterable[_Union[Row, _Mapping]]] = ...) -> None: ...

class Row(_message.Message):
    __slots__ = ("data",)
    class DataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: float
        def __init__(self, key: _Optional[str] = ..., value: _Optional[float] = ...) -> None: ...
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: _containers.ScalarMap[str, float]
    def __init__(self, data: _Optional[_Mapping[str, float]] = ...) -> None: ...
