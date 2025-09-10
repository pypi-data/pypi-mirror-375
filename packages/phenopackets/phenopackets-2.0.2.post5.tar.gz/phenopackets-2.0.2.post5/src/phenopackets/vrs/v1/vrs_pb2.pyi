from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar, Iterable, Mapping, Optional, Union

DESCRIPTOR: _descriptor.FileDescriptor

class Abundance(_message.Message):
    __slots__ = ["copy_number"]
    COPY_NUMBER_FIELD_NUMBER: ClassVar[int]
    copy_number: CopyNumber
    def __init__(self, copy_number: Optional[Union[CopyNumber, Mapping]] = ...) -> None: ...

class Allele(_message.Message):
    __slots__ = ["_id", "chromosome_location", "curie", "derived_sequence_expression", "literal_sequence_expression", "repeated_sequence_expression", "sequence_location", "sequence_state"]
    CHROMOSOME_LOCATION_FIELD_NUMBER: ClassVar[int]
    CURIE_FIELD_NUMBER: ClassVar[int]
    DERIVED_SEQUENCE_EXPRESSION_FIELD_NUMBER: ClassVar[int]
    LITERAL_SEQUENCE_EXPRESSION_FIELD_NUMBER: ClassVar[int]
    REPEATED_SEQUENCE_EXPRESSION_FIELD_NUMBER: ClassVar[int]
    SEQUENCE_LOCATION_FIELD_NUMBER: ClassVar[int]
    SEQUENCE_STATE_FIELD_NUMBER: ClassVar[int]
    _ID_FIELD_NUMBER: ClassVar[int]
    _id: str
    chromosome_location: ChromosomeLocation
    curie: str
    derived_sequence_expression: DerivedSequenceExpression
    literal_sequence_expression: LiteralSequenceExpression
    repeated_sequence_expression: RepeatedSequenceExpression
    sequence_location: SequenceLocation
    sequence_state: SequenceState
    def __init__(self, _id: Optional[str] = ..., curie: Optional[str] = ..., chromosome_location: Optional[Union[ChromosomeLocation, Mapping]] = ..., sequence_location: Optional[Union[SequenceLocation, Mapping]] = ..., sequence_state: Optional[Union[SequenceState, Mapping]] = ..., literal_sequence_expression: Optional[Union[LiteralSequenceExpression, Mapping]] = ..., derived_sequence_expression: Optional[Union[DerivedSequenceExpression, Mapping]] = ..., repeated_sequence_expression: Optional[Union[RepeatedSequenceExpression, Mapping]] = ...) -> None: ...

class ChromosomeLocation(_message.Message):
    __slots__ = ["_id", "chr", "interval", "species_id"]
    CHR_FIELD_NUMBER: ClassVar[int]
    INTERVAL_FIELD_NUMBER: ClassVar[int]
    SPECIES_ID_FIELD_NUMBER: ClassVar[int]
    _ID_FIELD_NUMBER: ClassVar[int]
    _id: str
    chr: str
    interval: CytobandInterval
    species_id: str
    def __init__(self, _id: Optional[str] = ..., species_id: Optional[str] = ..., chr: Optional[str] = ..., interval: Optional[Union[CytobandInterval, Mapping]] = ...) -> None: ...

class CopyNumber(_message.Message):
    __slots__ = ["_id", "allele", "curie", "definite_range", "derived_sequence_expression", "gene", "haplotype", "indefinite_range", "literal_sequence_expression", "number", "repeated_sequence_expression"]
    ALLELE_FIELD_NUMBER: ClassVar[int]
    CURIE_FIELD_NUMBER: ClassVar[int]
    DEFINITE_RANGE_FIELD_NUMBER: ClassVar[int]
    DERIVED_SEQUENCE_EXPRESSION_FIELD_NUMBER: ClassVar[int]
    GENE_FIELD_NUMBER: ClassVar[int]
    HAPLOTYPE_FIELD_NUMBER: ClassVar[int]
    INDEFINITE_RANGE_FIELD_NUMBER: ClassVar[int]
    LITERAL_SEQUENCE_EXPRESSION_FIELD_NUMBER: ClassVar[int]
    NUMBER_FIELD_NUMBER: ClassVar[int]
    REPEATED_SEQUENCE_EXPRESSION_FIELD_NUMBER: ClassVar[int]
    _ID_FIELD_NUMBER: ClassVar[int]
    _id: str
    allele: Allele
    curie: str
    definite_range: DefiniteRange
    derived_sequence_expression: DerivedSequenceExpression
    gene: Gene
    haplotype: Haplotype
    indefinite_range: IndefiniteRange
    literal_sequence_expression: LiteralSequenceExpression
    number: Number
    repeated_sequence_expression: RepeatedSequenceExpression
    def __init__(self, _id: Optional[str] = ..., allele: Optional[Union[Allele, Mapping]] = ..., haplotype: Optional[Union[Haplotype, Mapping]] = ..., gene: Optional[Union[Gene, Mapping]] = ..., literal_sequence_expression: Optional[Union[LiteralSequenceExpression, Mapping]] = ..., derived_sequence_expression: Optional[Union[DerivedSequenceExpression, Mapping]] = ..., repeated_sequence_expression: Optional[Union[RepeatedSequenceExpression, Mapping]] = ..., curie: Optional[str] = ..., number: Optional[Union[Number, Mapping]] = ..., indefinite_range: Optional[Union[IndefiniteRange, Mapping]] = ..., definite_range: Optional[Union[DefiniteRange, Mapping]] = ...) -> None: ...

