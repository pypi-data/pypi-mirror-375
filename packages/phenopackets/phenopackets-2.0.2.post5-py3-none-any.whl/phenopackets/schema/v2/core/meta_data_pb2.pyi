from google.protobuf import timestamp_pb2 as _timestamp_pb2
from phenopackets.schema.v2.core import base_pb2 as _base_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar, Iterable, Mapping, Optional, Union

DESCRIPTOR: _descriptor.FileDescriptor

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
    external_references: _containers.RepeatedCompositeFieldContainer[_base_pb2.ExternalReference]
    phenopacket_schema_version: str
    resources: _containers.RepeatedCompositeFieldContainer[Resource]
    submitted_by: str
    updates: _containers.RepeatedCompositeFieldContainer[Update]
    def __init__(self, created: Optional[Union[_timestamp_pb2.Timestamp, Mapping]] = ..., created_by: Optional[str] = ..., submitted_by: Optional[str] = ..., resources: Optional[Iterable[Union[Resource, Mapping]]] = ..., updates: Optional[Iterable[Union[Update, Mapping]]] = ..., phenopacket_schema_version: Optional[str] = ..., external_references: Optional[Iterable[Union[_base_pb2.ExternalReference, Mapping]]] = ...) -> None: ...

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

class Update(_message.Message):
    __slots__ = ["comment", "timestamp", "updated_by"]
    COMMENT_FIELD_NUMBER: ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: ClassVar[int]
    UPDATED_BY_FIELD_NUMBER: ClassVar[int]
    comment: str
    timestamp: _timestamp_pb2.Timestamp
    updated_by: str
    def __init__(self, timestamp: Optional[Union[_timestamp_pb2.Timestamp, Mapping]] = ..., updated_by: Optional[str] = ..., comment: Optional[str] = ...) -> None: ...
