from phenopackets.vrs.v1 import vrs_pb2 as _vrs_pb2
from phenopackets.schema.v2.core import base_pb2 as _base_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar, Iterable, Mapping, Optional, Union

DESCRIPTOR: _descriptor.FileDescriptor
genomic: MoleculeContext
protein: MoleculeContext
transcript: MoleculeContext
unspecified_molecule_context: MoleculeContext

class Expression(_message.Message):
    __slots__ = ["syntax", "value", "version"]
    SYNTAX_FIELD_NUMBER: ClassVar[int]
    VALUE_FIELD_NUMBER: ClassVar[int]
    VERSION_FIELD_NUMBER: ClassVar[int]
    syntax: str
    value: str
    version: str
    def __init__(self, syntax: Optional[str] = ..., value: Optional[str] = ..., version: Optional[str] = ...) -> None: ...

class Extension(_message.Message):
    __slots__ = ["name", "value"]
    NAME_FIELD_NUMBER: ClassVar[int]
    VALUE_FIELD_NUMBER: ClassVar[int]
    name: str
    value: str
    def __init__(self, name: Optional[str] = ..., value: Optional[str] = ...) -> None: ...

class GeneDescriptor(_message.Message):
    __slots__ = ["alternate_ids", "alternate_symbols", "description", "symbol", "value_id", "xrefs"]
    ALTERNATE_IDS_FIELD_NUMBER: ClassVar[int]
    ALTERNATE_SYMBOLS_FIELD_NUMBER: ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: ClassVar[int]
    SYMBOL_FIELD_NUMBER: ClassVar[int]
    VALUE_ID_FIELD_NUMBER: ClassVar[int]
    XREFS_FIELD_NUMBER: ClassVar[int]
    alternate_ids: _containers.RepeatedScalarFieldContainer[str]
    alternate_symbols: _containers.RepeatedScalarFieldContainer[str]
    description: str
    symbol: str
    value_id: str
    xrefs: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, value_id: Optional[str] = ..., symbol: Optional[str] = ..., description: Optional[str] = ..., alternate_ids: Optional[Iterable[str]] = ..., alternate_symbols: Optional[Iterable[str]] = ..., xrefs: Optional[Iterable[str]] = ...) -> None: ...

class VariationDescriptor(_message.Message):
    __slots__ = ["allelic_state", "alternate_labels", "description", "expressions", "extensions", "gene_context", "id", "label", "molecule_context", "structural_type", "variation", "vcf_record", "vrs_ref_allele_seq", "xrefs"]
    ALLELIC_STATE_FIELD_NUMBER: ClassVar[int]
    ALTERNATE_LABELS_FIELD_NUMBER: ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: ClassVar[int]
    EXPRESSIONS_FIELD_NUMBER: ClassVar[int]
    EXTENSIONS_FIELD_NUMBER: ClassVar[int]
    GENE_CONTEXT_FIELD_NUMBER: ClassVar[int]
    ID_FIELD_NUMBER: ClassVar[int]
    LABEL_FIELD_NUMBER: ClassVar[int]
    MOLECULE_CONTEXT_FIELD_NUMBER: ClassVar[int]
    STRUCTURAL_TYPE_FIELD_NUMBER: ClassVar[int]
    VARIATION_FIELD_NUMBER: ClassVar[int]
    VCF_RECORD_FIELD_NUMBER: ClassVar[int]
    VRS_REF_ALLELE_SEQ_FIELD_NUMBER: ClassVar[int]
    XREFS_FIELD_NUMBER: ClassVar[int]
    allelic_state: _base_pb2.OntologyClass
    alternate_labels: _containers.RepeatedScalarFieldContainer[str]
    description: str
    expressions: _containers.RepeatedCompositeFieldContainer[Expression]
    extensions: _containers.RepeatedCompositeFieldContainer[Extension]
    gene_context: GeneDescriptor
    id: str
    label: str
    molecule_context: MoleculeContext
    structural_type: _base_pb2.OntologyClass
    variation: _vrs_pb2.Variation
    vcf_record: VcfRecord
    vrs_ref_allele_seq: str
    xrefs: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, id: Optional[str] = ..., variation: Optional[Union[_vrs_pb2.Variation, Mapping]] = ..., label: Optional[str] = ..., description: Optional[str] = ..., gene_context: Optional[Union[GeneDescriptor, Mapping]] = ..., expressions: Optional[Iterable[Union[Expression, Mapping]]] = ..., vcf_record: Optional[Union[VcfRecord, Mapping]] = ..., xrefs: Optional[Iterable[str]] = ..., alternate_labels: Optional[Iterable[str]] = ..., extensions: Optional[Iterable[Union[Extension, Mapping]]] = ..., molecule_context: Optional[Union[MoleculeContext, str]] = ..., structural_type: Optional[Union[_base_pb2.OntologyClass, Mapping]] = ..., vrs_ref_allele_seq: Optional[str] = ..., allelic_state: Optional[Union[_base_pb2.OntologyClass, Mapping]] = ...) -> None: ...

class VcfRecord(_message.Message):
    __slots__ = ["alt", "chrom", "filter", "genome_assembly", "id", "info", "pos", "qual", "ref"]
    ALT_FIELD_NUMBER: ClassVar[int]
    CHROM_FIELD_NUMBER: ClassVar[int]
    FILTER_FIELD_NUMBER: ClassVar[int]
    GENOME_ASSEMBLY_FIELD_NUMBER: ClassVar[int]
    ID_FIELD_NUMBER: ClassVar[int]
    INFO_FIELD_NUMBER: ClassVar[int]
    POS_FIELD_NUMBER: ClassVar[int]
    QUAL_FIELD_NUMBER: ClassVar[int]
    REF_FIELD_NUMBER: ClassVar[int]
    alt: str
    chrom: str
    filter: str
    genome_assembly: str
    id: str
    info: str
    pos: int
    qual: str
    ref: str
    def __init__(self, genome_assembly: Optional[str] = ..., chrom: Optional[str] = ..., pos: Optional[int] = ..., id: Optional[str] = ..., ref: Optional[str] = ..., alt: Optional[str] = ..., qual: Optional[str] = ..., filter: Optional[str] = ..., info: Optional[str] = ...) -> None: ...

class MoleculeContext(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