class CytobandInterval(_message.Message):
    __slots__ = ["end", "start"]
    END_FIELD_NUMBER: ClassVar[int]
    START_FIELD_NUMBER: ClassVar[int]
    end: str
    start: str
    def __init__(self, start: Optional[str] = ..., end: Optional[str] = ...) -> None: ...

class DefiniteRange(_message.Message):
    __slots__ = ["max", "min"]
    MAX_FIELD_NUMBER: ClassVar[int]
    MIN_FIELD_NUMBER: ClassVar[int]
    max: int
    min: int
    def __init__(self, min: Optional[int] = ..., max: Optional[int] = ...) -> None: ...

class DerivedSequenceExpression(_message.Message):
    __slots__ = ["location", "reverse_complement"]
    LOCATION_FIELD_NUMBER: ClassVar[int]
    REVERSE_COMPLEMENT_FIELD_NUMBER: ClassVar[int]
    location: SequenceLocation
    reverse_complement: bool
    def __init__(self, location: Optional[Union[SequenceLocation, Mapping]] = ..., reverse_complement: bool = ...) -> None: ...

class Feature(_message.Message):
    __slots__ = ["gene"]
    GENE_FIELD_NUMBER: ClassVar[int]
    gene: Gene
    def __init__(self, gene: Optional[Union[Gene, Mapping]] = ...) -> None: ...

class Gene(_message.Message):
    __slots__ = ["gene_id"]
    GENE_ID_FIELD_NUMBER: ClassVar[int]
    gene_id: str
    def __init__(self, gene_id: Optional[str] = ...) -> None: ...

class Haplotype(_message.Message):
    __slots__ = ["_id", "members"]
    class Member(_message.Message):
        __slots__ = ["allele", "curie"]
        ALLELE_FIELD_NUMBER: ClassVar[int]
        CURIE_FIELD_NUMBER: ClassVar[int]
        allele: Allele
        curie: str
        def __init__(self, allele: Optional[Union[Allele, Mapping]] = ..., curie: Optional[str] = ...) -> None: ...
    MEMBERS_FIELD_NUMBER: ClassVar[int]
    _ID_FIELD_NUMBER: ClassVar[int]
    _id: str
    members: _containers.RepeatedCompositeFieldContainer[Haplotype.Member]
    def __init__(self, _id: Optional[str] = ..., members: Optional[Iterable[Union[Haplotype.Member, Mapping]]] = ...) -> None: ...

class IndefiniteRange(_message.Message):
    __slots__ = ["comparator", "value"]
    COMPARATOR_FIELD_NUMBER: ClassVar[int]
    VALUE_FIELD_NUMBER: ClassVar[int]
    comparator: str
    value: int
    def __init__(self, value: Optional[int] = ..., comparator: Optional[str] = ...) -> None: ...

class LiteralSequenceExpression(_message.Message):
    __slots__ = ["sequence"]
    SEQUENCE_FIELD_NUMBER: ClassVar[int]
    sequence: str
    def __init__(self, sequence: Optional[str] = ...) -> None: ...

class Location(_message.Message):
    __slots__ = ["chromosome_location", "sequence_location"]
    CHROMOSOME_LOCATION_FIELD_NUMBER: ClassVar[int]
    SEQUENCE_LOCATION_FIELD_NUMBER: ClassVar[int]
    chromosome_location: ChromosomeLocation
    sequence_location: SequenceLocation
    def __init__(self, chromosome_location: Optional[Union[ChromosomeLocation, Mapping]] = ..., sequence_location: Optional[Union[SequenceLocation, Mapping]] = ...) -> None: ...

