from google.protobuf import timestamp_pb2 as _timestamp_pb2
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

class Age(_message.Message):
    __slots__ = ["age"]
    AGE_FIELD_NUMBER: ClassVar[int]
    age: str
    def __init__(self, age: Optional[str] = ...) -> None: ...

class AgeRange(_message.Message):
    __slots__ = ["end", "start"]
    END_FIELD_NUMBER: ClassVar[int]
    START_FIELD_NUMBER: ClassVar[int]
    end: Age
    start: Age
    def __init__(self, start: Optional[Union[Age, Mapping]] = ..., end: Optional[Union[Age, Mapping]] = ...) -> None: ...

class Biosample(_message.Message):
    __slots__ = ["age_of_individual_at_collection", "age_range_of_individual_at_collection", "description", "diagnostic_markers", "histological_diagnosis", "hts_files", "id", "individual_id", "is_control_sample", "phenotypic_features", "procedure", "sampled_tissue", "taxonomy", "tumor_grade", "tumor_progression", "variants"]
    AGE_OF_INDIVIDUAL_AT_COLLECTION_FIELD_NUMBER: ClassVar[int]
    AGE_RANGE_OF_INDIVIDUAL_AT_COLLECTION_FIELD_NUMBER: ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: ClassVar[int]
    DIAGNOSTIC_MARKERS_FIELD_NUMBER: ClassVar[int]
    HISTOLOGICAL_DIAGNOSIS_FIELD_NUMBER: ClassVar[int]
    HTS_FILES_FIELD_NUMBER: ClassVar[int]
    ID_FIELD_NUMBER: ClassVar[int]
    INDIVIDUAL_ID_FIELD_NUMBER: ClassVar[int]
    IS_CONTROL_SAMPLE_FIELD_NUMBER: ClassVar[int]
    PHENOTYPIC_FEATURES_FIELD_NUMBER: ClassVar[int]
    PROCEDURE_FIELD_NUMBER: ClassVar[int]
    SAMPLED_TISSUE_FIELD_NUMBER: ClassVar[int]
    TAXONOMY_FIELD_NUMBER: ClassVar[int]
    TUMOR_GRADE_FIELD_NUMBER: ClassVar[int]
    TUMOR_PROGRESSION_FIELD_NUMBER: ClassVar[int]
    VARIANTS_FIELD_NUMBER: ClassVar[int]
    age_of_individual_at_collection: Age
    age_range_of_individual_at_collection: AgeRange
    description: str
    diagnostic_markers: _containers.RepeatedCompositeFieldContainer[OntologyClass]
    histological_diagnosis: OntologyClass
    hts_files: _containers.RepeatedCompositeFieldContainer[HtsFile]
    id: str
    individual_id: str
    is_control_sample: bool
    phenotypic_features: _containers.RepeatedCompositeFieldContainer[PhenotypicFeature]
    procedure: Procedure
    sampled_tissue: OntologyClass
    taxonomy: OntologyClass
    tumor_grade: OntologyClass
    tumor_progression: OntologyClass
    variants: _containers.RepeatedCompositeFieldContainer[Variant]
    def __init__(self, id: Optional[str] = ..., individual_id: Optional[str] = ..., description: Optional[str] = ..., sampled_tissue: Optional[Union[OntologyClass, Mapping]] = ..., phenotypic_features: Optional[Iterable[Union[PhenotypicFeature, Mapping]]] = ..., taxonomy: Optional[Union[OntologyClass, Mapping]] = ..., age_of_individual_at_collection: Optional[Union[Age, Mapping]] = ..., age_range_of_individual_at_collection: Optional[Union[AgeRange, Mapping]] = ..., histological_diagnosis: Optional[Union[OntologyClass, Mapping]] = ..., tumor_progression: Optional[Union[OntologyClass, Mapping]] = ..., tumor_grade: Optional[Union[OntologyClass, Mapping]] = ..., diagnostic_markers: Optional[Iterable[Union[OntologyClass, Mapping]]] = ..., procedure: Optional[Union[Procedure, Mapping]] = ..., hts_files: Optional[Iterable[Union[HtsFile, Mapping]]] = ..., variants: Optional[Iterable[Union[Variant, Mapping]]] = ..., is_control_sample: bool = ...) -> None: ...

