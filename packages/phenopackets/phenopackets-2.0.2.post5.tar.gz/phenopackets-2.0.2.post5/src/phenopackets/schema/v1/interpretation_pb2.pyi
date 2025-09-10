from phenopackets.schema.v1 import base_pb2 as _base_pb2
from phenopackets.schema.v1 import phenopackets_pb2 as _phenopackets_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar, Iterable, Mapping, Optional, Union

DESCRIPTOR: _descriptor.FileDescriptor

class Diagnosis(_message.Message):
    __slots__ = ["disease", "genomic_interpretations"]
    DISEASE_FIELD_NUMBER: ClassVar[int]
    GENOMIC_INTERPRETATIONS_FIELD_NUMBER: ClassVar[int]
    disease: _base_pb2.Disease
    genomic_interpretations: _containers.RepeatedCompositeFieldContainer[GenomicInterpretation]
    def __init__(self, disease: Optional[Union[_base_pb2.Disease, Mapping]] = ..., genomic_interpretations: Optional[Iterable[Union[GenomicInterpretation, Mapping]]] = ...) -> None: ...

class GenomicInterpretation(_message.Message):
    __slots__ = ["gene", "status", "variant"]
    class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
    CANDIDATE: GenomicInterpretation.Status
    CAUSATIVE: GenomicInterpretation.Status
    GENE_FIELD_NUMBER: ClassVar[int]
    REJECTED: GenomicInterpretation.Status
    STATUS_FIELD_NUMBER: ClassVar[int]
    UNKNOWN: GenomicInterpretation.Status
    VARIANT_FIELD_NUMBER: ClassVar[int]
    gene: _base_pb2.Gene
    status: GenomicInterpretation.Status
    variant: _base_pb2.Variant
    def __init__(self, status: Optional[Union[GenomicInterpretation.Status, str]] = ..., gene: Optional[Union[_base_pb2.Gene, Mapping]] = ..., variant: Optional[Union[_base_pb2.Variant, Mapping]] = ...) -> None: ...

class Interpretation(_message.Message):
    __slots__ = ["diagnosis", "family", "id", "meta_data", "phenopacket", "resolution_status"]
    class ResolutionStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
    DIAGNOSIS_FIELD_NUMBER: ClassVar[int]
    FAMILY_FIELD_NUMBER: ClassVar[int]
    ID_FIELD_NUMBER: ClassVar[int]
    IN_PROGRESS: Interpretation.ResolutionStatus
    META_DATA_FIELD_NUMBER: ClassVar[int]
    PHENOPACKET_FIELD_NUMBER: ClassVar[int]
    RESOLUTION_STATUS_FIELD_NUMBER: ClassVar[int]
    SOLVED: Interpretation.ResolutionStatus
    UNKNOWN: Interpretation.ResolutionStatus
    UNSOLVED: Interpretation.ResolutionStatus
    diagnosis: _containers.RepeatedCompositeFieldContainer[Diagnosis]
    family: _phenopackets_pb2.Family
    id: str
    meta_data: _base_pb2.MetaData
    phenopacket: _phenopackets_pb2.Phenopacket
    resolution_status: Interpretation.ResolutionStatus
    def __init__(self, id: Optional[str] = ..., resolution_status: Optional[Union[Interpretation.ResolutionStatus, str]] = ..., phenopacket: Optional[Union[_phenopackets_pb2.Phenopacket, Mapping]] = ..., family: Optional[Union[_phenopackets_pb2.Family, Mapping]] = ..., diagnosis: Optional[Iterable[Union[Diagnosis, Mapping]]] = ..., meta_data: Optional[Union[_base_pb2.MetaData, Mapping]] = ...) -> None: ...
