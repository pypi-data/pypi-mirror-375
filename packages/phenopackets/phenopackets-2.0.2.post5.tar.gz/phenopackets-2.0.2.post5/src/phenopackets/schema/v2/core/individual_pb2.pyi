from google.protobuf import timestamp_pb2 as _timestamp_pb2
from phenopackets.schema.v2.core import base_pb2 as _base_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar, Iterable, Mapping, Optional, Union

DESCRIPTOR: _descriptor.FileDescriptor
FEMALE: Sex
MALE: Sex
OTHER_KARYOTYPE: KaryotypicSex
OTHER_SEX: Sex
UNKNOWN_KARYOTYPE: KaryotypicSex
UNKNOWN_SEX: Sex
XO: KaryotypicSex
XX: KaryotypicSex
XXX: KaryotypicSex
XXXX: KaryotypicSex
XXXY: KaryotypicSex
XXY: KaryotypicSex
XXYY: KaryotypicSex
XY: KaryotypicSex
XYY: KaryotypicSex

class Individual(_message.Message):
    __slots__ = ["alternate_ids", "date_of_birth", "gender", "id", "karyotypic_sex", "sex", "taxonomy", "time_at_last_encounter", "vital_status"]
    ALTERNATE_IDS_FIELD_NUMBER: ClassVar[int]
    DATE_OF_BIRTH_FIELD_NUMBER: ClassVar[int]
    GENDER_FIELD_NUMBER: ClassVar[int]
    ID_FIELD_NUMBER: ClassVar[int]
    KARYOTYPIC_SEX_FIELD_NUMBER: ClassVar[int]
    SEX_FIELD_NUMBER: ClassVar[int]
    TAXONOMY_FIELD_NUMBER: ClassVar[int]
    TIME_AT_LAST_ENCOUNTER_FIELD_NUMBER: ClassVar[int]
    VITAL_STATUS_FIELD_NUMBER: ClassVar[int]
    alternate_ids: _containers.RepeatedScalarFieldContainer[str]
    date_of_birth: _timestamp_pb2.Timestamp
    gender: _base_pb2.OntologyClass
    id: str
    karyotypic_sex: KaryotypicSex
    sex: Sex
    taxonomy: _base_pb2.OntologyClass
    time_at_last_encounter: _base_pb2.TimeElement
    vital_status: VitalStatus
    def __init__(self, id: Optional[str] = ..., alternate_ids: Optional[Iterable[str]] = ..., date_of_birth: Optional[Union[_timestamp_pb2.Timestamp, Mapping]] = ..., time_at_last_encounter: Optional[Union[_base_pb2.TimeElement, Mapping]] = ..., vital_status: Optional[Union[VitalStatus, Mapping]] = ..., sex: Optional[Union[Sex, str]] = ..., karyotypic_sex: Optional[Union[KaryotypicSex, str]] = ..., gender: Optional[Union[_base_pb2.OntologyClass, Mapping]] = ..., taxonomy: Optional[Union[_base_pb2.OntologyClass, Mapping]] = ...) -> None: ...

class VitalStatus(_message.Message):
    __slots__ = ["cause_of_death", "status", "survival_time_in_days", "time_of_death"]
    class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
    ALIVE: VitalStatus.Status
    CAUSE_OF_DEATH_FIELD_NUMBER: ClassVar[int]
    DECEASED: VitalStatus.Status
    STATUS_FIELD_NUMBER: ClassVar[int]
    SURVIVAL_TIME_IN_DAYS_FIELD_NUMBER: ClassVar[int]
    TIME_OF_DEATH_FIELD_NUMBER: ClassVar[int]
    UNKNOWN_STATUS: VitalStatus.Status
    cause_of_death: _base_pb2.OntologyClass
    status: VitalStatus.Status
    survival_time_in_days: int
    time_of_death: _base_pb2.TimeElement
    def __init__(self, status: Optional[Union[VitalStatus.Status, str]] = ..., time_of_death: Optional[Union[_base_pb2.TimeElement, Mapping]] = ..., cause_of_death: Optional[Union[_base_pb2.OntologyClass, Mapping]] = ..., survival_time_in_days: Optional[int] = ...) -> None: ...

class Sex(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class KaryotypicSex(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