class Disease(_message.Message):
    __slots__ = ["age_of_onset", "age_range_of_onset", "class_of_onset", "disease_stage", "term", "tnm_finding"]
    AGE_OF_ONSET_FIELD_NUMBER: ClassVar[int]
    AGE_RANGE_OF_ONSET_FIELD_NUMBER: ClassVar[int]
    CLASS_OF_ONSET_FIELD_NUMBER: ClassVar[int]
    DISEASE_STAGE_FIELD_NUMBER: ClassVar[int]
    TERM_FIELD_NUMBER: ClassVar[int]
    TNM_FINDING_FIELD_NUMBER: ClassVar[int]
    age_of_onset: Age
    age_range_of_onset: AgeRange
    class_of_onset: OntologyClass
    disease_stage: _containers.RepeatedCompositeFieldContainer[OntologyClass]
    term: OntologyClass
    tnm_finding: _containers.RepeatedCompositeFieldContainer[OntologyClass]
    def __init__(self, term: Optional[Union[OntologyClass, Mapping]] = ..., age_of_onset: Optional[Union[Age, Mapping]] = ..., age_range_of_onset: Optional[Union[AgeRange, Mapping]] = ..., class_of_onset: Optional[Union[OntologyClass, Mapping]] = ..., disease_stage: Optional[Iterable[Union[OntologyClass, Mapping]]] = ..., tnm_finding: Optional[Iterable[Union[OntologyClass, Mapping]]] = ...) -> None: ...

class Evidence(_message.Message):
    __slots__ = ["evidence_code", "reference"]
    EVIDENCE_CODE_FIELD_NUMBER: ClassVar[int]
    REFERENCE_FIELD_NUMBER: ClassVar[int]
    evidence_code: OntologyClass
    reference: ExternalReference
    def __init__(self, evidence_code: Optional[Union[OntologyClass, Mapping]] = ..., reference: Optional[Union[ExternalReference, Mapping]] = ...) -> None: ...

class ExternalReference(_message.Message):
    __slots__ = ["description", "id"]
    DESCRIPTION_FIELD_NUMBER: ClassVar[int]
    ID_FIELD_NUMBER: ClassVar[int]
    description: str
    id: str
    def __init__(self, id: Optional[str] = ..., description: Optional[str] = ...) -> None: ...

class Gene(_message.Message):
    __slots__ = ["alternate_ids", "id", "symbol"]
    ALTERNATE_IDS_FIELD_NUMBER: ClassVar[int]
    ID_FIELD_NUMBER: ClassVar[int]
    SYMBOL_FIELD_NUMBER: ClassVar[int]
    alternate_ids: _containers.RepeatedScalarFieldContainer[str]
    id: str
    symbol: str
    def __init__(self, id: Optional[str] = ..., alternate_ids: Optional[Iterable[str]] = ..., symbol: Optional[str] = ...) -> None: ...

class HgvsAllele(_message.Message):
    __slots__ = ["hgvs", "id"]
    HGVS_FIELD_NUMBER: ClassVar[int]
    ID_FIELD_NUMBER: ClassVar[int]
    hgvs: str
    id: str
    def __init__(self, id: Optional[str] = ..., hgvs: Optional[str] = ...) -> None: ...