class MolecularVariation(_message.Message):
    __slots__ = ["allele", "haplotype"]
    ALLELE_FIELD_NUMBER: ClassVar[int]
    HAPLOTYPE_FIELD_NUMBER: ClassVar[int]
    allele: Allele
    haplotype: Haplotype
    def __init__(self, allele: Optional[Union[Allele, Mapping]] = ..., haplotype: Optional[Union[Haplotype, Mapping]] = ...) -> None: ...

class Number(_message.Message):
    __slots__ = ["value"]
    VALUE_FIELD_NUMBER: ClassVar[int]
    value: int
    def __init__(self, value: Optional[int] = ...) -> None: ...

class RepeatedSequenceExpression(_message.Message):
    __slots__ = ["definite_range", "derived_sequence_expression", "indefinite_range", "literal_sequence_expression", "number"]
    DEFINITE_RANGE_FIELD_NUMBER: ClassVar[int]
    DERIVED_SEQUENCE_EXPRESSION_FIELD_NUMBER: ClassVar[int]
    INDEFINITE_RANGE_FIELD_NUMBER: ClassVar[int]
    LITERAL_SEQUENCE_EXPRESSION_FIELD_NUMBER: ClassVar[int]
    NUMBER_FIELD_NUMBER: ClassVar[int]
    definite_range: DefiniteRange
    derived_sequence_expression: DerivedSequenceExpression
    indefinite_range: IndefiniteRange
    literal_sequence_expression: LiteralSequenceExpression
    number: Number
    def __init__(self, literal_sequence_expression: Optional[Union[LiteralSequenceExpression, Mapping]] = ..., derived_sequence_expression: Optional[Union[DerivedSequenceExpression, Mapping]] = ..., number: Optional[Union[Number, Mapping]] = ..., indefinite_range: Optional[Union[IndefiniteRange, Mapping]] = ..., definite_range: Optional[Union[DefiniteRange, Mapping]] = ...) -> None: ...

class SequenceExpression(_message.Message):
    __slots__ = ["derived_sequence_expression", "literal_sequence_expression", "repeated_sequence_expression"]
    DERIVED_SEQUENCE_EXPRESSION_FIELD_NUMBER: ClassVar[int]
    LITERAL_SEQUENCE_EXPRESSION_FIELD_NUMBER: ClassVar[int]
    REPEATED_SEQUENCE_EXPRESSION_FIELD_NUMBER: ClassVar[int]
    derived_sequence_expression: DerivedSequenceExpression
    literal_sequence_expression: LiteralSequenceExpression
    repeated_sequence_expression: RepeatedSequenceExpression
    def __init__(self, literal_sequence_expression: Optional[Union[LiteralSequenceExpression, Mapping]] = ..., derived_sequence_expression: Optional[Union[DerivedSequenceExpression, Mapping]] = ..., repeated_sequence_expression: Optional[Union[RepeatedSequenceExpression, Mapping]] = ...) -> None: ...

class SequenceInterval(_message.Message):
    __slots__ = ["end_definite_range", "end_indefinite_range", "end_number", "start_definite_range", "start_indefinite_range", "start_number"]
    END_DEFINITE_RANGE_FIELD_NUMBER: ClassVar[int]
    END_INDEFINITE_RANGE_FIELD_NUMBER: ClassVar[int]
    END_NUMBER_FIELD_NUMBER: ClassVar[int]
    START_DEFINITE_RANGE_FIELD_NUMBER: ClassVar[int]
    START_INDEFINITE_RANGE_FIELD_NUMBER: ClassVar[int]
    START_NUMBER_FIELD_NUMBER: ClassVar[int]
    end_definite_range: DefiniteRange
    end_indefinite_range: IndefiniteRange
    end_number: Number
    start_definite_range: DefiniteRange
    start_indefinite_range: IndefiniteRange
    start_number: Number
    def __init__(self, start_number: Optional[Union[Number, Mapping]] = ..., start_indefinite_range: Optional[Union[IndefiniteRange, Mapping]] = ..., start_definite_range: Optional[Union[DefiniteRange, Mapping]] = ..., end_number: Optional[Union[Number, Mapping]] = ..., end_indefinite_range: Optional[Union[IndefiniteRange, Mapping]] = ..., end_definite_range: Optional[Union[DefiniteRange, Mapping]] = ...) -> None: ...

