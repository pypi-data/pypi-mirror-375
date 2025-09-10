from phenopackets.schema.v2.core import individual_pb2 as _individual_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar, Iterable, Mapping, Optional, Union

DESCRIPTOR: _descriptor.FileDescriptor

class Pedigree(_message.Message):
    __slots__ = ["persons"]
    class Person(_message.Message):
        __slots__ = ["affected_status", "family_id", "individual_id", "maternal_id", "paternal_id", "sex"]
        class AffectedStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = []
        AFFECTED: Pedigree.Person.AffectedStatus
        AFFECTED_STATUS_FIELD_NUMBER: ClassVar[int]
        FAMILY_ID_FIELD_NUMBER: ClassVar[int]
        INDIVIDUAL_ID_FIELD_NUMBER: ClassVar[int]
        MATERNAL_ID_FIELD_NUMBER: ClassVar[int]
        MISSING: Pedigree.Person.AffectedStatus
        PATERNAL_ID_FIELD_NUMBER: ClassVar[int]
        SEX_FIELD_NUMBER: ClassVar[int]
        UNAFFECTED: Pedigree.Person.AffectedStatus
        affected_status: Pedigree.Person.AffectedStatus
        family_id: str
        individual_id: str
        maternal_id: str
        paternal_id: str
        sex: _individual_pb2.Sex
        def __init__(self, family_id: Optional[str] = ..., individual_id: Optional[str] = ..., paternal_id: Optional[str] = ..., maternal_id: Optional[str] = ..., sex: Optional[Union[_individual_pb2.Sex, str]] = ..., affected_status: Optional[Union[Pedigree.Person.AffectedStatus, str]] = ...) -> None: ...
    PERSONS_FIELD_NUMBER: ClassVar[int]
    persons: _containers.RepeatedCompositeFieldContainer[Pedigree.Person]
    def __init__(self, persons: Optional[Iterable[Union[Pedigree.Person, Mapping]]] = ...) -> None: ...
