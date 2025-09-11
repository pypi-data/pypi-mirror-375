from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetVectorPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "pile_type_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_TYPE_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    pile_type_id: str
    def __init__(self, session_id: _Optional[str] = ..., pile_type_id: _Optional[str] = ...) -> None: ...

class GetVectorPropertiesResponse(_message.Message):
    __slots__ = ("vector_props",)
    VECTOR_PROPS_FIELD_NUMBER: _ClassVar[int]
    vector_props: VectorProperties
    def __init__(self, vector_props: _Optional[_Union[VectorProperties, _Mapping]] = ...) -> None: ...

class SetVectorPropertiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_type_id", "vector_props")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_TYPE_ID_FIELD_NUMBER: _ClassVar[int]
    VECTOR_PROPS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_type_id: str
    vector_props: VectorProperties
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_type_id: _Optional[str] = ..., vector_props: _Optional[_Union[VectorProperties, _Mapping]] = ...) -> None: ...

class SetVectorPropertiesResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class VectorProperties(_message.Message):
    __slots__ = ("vector",)
    VECTOR_FIELD_NUMBER: _ClassVar[int]
    vector: Vector3D
    def __init__(self, vector: _Optional[_Union[Vector3D, _Mapping]] = ...) -> None: ...

class Vector3D(_message.Message):
    __slots__ = ("x", "y", "z")
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    Z_FIELD_NUMBER: _ClassVar[int]
    x: float
    y: float
    z: float
    def __init__(self, x: _Optional[float] = ..., y: _Optional[float] = ..., z: _Optional[float] = ...) -> None: ...
