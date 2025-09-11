from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class CrossSectionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    P2_UNSPECIFIED: _ClassVar[CrossSectionType]
    P2_CIRCULAR: _ClassVar[CrossSectionType]
    P2_RECTANGULAR: _ClassVar[CrossSectionType]
    P2_PIPE: _ClassVar[CrossSectionType]
    P2_CUSTOM: _ClassVar[CrossSectionType]
P2_UNSPECIFIED: CrossSectionType
P2_CIRCULAR: CrossSectionType
P2_RECTANGULAR: CrossSectionType
P2_PIPE: CrossSectionType
P2_CUSTOM: CrossSectionType
