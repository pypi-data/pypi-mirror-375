from phenopackets.schema.v1 import base_pb2 as _base_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar, Iterable, Mapping, Optional, Union

DESCRIPTOR: _descriptor.FileDescriptor

class Cohort(_message.Message):
    __slots__ = ["description", "hts_files", "id", "members", "meta_data"]
    DESCRIPTION_FIELD_NUMBER: ClassVar[int]
    HTS_FILES_FIELD_NUMBER: ClassVar[int]
    ID_FIELD_NUMBER: ClassVar[int]
    MEMBERS_FIELD_NUMBER: ClassVar[int]
    META_DATA_FIELD_NUMBER: ClassVar[int]
    description: str
    hts_files: _containers.RepeatedCompositeFieldContainer[_base_pb2.HtsFile]
    id: str
    members: _containers.RepeatedCompositeFieldContainer[Phenopacket]
    meta_data: _base_pb2.MetaData
    def __init__(self, id: Optional[str] = ..., description: Optional[str] = ..., members: Optional[Iterable[Union[Phenopacket, Mapping]]] = ..., hts_files: Optional[Iterable[Union[_base_pb2.HtsFile, Mapping]]] = ..., meta_data: Optional[Union[_base_pb2.MetaData, Mapping]] = ...) -> None: ...

class Family(_message.Message):
    __slots__ = ["hts_files", "id", "meta_data", "pedigree", "proband", "relatives"]
    HTS_FILES_FIELD_NUMBER: ClassVar[int]
    ID_FIELD_NUMBER: ClassVar[int]
    META_DATA_FIELD_NUMBER: ClassVar[int]
    PEDIGREE_FIELD_NUMBER: ClassVar[int]
    PROBAND_FIELD_NUMBER: ClassVar[int]
    RELATIVES_FIELD_NUMBER: ClassVar[int]
    hts_files: _containers.RepeatedCompositeFieldContainer[_base_pb2.HtsFile]
    id: str
    meta_data: _base_pb2.MetaData
    pedigree: _base_pb2.Pedigree
    proband: Phenopacket
    relatives: _containers.RepeatedCompositeFieldContainer[Phenopacket]
    def __init__(self, id: Optional[str] = ..., proband: Optional[Union[Phenopacket, Mapping]] = ..., relatives: Optional[Iterable[Union[Phenopacket, Mapping]]] = ..., pedigree: Optional[Union[_base_pb2.Pedigree, Mapping]] = ..., hts_files: Optional[Iterable[Union[_base_pb2.HtsFile, Mapping]]] = ..., meta_data: Optional[Union[_base_pb2.MetaData, Mapping]] = ...) -> None: ...

class Phenopacket(_message.Message):
    __slots__ = ["biosamples", "diseases", "genes", "hts_files", "id", "meta_data", "phenotypic_features", "subject", "variants"]
    BIOSAMPLES_FIELD_NUMBER: ClassVar[int]
    DISEASES_FIELD_NUMBER: ClassVar[int]
    GENES_FIELD_NUMBER: ClassVar[int]
    HTS_FILES_FIELD_NUMBER: ClassVar[int]
    ID_FIELD_NUMBER: ClassVar[int]
    META_DATA_FIELD_NUMBER: ClassVar[int]
    PHENOTYPIC_FEATURES_FIELD_NUMBER: ClassVar[int]
    SUBJECT_FIELD_NUMBER: ClassVar[int]
    VARIANTS_FIELD_NUMBER: ClassVar[int]
    biosamples: _containers.RepeatedCompositeFieldContainer[_base_pb2.Biosample]
    diseases: _containers.RepeatedCompositeFieldContainer[_base_pb2.Disease]
    genes: _containers.RepeatedCompositeFieldContainer[_base_pb2.Gene]
    hts_files: _containers.RepeatedCompositeFieldContainer[_base_pb2.HtsFile]
    id: str
    meta_data: _base_pb2.MetaData
    phenotypic_features: _containers.RepeatedCompositeFieldContainer[_base_pb2.PhenotypicFeature]
    subject: _base_pb2.Individual
    variants: _containers.RepeatedCompositeFieldContainer[_base_pb2.Variant]
    def __init__(self, id: Optional[str] = ..., subject: Optional[Union[_base_pb2.Individual, Mapping]] = ..., phenotypic_features: Optional[Iterable[Union[_base_pb2.PhenotypicFeature, Mapping]]] = ..., biosamples: Optional[Iterable[Union[_base_pb2.Biosample, Mapping]]] = ..., genes: Optional[Iterable[Union[_base_pb2.Gene, Mapping]]] = ..., variants: Optional[Iterable[Union[_base_pb2.Variant, Mapping]]] = ..., diseases: Optional[Iterable[Union[_base_pb2.Disease, Mapping]]] = ..., hts_files: Optional[Iterable[Union[_base_pb2.HtsFile, Mapping]]] = ..., meta_data: Optional[Union[_base_pb2.MetaData, Mapping]] = ...) -> None: ...