class SequenceLocation(_message.Message):
    __slots__ = ["_id", "sequence_id", "sequence_interval", "simple_interval"]
    SEQUENCE_ID_FIELD_NUMBER: ClassVar[int]
    SEQUENCE_INTERVAL_FIELD_NUMBER: ClassVar[int]
    SIMPLE_INTERVAL_FIELD_NUMBER: ClassVar[int]
    _ID_FIELD_NUMBER: ClassVar[int]
    _id: str
    sequence_id: str
    sequence_interval: SequenceInterval
    simple_interval: SimpleInterval
    def __init__(self, _id: Optional[str] = ..., sequence_id: Optional[str] = ..., sequence_interval: Optional[Union[SequenceInterval, Mapping]] = ..., simple_interval: Optional[Union[SimpleInterval, Mapping]] = ...) -> None: ...

class SequenceState(_message.Message):
    __slots__ = ["sequence"]
    SEQUENCE_FIELD_NUMBER: ClassVar[int]
    sequence: str
    def __init__(self, sequence: Optional[str] = ...) -> None: ...

class SimpleInterval(_message.Message):
    __slots__ = ["end", "start"]
    END_FIELD_NUMBER: ClassVar[int]
    START_FIELD_NUMBER: ClassVar[int]
    end: int
    start: int
    def __init__(self, start: Optional[int] = ..., end: Optional[int] = ...) -> None: ...

class SystemicVariation(_message.Message):
    __slots__ = ["copy_number"]
    COPY_NUMBER_FIELD_NUMBER: ClassVar[int]
    copy_number: CopyNumber
    def __init__(self, copy_number: Optional[Union[CopyNumber, Mapping]] = ...) -> None: ...

class Text(_message.Message):
    __slots__ = ["_id", "definition"]
    DEFINITION_FIELD_NUMBER: ClassVar[int]
    _ID_FIELD_NUMBER: ClassVar[int]
    _id: str
    definition: str
    def __init__(self, _id: Optional[str] = ..., definition: Optional[str] = ...) -> None: ...

class UtilityVariation(_message.Message):
    __slots__ = ["text", "variation_set"]
    TEXT_FIELD_NUMBER: ClassVar[int]
    VARIATION_SET_FIELD_NUMBER: ClassVar[int]
    text: Text
    variation_set: VariationSet
    def __init__(self, text: Optional[Union[Text, Mapping]] = ..., variation_set: Optional[Union[VariationSet, Mapping]] = ...) -> None: ...

class Variation(_message.Message):
    __slots__ = ["allele", "copy_number", "haplotype", "text", "variation_set"]
    ALLELE_FIELD_NUMBER: ClassVar[int]
    COPY_NUMBER_FIELD_NUMBER: ClassVar[int]
    HAPLOTYPE_FIELD_NUMBER: ClassVar[int]
    TEXT_FIELD_NUMBER: ClassVar[int]
    VARIATION_SET_FIELD_NUMBER: ClassVar[int]
    allele: Allele
    copy_number: CopyNumber
    haplotype: Haplotype
    text: Text
    variation_set: VariationSet
    def __init__(self, allele: Optional[Union[Allele, Mapping]] = ..., haplotype: Optional[Union[Haplotype, Mapping]] = ..., copy_number: Optional[Union[CopyNumber, Mapping]] = ..., text: Optional[Union[Text, Mapping]] = ..., variation_set: Optional[Union[VariationSet, Mapping]] = ...) -> None: ...

class VariationSet(_message.Message):
    __slots__ = ["_id", "members"]
    class Member(_message.Message):
        __slots__ = ["allele", "copy_number", "curie", "haplotype", "text", "variation_set"]
        ALLELE_FIELD_NUMBER: ClassVar[int]
        COPY_NUMBER_FIELD_NUMBER: ClassVar[int]
        CURIE_FIELD_NUMBER: ClassVar[int]
        HAPLOTYPE_FIELD_NUMBER: ClassVar[int]
        TEXT_FIELD_NUMBER: ClassVar[int]
        VARIATION_SET_FIELD_NUMBER: ClassVar[int]
        allele: Allele
        copy_number: CopyNumber
        curie: str
        haplotype: Haplotype
        text: Text
        variation_set: VariationSet
        def __init__(self, curie: Optional[str] = ..., allele: Optional[Union[Allele, Mapping]] = ..., haplotype: Optional[Union[Haplotype, Mapping]] = ..., copy_number: Optional[Union[CopyNumber, Mapping]] = ..., text: Optional[Union[Text, Mapping]] = ..., variation_set: Optional[Union[VariationSet, Mapping]] = ...) -> None: ...
    MEMBERS_FIELD_NUMBER: ClassVar[int]
    _ID_FIELD_NUMBER: ClassVar[int]
    _id: str
    members: _containers.RepeatedCompositeFieldContainer[VariationSet.Member]
    def __init__(self, _id: Optional[str] = ..., members: Optional[Iterable[Union[VariationSet.Member, Mapping]]] = ...) -> None: ...
