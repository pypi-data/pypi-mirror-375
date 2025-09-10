from phenopackets.schema.v2.core import base_pb2 as _base_pb2
from phenopackets.schema.v2.core import biosample_pb2 as _biosample_pb2
from phenopackets.schema.v2.core import disease_pb2 as _disease_pb2
from phenopackets.schema.v2.core import interpretation_pb2 as _interpretation_pb2
from phenopackets.schema.v2.core import individual_pb2 as _individual_pb2
from phenopackets.schema.v2.core import measurement_pb2 as _measurement_pb2
from phenopackets.schema.v2.core import medical_action_pb2 as _medical_action_pb2
from phenopackets.schema.v2.core import meta_data_pb2 as _meta_data_pb2
from phenopackets.schema.v2.core import pedigree_pb2 as _pedigree_pb2
from phenopackets.schema.v2.core import phenotypic_feature_pb2 as _phenotypic_feature_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar, Iterable, Mapping, Optional, Union

DESCRIPTOR: _descriptor.FileDescriptor

class Cohort(_message.Message):
    __slots__ = ["description", "files", "id", "members", "meta_data"]
    DESCRIPTION_FIELD_NUMBER: ClassVar[int]
    FILES_FIELD_NUMBER: ClassVar[int]
    ID_FIELD_NUMBER: ClassVar[int]
    MEMBERS_FIELD_NUMBER: ClassVar[int]
    META_DATA_FIELD_NUMBER: ClassVar[int]
    description: str
    files: _containers.RepeatedCompositeFieldContainer[_base_pb2.File]
    id: str
    members: _containers.RepeatedCompositeFieldContainer[Phenopacket]
    meta_data: _meta_data_pb2.MetaData
    def __init__(self, id: Optional[str] = ..., description: Optional[str] = ..., members: Optional[Iterable[Union[Phenopacket, Mapping]]] = ..., files: Optional[Iterable[Union[_base_pb2.File, Mapping]]] = ..., meta_data: Optional[Union[_meta_data_pb2.MetaData, Mapping]] = ...) -> None: ...

class Family(_message.Message):
    __slots__ = ["consanguinous_parents", "files", "id", "meta_data", "pedigree", "proband", "relatives"]
    CONSANGUINOUS_PARENTS_FIELD_NUMBER: ClassVar[int]
    FILES_FIELD_NUMBER: ClassVar[int]
    ID_FIELD_NUMBER: ClassVar[int]
    META_DATA_FIELD_NUMBER: ClassVar[int]
    PEDIGREE_FIELD_NUMBER: ClassVar[int]
    PROBAND_FIELD_NUMBER: ClassVar[int]
    RELATIVES_FIELD_NUMBER: ClassVar[int]
    consanguinous_parents: bool
    files: _containers.RepeatedCompositeFieldContainer[_base_pb2.File]
    id: str
    meta_data: _meta_data_pb2.MetaData
    pedigree: _pedigree_pb2.Pedigree
    proband: Phenopacket
    relatives: _containers.RepeatedCompositeFieldContainer[Phenopacket]
    def __init__(self, id: Optional[str] = ..., proband: Optional[Union[Phenopacket, Mapping]] = ..., relatives: Optional[Iterable[Union[Phenopacket, Mapping]]] = ..., consanguinous_parents: bool = ..., pedigree: Optional[Union[_pedigree_pb2.Pedigree, Mapping]] = ..., files: Optional[Iterable[Union[_base_pb2.File, Mapping]]] = ..., meta_data: Optional[Union[_meta_data_pb2.MetaData, Mapping]] = ...) -> None: ...

class Phenopacket(_message.Message):
    __slots__ = ["biosamples", "diseases", "files", "id", "interpretations", "measurements", "medical_actions", "meta_data", "phenotypic_features", "subject"]
    BIOSAMPLES_FIELD_NUMBER: ClassVar[int]
    DISEASES_FIELD_NUMBER: ClassVar[int]
    FILES_FIELD_NUMBER: ClassVar[int]
    ID_FIELD_NUMBER: ClassVar[int]
    INTERPRETATIONS_FIELD_NUMBER: ClassVar[int]
    MEASUREMENTS_FIELD_NUMBER: ClassVar[int]
    MEDICAL_ACTIONS_FIELD_NUMBER: ClassVar[int]
    META_DATA_FIELD_NUMBER: ClassVar[int]
    PHENOTYPIC_FEATURES_FIELD_NUMBER: ClassVar[int]
    SUBJECT_FIELD_NUMBER: ClassVar[int]
    biosamples: _containers.RepeatedCompositeFieldContainer[_biosample_pb2.Biosample]
    diseases: _containers.RepeatedCompositeFieldContainer[_disease_pb2.Disease]
    files: _containers.RepeatedCompositeFieldContainer[_base_pb2.File]
    id: str
    interpretations: _containers.RepeatedCompositeFieldContainer[_interpretation_pb2.Interpretation]
    measurements: _containers.RepeatedCompositeFieldContainer[_measurement_pb2.Measurement]
    medical_actions: _containers.RepeatedCompositeFieldContainer[_medical_action_pb2.MedicalAction]
    meta_data: _meta_data_pb2.MetaData
    phenotypic_features: _containers.RepeatedCompositeFieldContainer[_phenotypic_feature_pb2.PhenotypicFeature]
    subject: _individual_pb2.Individual
    def __init__(self, id: Optional[str] = ..., subject: Optional[Union[_individual_pb2.Individual, Mapping]] = ..., phenotypic_features: Optional[Iterable[Union[_phenotypic_feature_pb2.PhenotypicFeature, Mapping]]] = ..., measurements: Optional[Iterable[Union[_measurement_pb2.Measurement, Mapping]]] = ..., biosamples: Optional[Iterable[Union[_biosample_pb2.Biosample, Mapping]]] = ..., interpretations: Optional[Iterable[Union[_interpretation_pb2.Interpretation, Mapping]]] = ..., diseases: Optional[Iterable[Union[_disease_pb2.Disease, Mapping]]] = ..., medical_actions: Optional[Iterable[Union[_medical_action_pb2.MedicalAction, Mapping]]] = ..., files: Optional[Iterable[Union[_base_pb2.File, Mapping]]] = ..., meta_data: Optional[Union[_meta_data_pb2.MetaData, Mapping]] = ...) -> None: ...
