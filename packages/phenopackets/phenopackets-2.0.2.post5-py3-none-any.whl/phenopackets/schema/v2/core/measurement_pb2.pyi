from phenopackets.schema.v2.core import base_pb2 as _base_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar, Iterable, Mapping, Optional, Union

DESCRIPTOR: _descriptor.FileDescriptor

class ComplexValue(_message.Message):
    __slots__ = ["typed_quantities"]
    TYPED_QUANTITIES_FIELD_NUMBER: ClassVar[int]
    typed_quantities: _containers.RepeatedCompositeFieldContainer[TypedQuantity]
    def __init__(self, typed_quantities: Optional[Iterable[Union[TypedQuantity, Mapping]]] = ...) -> None: ...

class Measurement(_message.Message):
    __slots__ = ["assay", "complex_value", "description", "procedure", "time_observed", "value"]
    ASSAY_FIELD_NUMBER: ClassVar[int]
    COMPLEX_VALUE_FIELD_NUMBER: ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: ClassVar[int]
    PROCEDURE_FIELD_NUMBER: ClassVar[int]
    TIME_OBSERVED_FIELD_NUMBER: ClassVar[int]
    VALUE_FIELD_NUMBER: ClassVar[int]
    assay: _base_pb2.OntologyClass
    complex_value: ComplexValue
    description: str
    procedure: _base_pb2.Procedure
    time_observed: _base_pb2.TimeElement
    value: Value
    def __init__(self, description: Optional[str] = ..., assay: Optional[Union[_base_pb2.OntologyClass, Mapping]] = ..., value: Optional[Union[Value, Mapping]] = ..., complex_value: Optional[Union[ComplexValue, Mapping]] = ..., time_observed: Optional[Union[_base_pb2.TimeElement, Mapping]] = ..., procedure: Optional[Union[_base_pb2.Procedure, Mapping]] = ...) -> None: ...

class Quantity(_message.Message):
    __slots__ = ["reference_range", "unit", "value"]
    REFERENCE_RANGE_FIELD_NUMBER: ClassVar[int]
    UNIT_FIELD_NUMBER: ClassVar[int]
    VALUE_FIELD_NUMBER: ClassVar[int]
    reference_range: ReferenceRange
    unit: _base_pb2.OntologyClass
    value: float
    def __init__(self, unit: Optional[Union[_base_pb2.OntologyClass, Mapping]] = ..., value: Optional[float] = ..., reference_range: Optional[Union[ReferenceRange, Mapping]] = ...) -> None: ...

class ReferenceRange(_message.Message):
    __slots__ = ["high", "low", "unit"]
    HIGH_FIELD_NUMBER: ClassVar[int]
    LOW_FIELD_NUMBER: ClassVar[int]
    UNIT_FIELD_NUMBER: ClassVar[int]
    high: float
    low: float
    unit: _base_pb2.OntologyClass
    def __init__(self, unit: Optional[Union[_base_pb2.OntologyClass, Mapping]] = ..., low: Optional[float] = ..., high: Optional[float] = ...) -> None: ...

class TypedQuantity(_message.Message):
    __slots__ = ["quantity", "type"]
    QUANTITY_FIELD_NUMBER: ClassVar[int]
    TYPE_FIELD_NUMBER: ClassVar[int]
    quantity: Quantity
    type: _base_pb2.OntologyClass
    def __init__(self, type: Optional[Union[_base_pb2.OntologyClass, Mapping]] = ..., quantity: Optional[Union[Quantity, Mapping]] = ...) -> None: ...

class Value(_message.Message):
    __slots__ = ["ontology_class", "quantity"]
    ONTOLOGY_CLASS_FIELD_NUMBER: ClassVar[int]
    QUANTITY_FIELD_NUMBER: ClassVar[int]
    ontology_class: _base_pb2.OntologyClass
    quantity: Quantity
    def __init__(self, quantity: Optional[Union[Quantity, Mapping]] = ..., ontology_class: Optional[Union[_base_pb2.OntologyClass, Mapping]] = ...) -> None: ...
