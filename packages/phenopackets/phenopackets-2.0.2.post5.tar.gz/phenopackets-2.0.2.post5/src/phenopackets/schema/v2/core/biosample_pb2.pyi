from phenopackets.schema.v2.core import base_pb2 as _base_pb2
from phenopackets.schema.v2.core import measurement_pb2 as _measurement_pb2
from phenopackets.schema.v2.core import phenotypic_feature_pb2 as _phenotypic_feature_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar, Iterable, Mapping, Optional, Union

DESCRIPTOR: _descriptor.FileDescriptor

class Biosample(_message.Message):
    __slots__ = ["derived_from_id", "description", "diagnostic_markers", "files", "histological_diagnosis", "id", "individual_id", "material_sample", "measurements", "pathological_stage", "pathological_tnm_finding", "phenotypic_features", "procedure", "sample_processing", "sample_storage", "sample_type", "sampled_tissue", "taxonomy", "time_of_collection", "tumor_grade", "tumor_progression"]
    DERIVED_FROM_ID_FIELD_NUMBER: ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: ClassVar[int]
    DIAGNOSTIC_MARKERS_FIELD_NUMBER: ClassVar[int]
    FILES_FIELD_NUMBER: ClassVar[int]
    HISTOLOGICAL_DIAGNOSIS_FIELD_NUMBER: ClassVar[int]
    ID_FIELD_NUMBER: ClassVar[int]
    INDIVIDUAL_ID_FIELD_NUMBER: ClassVar[int]
    MATERIAL_SAMPLE_FIELD_NUMBER: ClassVar[int]
    MEASUREMENTS_FIELD_NUMBER: ClassVar[int]
    PATHOLOGICAL_STAGE_FIELD_NUMBER: ClassVar[int]
    PATHOLOGICAL_TNM_FINDING_FIELD_NUMBER: ClassVar[int]
    PHENOTYPIC_FEATURES_FIELD_NUMBER: ClassVar[int]
    PROCEDURE_FIELD_NUMBER: ClassVar[int]
    SAMPLED_TISSUE_FIELD_NUMBER: ClassVar[int]
    SAMPLE_PROCESSING_FIELD_NUMBER: ClassVar[int]
    SAMPLE_STORAGE_FIELD_NUMBER: ClassVar[int]
    SAMPLE_TYPE_FIELD_NUMBER: ClassVar[int]
    TAXONOMY_FIELD_NUMBER: ClassVar[int]
    TIME_OF_COLLECTION_FIELD_NUMBER: ClassVar[int]
    TUMOR_GRADE_FIELD_NUMBER: ClassVar[int]
    TUMOR_PROGRESSION_FIELD_NUMBER: ClassVar[int]
    derived_from_id: str
    description: str
    diagnostic_markers: _containers.RepeatedCompositeFieldContainer[_base_pb2.OntologyClass]
    files: _containers.RepeatedCompositeFieldContainer[_base_pb2.File]
    histological_diagnosis: _base_pb2.OntologyClass
    id: str
    individual_id: str
    material_sample: _base_pb2.OntologyClass
    measurements: _containers.RepeatedCompositeFieldContainer[_measurement_pb2.Measurement]
    pathological_stage: _base_pb2.OntologyClass
    pathological_tnm_finding: _containers.RepeatedCompositeFieldContainer[_base_pb2.OntologyClass]
    phenotypic_features: _containers.RepeatedCompositeFieldContainer[_phenotypic_feature_pb2.PhenotypicFeature]
    procedure: _base_pb2.Procedure
    sample_processing: _base_pb2.OntologyClass
    sample_storage: _base_pb2.OntologyClass
    sample_type: _base_pb2.OntologyClass
    sampled_tissue: _base_pb2.OntologyClass
    taxonomy: _base_pb2.OntologyClass
    time_of_collection: _base_pb2.TimeElement
    tumor_grade: _base_pb2.OntologyClass
    tumor_progression: _base_pb2.OntologyClass
    def __init__(self, id: Optional[str] = ..., individual_id: Optional[str] = ..., derived_from_id: Optional[str] = ..., description: Optional[str] = ..., sampled_tissue: Optional[Union[_base_pb2.OntologyClass, Mapping]] = ..., sample_type: Optional[Union[_base_pb2.OntologyClass, Mapping]] = ..., phenotypic_features: Optional[Iterable[Union[_phenotypic_feature_pb2.PhenotypicFeature, Mapping]]] = ..., measurements: Optional[Iterable[Union[_measurement_pb2.Measurement, Mapping]]] = ..., taxonomy: Optional[Union[_base_pb2.OntologyClass, Mapping]] = ..., time_of_collection: Optional[Union[_base_pb2.TimeElement, Mapping]] = ..., histological_diagnosis: Optional[Union[_base_pb2.OntologyClass, Mapping]] = ..., tumor_progression: Optional[Union[_base_pb2.OntologyClass, Mapping]] = ..., tumor_grade: Optional[Union[_base_pb2.OntologyClass, Mapping]] = ..., pathological_stage: Optional[Union[_base_pb2.OntologyClass, Mapping]] = ..., pathological_tnm_finding: Optional[Iterable[Union[_base_pb2.OntologyClass, Mapping]]] = ..., diagnostic_markers: Optional[Iterable[Union[_base_pb2.OntologyClass, Mapping]]] = ..., procedure: Optional[Union[_base_pb2.Procedure, Mapping]] = ..., files: Optional[Iterable[Union[_base_pb2.File, Mapping]]] = ..., material_sample: Optional[Union[_base_pb2.OntologyClass, Mapping]] = ..., sample_processing: Optional[Union[_base_pb2.OntologyClass, Mapping]] = ..., sample_storage: Optional[Union[_base_pb2.OntologyClass, Mapping]] = ...) -> None: ...
