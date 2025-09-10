from phenopackets.schema.v2.core import base_pb2 as _base_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar, Iterable, Mapping, Optional, Union

DESCRIPTOR: _descriptor.FileDescriptor

class Disease(_message.Message):
    __slots__ = ["clinical_tnm_finding", "disease_stage", "excluded", "laterality", "onset", "primary_site", "resolution", "term"]
    CLINICAL_TNM_FINDING_FIELD_NUMBER: ClassVar[int]
    DISEASE_STAGE_FIELD_NUMBER: ClassVar[int]
    EXCLUDED_FIELD_NUMBER: ClassVar[int]
    LATERALITY_FIELD_NUMBER: ClassVar[int]
    ONSET_FIELD_NUMBER: ClassVar[int]
    PRIMARY_SITE_FIELD_NUMBER: ClassVar[int]
    RESOLUTION_FIELD_NUMBER: ClassVar[int]
    TERM_FIELD_NUMBER: ClassVar[int]
    clinical_tnm_finding: _containers.RepeatedCompositeFieldContainer[_base_pb2.OntologyClass]
    disease_stage: _containers.RepeatedCompositeFieldContainer[_base_pb2.OntologyClass]
    excluded: bool
    laterality: _base_pb2.OntologyClass
    onset: _base_pb2.TimeElement
    primary_site: _base_pb2.OntologyClass
    resolution: _base_pb2.TimeElement
    term: _base_pb2.OntologyClass
    def __init__(self, term: Optional[Union[_base_pb2.OntologyClass, Mapping]] = ..., excluded: bool = ..., onset: Optional[Union[_base_pb2.TimeElement, Mapping]] = ..., resolution: Optional[Union[_base_pb2.TimeElement, Mapping]] = ..., disease_stage: Optional[Iterable[Union[_base_pb2.OntologyClass, Mapping]]] = ..., clinical_tnm_finding: Optional[Iterable[Union[_base_pb2.OntologyClass, Mapping]]] = ..., primary_site: Optional[Union[_base_pb2.OntologyClass, Mapping]] = ..., laterality: Optional[Union[_base_pb2.OntologyClass, Mapping]] = ...) -> None: ...