class HtsFile(_message.Message):
    __slots__ = ["description", "genome_assembly", "hts_format", "individual_to_sample_identifiers", "uri"]
    class HtsFormat(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
    class IndividualToSampleIdentifiersEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: ClassVar[int]
        VALUE_FIELD_NUMBER: ClassVar[int]
        key: str
        value: str
        def __init__(self, key: Optional[str] = ..., value: Optional[str] = ...) -> None: ...
    BAM: HtsFile.HtsFormat
    BCF: HtsFile.HtsFormat
    CRAM: HtsFile.HtsFormat
    DESCRIPTION_FIELD_NUMBER: ClassVar[int]
    FASTQ: HtsFile.HtsFormat
    GENOME_ASSEMBLY_FIELD_NUMBER: ClassVar[int]
    GVCF: HtsFile.HtsFormat
    HTS_FORMAT_FIELD_NUMBER: ClassVar[int]
    INDIVIDUAL_TO_SAMPLE_IDENTIFIERS_FIELD_NUMBER: ClassVar[int]
    SAM: HtsFile.HtsFormat
    UNKNOWN: HtsFile.HtsFormat
    URI_FIELD_NUMBER: ClassVar[int]
    VCF: HtsFile.HtsFormat
    description: str
    genome_assembly: str
    hts_format: HtsFile.HtsFormat
    individual_to_sample_identifiers: _containers.ScalarMap[str, str]
    uri: str
    def __init__(self, uri: Optional[str] = ..., description: Optional[str] = ..., hts_format: Optional[Union[HtsFile.HtsFormat, str]] = ..., genome_assembly: Optional[str] = ..., individual_to_sample_identifiers: Optional[Mapping[str, str]] = ...) -> None: ...

class Individual(_message.Message):
    __slots__ = ["age_at_collection", "age_range_at_collection", "alternate_ids", "date_of_birth", "id", "karyotypic_sex", "sex", "taxonomy"]
    AGE_AT_COLLECTION_FIELD_NUMBER: ClassVar[int]
    AGE_RANGE_AT_COLLECTION_FIELD_NUMBER: ClassVar[int]
    ALTERNATE_IDS_FIELD_NUMBER: ClassVar[int]
    DATE_OF_BIRTH_FIELD_NUMBER: ClassVar[int]
    ID_FIELD_NUMBER: ClassVar[int]
    KARYOTYPIC_SEX_FIELD_NUMBER: ClassVar[int]
    SEX_FIELD_NUMBER: ClassVar[int]
    TAXONOMY_FIELD_NUMBER: ClassVar[int]
    age_at_collection: Age
    age_range_at_collection: AgeRange
    alternate_ids: _containers.RepeatedScalarFieldContainer[str]
    date_of_birth: _timestamp_pb2.Timestamp
    id: str
    karyotypic_sex: KaryotypicSex
    sex: Sex
    taxonomy: OntologyClass
    def __init__(self, id: Optional[str] = ..., alternate_ids: Optional[Iterable[str]] = ..., date_of_birth: Optional[Union[_timestamp_pb2.Timestamp, Mapping]] = ..., age_at_collection: Optional[Union[Age, Mapping]] = ..., age_range_at_collection: Optional[Union[AgeRange, Mapping]] = ..., sex: Optional[Union[Sex, str]] = ..., karyotypic_sex: Optional[Union[KaryotypicSex, str]] = ..., taxonomy: Optional[Union[OntologyClass, Mapping]] = ...) -> None: ...

class IscnAllele(_message.Message):
    __slots__ = ["id", "iscn"]
    ID_FIELD_NUMBER: ClassVar[int]
    ISCN_FIELD_NUMBER: ClassVar[int]
    id: str
    iscn: str
    def __init__(self, id: Optional[str] = ..., iscn: Optional[str] = ...) -> None: ...

class MetaData(_message.Message):
    __slots__ = ["created", "created_by", "external_references", "phenopacket_schema_version", "resources", "submitted_by", "updates"]
    CREATED_BY_FIELD_NUMBER: ClassVar[int]
    CREATED_FIELD_NUMBER: ClassVar[int]
    EXTERNAL_REFERENCES_FIELD_NUMBER: ClassVar[int]
    PHENOPACKET_SCHEMA_VERSION_FIELD_NUMBER: ClassVar[int]
    RESOURCES_FIELD_NUMBER: ClassVar[int]
    SUBMITTED_BY_FIELD_NUMBER: ClassVar[int]
    UPDATES_FIELD_NUMBER: ClassVar[int]
    created: _timestamp_pb2.Timestamp
    created_by: str
    external_references: _containers.RepeatedCompositeFieldContainer[ExternalReference]
    phenopacket_schema_version: str
    resources: _containers.RepeatedCompositeFieldContainer[Resource]
    submitted_by: str
    updates: _containers.RepeatedCompositeFieldContainer[Update]
    def __init__(self, created: Optional[Union[_timestamp_pb2.Timestamp, Mapping]] = ..., created_by: Optional[str] = ..., submitted_by: Optional[str] = ..., resources: Optional[Iterable[Union[Resource, Mapping]]] = ..., updates: Optional[Iterable[Union[Update, Mapping]]] = ..., phenopacket_schema_version: Optional[str] = ..., external_references: Optional[Iterable[Union[ExternalReference, Mapping]]] = ...) -> None: ...

class OntologyClass(_message.Message):
    __slots__ = ["id", "label"]
    ID_FIELD_NUMBER: ClassVar[int]
    LABEL_FIELD_NUMBER: ClassVar[int]
    id: str
    label: str
    def __init__(self, id: Optional[str] = ..., label: Optional[str] = ...) -> None: ...

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
        sex: Sex
        def __init__(self, family_id: Optional[str] = ..., individual_id: Optional[str] = ..., paternal_id: Optional[str] = ..., maternal_id: Optional[str] = ..., sex: Optional[Union[Sex, str]] = ..., affected_status: Optional[Union[Pedigree.Person.AffectedStatus, str]] = ...) -> None: ...
    PERSONS_FIELD_NUMBER: ClassVar[int]
    persons: _containers.RepeatedCompositeFieldContainer[Pedigree.Person]
    def __init__(self, persons: Optional[Iterable[Union[Pedigree.Person, Mapping]]] = ...) -> None: ...

class PhenotypicFeature(_message.Message):
    __slots__ = ["age_of_onset", "age_range_of_onset", "class_of_onset", "description", "evidence", "modifiers", "negated", "severity", "type"]
    AGE_OF_ONSET_FIELD_NUMBER: ClassVar[int]
    AGE_RANGE_OF_ONSET_FIELD_NUMBER: ClassVar[int]
    CLASS_OF_ONSET_FIELD_NUMBER: ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: ClassVar[int]
    EVIDENCE_FIELD_NUMBER: ClassVar[int]
    MODIFIERS_FIELD_NUMBER: ClassVar[int]
    NEGATED_FIELD_NUMBER: ClassVar[int]
    SEVERITY_FIELD_NUMBER: ClassVar[int]
    TYPE_FIELD_NUMBER: ClassVar[int]
    age_of_onset: Age
    age_range_of_onset: AgeRange
    class_of_onset: OntologyClass
    description: str
    evidence: _containers.RepeatedCompositeFieldContainer[Evidence]
    modifiers: _containers.RepeatedCompositeFieldContainer[OntologyClass]
    negated: bool
    severity: OntologyClass
    type: OntologyClass
    def __init__(self, description: Optional[str] = ..., type: Optional[Union[OntologyClass, Mapping]] = ..., negated: bool = ..., severity: Optional[Union[OntologyClass, Mapping]] = ..., modifiers: Optional[Iterable[Union[OntologyClass, Mapping]]] = ..., age_of_onset: Optional[Union[Age, Mapping]] = ..., age_range_of_onset: Optional[Union[AgeRange, Mapping]] = ..., class_of_onset: Optional[Union[OntologyClass, Mapping]] = ..., evidence: Optional[Iterable[Union[Evidence, Mapping]]] = ...) -> None: ...

class Procedure(_message.Message):
    __slots__ = ["body_site", "code"]
    BODY_SITE_FIELD_NUMBER: ClassVar[int]
    CODE_FIELD_NUMBER: ClassVar[int]
    body_site: OntologyClass
    code: OntologyClass
    def __init__(self, code: Optional[Union[OntologyClass, Mapping]] = ..., body_site: Optional[Union[OntologyClass, Mapping]] = ...) -> None: ...

class Resource(_message.Message):
    __slots__ = ["id", "iri_prefix", "name", "namespace_prefix", "url", "version"]
    ID_FIELD_NUMBER: ClassVar[int]
    IRI_PREFIX_FIELD_NUMBER: ClassVar[int]
    NAMESPACE_PREFIX_FIELD_NUMBER: ClassVar[int]
    NAME_FIELD_NUMBER: ClassVar[int]
    URL_FIELD_NUMBER: ClassVar[int]
    VERSION_FIELD_NUMBER: ClassVar[int]
    id: str
    iri_prefix: str
    name: str
    namespace_prefix: str
    url: str
    version: str
    def __init__(self, id: Optional[str] = ..., name: Optional[str] = ..., url: Optional[str] = ..., version: Optional[str] = ..., namespace_prefix: Optional[str] = ..., iri_prefix: Optional[str] = ...) -> None: ...

class SpdiAllele(_message.Message):
    __slots__ = ["deleted_sequence", "id", "inserted_sequence", "position", "seq_id"]
    DELETED_SEQUENCE_FIELD_NUMBER: ClassVar[int]
    ID_FIELD_NUMBER: ClassVar[int]
    INSERTED_SEQUENCE_FIELD_NUMBER: ClassVar[int]
    POSITION_FIELD_NUMBER: ClassVar[int]
    SEQ_ID_FIELD_NUMBER: ClassVar[int]
    deleted_sequence: str
    id: str
    inserted_sequence: str
    position: int
    seq_id: str
    def __init__(self, id: Optional[str] = ..., seq_id: Optional[str] = ..., position: Optional[int] = ..., deleted_sequence: Optional[str] = ..., inserted_sequence: Optional[str] = ...) -> None: ...

class Update(_message.Message):
    __slots__ = ["comment", "timestamp", "updated_by"]
    COMMENT_FIELD_NUMBER: ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: ClassVar[int]
    UPDATED_BY_FIELD_NUMBER: ClassVar[int]
    comment: str
    timestamp: _timestamp_pb2.Timestamp
    updated_by: str
    def __init__(self, timestamp: Optional[Union[_timestamp_pb2.Timestamp, Mapping]] = ..., updated_by: Optional[str] = ..., comment: Optional[str] = ...) -> None: ...

class Variant(_message.Message):
    __slots__ = ["hgvs_allele", "iscn_allele", "spdi_allele", "vcf_allele", "zygosity"]
    HGVS_ALLELE_FIELD_NUMBER: ClassVar[int]
    ISCN_ALLELE_FIELD_NUMBER: ClassVar[int]
    SPDI_ALLELE_FIELD_NUMBER: ClassVar[int]
    VCF_ALLELE_FIELD_NUMBER: ClassVar[int]
    ZYGOSITY_FIELD_NUMBER: ClassVar[int]
    hgvs_allele: HgvsAllele
    iscn_allele: IscnAllele
    spdi_allele: SpdiAllele
    vcf_allele: VcfAllele
    zygosity: OntologyClass
    def __init__(self, hgvs_allele: Optional[Union[HgvsAllele, Mapping]] = ..., vcf_allele: Optional[Union[VcfAllele, Mapping]] = ..., spdi_allele: Optional[Union[SpdiAllele, Mapping]] = ..., iscn_allele: Optional[Union[IscnAllele, Mapping]] = ..., zygosity: Optional[Union[OntologyClass, Mapping]] = ...) -> None: ...

class VcfAllele(_message.Message):
    __slots__ = ["alt", "chr", "genome_assembly", "id", "info", "pos", "ref", "vcf_version"]
    ALT_FIELD_NUMBER: ClassVar[int]
    CHR_FIELD_NUMBER: ClassVar[int]
    GENOME_ASSEMBLY_FIELD_NUMBER: ClassVar[int]
    ID_FIELD_NUMBER: ClassVar[int]
    INFO_FIELD_NUMBER: ClassVar[int]
    POS_FIELD_NUMBER: ClassVar[int]
    REF_FIELD_NUMBER: ClassVar[int]
    VCF_VERSION_FIELD_NUMBER: ClassVar[int]
    alt: str
    chr: str
    genome_assembly: str
    id: str
    info: str
    pos: int
    ref: str
    vcf_version: str
    def __init__(self, vcf_version: Optional[str] = ..., genome_assembly: Optional[str] = ..., id: Optional[str] = ..., chr: Optional[str] = ..., pos: Optional[int] = ..., ref: Optional[str] = ..., alt: Optional[str] = ..., info: Optional[str] = ...) -> None: ...

class Sex(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class KaryotypicSex(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
