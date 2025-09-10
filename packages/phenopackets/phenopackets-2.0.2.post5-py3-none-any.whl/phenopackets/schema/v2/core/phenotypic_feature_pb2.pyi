from phenopackets.schema.v2.core import base_pb2 as _base_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar, Iterable, Mapping, Optional, Union

DESCRIPTOR: _descriptor.FileDescriptor

class PhenotypicFeature(_message.Message):
    __slots__ = ["description", "evidence", "excluded", "modifiers", "onset", "resolution", "severity", "type"]
    DESCRIPTION_FIELD_NUMBER: ClassVar[int]
    EVIDENCE_FIELD_NUMBER: ClassVar[int]
    EXCLUDED_FIELD_NUMBER: ClassVar[int]
    MODIFIERS_FIELD_NUMBER: ClassVar[int]
    ONSET_FIELD_NUMBER: ClassVar[int]
    RESOLUTION_FIELD_NUMBER: ClassVar[int]
    SEVERITY_FIELD_NUMBER: ClassVar[int]
    TYPE_FIELD_NUMBER: ClassVar[int]
    description: str
    evidence: _containers.RepeatedCompositeFieldContainer[_base_pb2.Evidence]
    excluded: bool
    modifiers: _containers.RepeatedCompositeFieldContainer[_base_pb2.OntologyClass]
    onset: _base_pb2.TimeElement
    resolution: _base_pb2.TimeElement
    severity: _base_pb2.OntologyClass
    type: _base_pb2.OntologyClass
    def __init__(self, description: Optional[str] = ..., type: Optional[Union[_base_pb2.OntologyClass, Mapping]] = ..., excluded: bool = ..., severity: Optional[Union[_base_pb2.OntologyClass, Mapping]] = ..., modifiers: Optional[Iterable[Union[_base_pb2.OntologyClass, Mapping]]] = ..., onset: Optional[Union[_base_pb2.TimeElement, Mapping]] = ..., resolution: Optional[Union[_base_pb2.TimeElement, Mapping]] = ..., evidence: Optional[Iterable[Union[_base_pb2.Evidence, Mapping]]] = ...) -> None: ...
