from phenopackets.schema.v2.core import base_pb2 as _base_pb2
from phenopackets.vrsatile.v1 import vrsatile_pb2 as _vrsatile_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar, Iterable, Mapping, Optional, Union

ACTIONABLE: TherapeuticActionability
BENIGN: AcmgPathogenicityClassification
DESCRIPTOR: _descriptor.FileDescriptor
LIKELY_BENIGN: AcmgPathogenicityClassification
LIKELY_PATHOGENIC: AcmgPathogenicityClassification
NOT_ACTIONABLE: TherapeuticActionability
NOT_PROVIDED: AcmgPathogenicityClassification
PATHOGENIC: AcmgPathogenicityClassification
UNCERTAIN_SIGNIFICANCE: AcmgPathogenicityClassification
UNKNOWN_ACTIONABILITY: TherapeuticActionability

class Diagnosis(_message.Message):
    __slots__ = ["disease", "genomic_interpretations"]
    DISEASE_FIELD_NUMBER: ClassVar[int]
    GENOMIC_INTERPRETATIONS_FIELD_NUMBER: ClassVar[int]
    disease: _base_pb2.OntologyClass
    genomic_interpretations: _containers.RepeatedCompositeFieldContainer[GenomicInterpretation]
    def __init__(self, disease: Optional[Union[_base_pb2.OntologyClass, Mapping]] = ..., genomic_interpretations: Optional[Iterable[Union[GenomicInterpretation, Mapping]]] = ...) -> None: ...

class GenomicInterpretation(_message.Message):
    __slots__ = ["gene", "interpretation_status", "subject_or_biosample_id", "variant_interpretation"]
    class InterpretationStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
    CANDIDATE: GenomicInterpretation.InterpretationStatus
    CAUSATIVE: GenomicInterpretation.InterpretationStatus
    CONTRIBUTORY: GenomicInterpretation.InterpretationStatus
    GENE_FIELD_NUMBER: ClassVar[int]
    INTERPRETATION_STATUS_FIELD_NUMBER: ClassVar[int]
    REJECTED: GenomicInterpretation.InterpretationStatus
    SUBJECT_OR_BIOSAMPLE_ID_FIELD_NUMBER: ClassVar[int]
    UNKNOWN_STATUS: GenomicInterpretation.InterpretationStatus
    VARIANT_INTERPRETATION_FIELD_NUMBER: ClassVar[int]
    gene: _vrsatile_pb2.GeneDescriptor
    interpretation_status: GenomicInterpretation.InterpretationStatus
    subject_or_biosample_id: str
    variant_interpretation: VariantInterpretation
    def __init__(self, subject_or_biosample_id: Optional[str] = ..., interpretation_status: Optional[Union[GenomicInterpretation.InterpretationStatus, str]] = ..., gene: Optional[Union[_vrsatile_pb2.GeneDescriptor, Mapping]] = ..., variant_interpretation: Optional[Union[VariantInterpretation, Mapping]] = ...) -> None: ...

class Interpretation(_message.Message):
    __slots__ = ["diagnosis", "id", "progress_status", "summary"]
    class ProgressStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
    COMPLETED: Interpretation.ProgressStatus
    DIAGNOSIS_FIELD_NUMBER: ClassVar[int]
    ID_FIELD_NUMBER: ClassVar[int]
    IN_PROGRESS: Interpretation.ProgressStatus
    PROGRESS_STATUS_FIELD_NUMBER: ClassVar[int]
    SOLVED: Interpretation.ProgressStatus
    SUMMARY_FIELD_NUMBER: ClassVar[int]
    UNKNOWN_PROGRESS: Interpretation.ProgressStatus
    UNSOLVED: Interpretation.ProgressStatus
    diagnosis: Diagnosis
    id: str
    progress_status: Interpretation.ProgressStatus
    summary: str
    def __init__(self, id: Optional[str] = ..., progress_status: Optional[Union[Interpretation.ProgressStatus, str]] = ..., diagnosis: Optional[Union[Diagnosis, Mapping]] = ..., summary: Optional[str] = ...) -> None: ...

class VariantInterpretation(_message.Message):
    __slots__ = ["acmg_pathogenicity_classification", "therapeutic_actionability", "variation_descriptor"]
    ACMG_PATHOGENICITY_CLASSIFICATION_FIELD_NUMBER: ClassVar[int]
    THERAPEUTIC_ACTIONABILITY_FIELD_NUMBER: ClassVar[int]
    VARIATION_DESCRIPTOR_FIELD_NUMBER: ClassVar[int]
    acmg_pathogenicity_classification: AcmgPathogenicityClassification
    therapeutic_actionability: TherapeuticActionability
    variation_descriptor: _vrsatile_pb2.VariationDescriptor
    def __init__(self, acmg_pathogenicity_classification: Optional[Union[AcmgPathogenicityClassification, str]] = ..., therapeutic_actionability: Optional[Union[TherapeuticActionability, str]] = ..., variation_descriptor: Optional[Union[_vrsatile_pb2.VariationDescriptor, Mapping]] = ...) -> None: ...

class AcmgPathogenicityClassification(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class TherapeuticActionability(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
