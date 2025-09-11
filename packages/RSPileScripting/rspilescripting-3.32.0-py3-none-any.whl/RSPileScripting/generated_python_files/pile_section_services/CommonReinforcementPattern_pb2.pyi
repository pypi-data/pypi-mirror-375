from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class PatternType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PATTERN_TYPE_UNSPECIFIED: _ClassVar[PatternType]
    RPATTERN_RADIAL: _ClassVar[PatternType]
    RPATTERN_RECTANGULAR: _ClassVar[PatternType]
    RPATTERN_CUSTOM: _ClassVar[PatternType]
PATTERN_TYPE_UNSPECIFIED: PatternType
RPATTERN_RADIAL: PatternType
RPATTERN_RECTANGULAR: PatternType
RPATTERN_CUSTOM: PatternType
