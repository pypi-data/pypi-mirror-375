from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar, Mapping, Optional, Union

DESCRIPTOR: _descriptor.FileDescriptor

class Age(_message.Message):
    __slots__ = ["iso8601duration"]
    ISO8601DURATION_FIELD_NUMBER: ClassVar[int]
    iso8601duration: str
    def __init__(self, iso8601duration: Optional[str] = ...) -> None: ...

class AgeRange(_message.Message):
    __slots__ = ["end", "start"]
    END_FIELD_NUMBER: ClassVar[int]
    START_FIELD_NUMBER: ClassVar[int]
    end: Age
    start: Age
    def __init__(self, start: Optional[Union[Age, Mapping]] = ..., end: Optional[Union[Age, Mapping]] = ...) -> None: ...

class Evidence(_message.Message):
    __slots__ = ["evidence_code", "reference"]
    EVIDENCE_CODE_FIELD_NUMBER: ClassVar[int]
    REFERENCE_FIELD_NUMBER: ClassVar[int]
    evidence_code: OntologyClass
    reference: ExternalReference
    def __init__(self, evidence_code: Optional[Union[OntologyClass, Mapping]] = ..., reference: Optional[Union[ExternalReference, Mapping]] = ...) -> None: ...

class ExternalReference(_message.Message):
    __slots__ = ["description", "id", "reference"]
    DESCRIPTION_FIELD_NUMBER: ClassVar[int]
    ID_FIELD_NUMBER: ClassVar[int]
    REFERENCE_FIELD_NUMBER: ClassVar[int]
    description: str
    id: str
    reference: str
    def __init__(self, id: Optional[str] = ..., reference: Optional[str] = ..., description: Optional[str] = ...) -> None: ...

class File(_message.Message):
    __slots__ = ["file_attributes", "individual_to_file_identifiers", "uri"]
    class FileAttributesEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: ClassVar[int]
        VALUE_FIELD_NUMBER: ClassVar[int]
        key: str
        value: str
        def __init__(self, key: Optional[str] = ..., value: Optional[str] = ...) -> None: ...
    class IndividualToFileIdentifiersEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: ClassVar[int]
        VALUE_FIELD_NUMBER: ClassVar[int]
        key: str
        value: str
        def __init__(self, key: Optional[str] = ..., value: Optional[str] = ...) -> None: ...
    FILE_ATTRIBUTES_FIELD_NUMBER: ClassVar[int]
    INDIVIDUAL_TO_FILE_IDENTIFIERS_FIELD_NUMBER: ClassVar[int]
    URI_FIELD_NUMBER: ClassVar[int]
    file_attributes: _containers.ScalarMap[str, str]
    individual_to_file_identifiers: _containers.ScalarMap[str, str]
    uri: str
    def __init__(self, uri: Optional[str] = ..., individual_to_file_identifiers: Optional[Mapping[str, str]] = ..., file_attributes: Optional[Mapping[str, str]] = ...) -> None: ...

class GestationalAge(_message.Message):
    __slots__ = ["days", "weeks"]
    DAYS_FIELD_NUMBER: ClassVar[int]
    WEEKS_FIELD_NUMBER: ClassVar[int]
    days: int
    weeks: int
    def __init__(self, weeks: Optional[int] = ..., days: Optional[int] = ...) -> None: ...

class OntologyClass(_message.Message):
    __slots__ = ["id", "label"]
    ID_FIELD_NUMBER: ClassVar[int]
    LABEL_FIELD_NUMBER: ClassVar[int]
    id: str
    label: str
    def __init__(self, id: Optional[str] = ..., label: Optional[str] = ...) -> None: ...

class Procedure(_message.Message):
    __slots__ = ["body_site", "code", "performed"]
    BODY_SITE_FIELD_NUMBER: ClassVar[int]
    CODE_FIELD_NUMBER: ClassVar[int]
    PERFORMED_FIELD_NUMBER: ClassVar[int]
    body_site: OntologyClass
    code: OntologyClass
    performed: TimeElement
    def __init__(self, code: Optional[Union[OntologyClass, Mapping]] = ..., body_site: Optional[Union[OntologyClass, Mapping]] = ..., performed: Optional[Union[TimeElement, Mapping]] = ...) -> None: ...

class TimeElement(_message.Message):
    __slots__ = ["age", "age_range", "gestational_age", "interval", "ontology_class", "timestamp"]
    AGE_FIELD_NUMBER: ClassVar[int]
    AGE_RANGE_FIELD_NUMBER: ClassVar[int]
    GESTATIONAL_AGE_FIELD_NUMBER: ClassVar[int]
    INTERVAL_FIELD_NUMBER: ClassVar[int]
    ONTOLOGY_CLASS_FIELD_NUMBER: ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: ClassVar[int]
    age: Age
    age_range: AgeRange
    gestational_age: GestationalAge
    interval: TimeInterval
    ontology_class: OntologyClass
    timestamp: _timestamp_pb2.Timestamp
    def __init__(self, gestational_age: Optional[Union[GestationalAge, Mapping]] = ..., age: Optional[Union[Age, Mapping]] = ..., age_range: Optional[Union[AgeRange, Mapping]] = ..., ontology_class: Optional[Union[OntologyClass, Mapping]] = ..., timestamp: Optional[Union[_timestamp_pb2.Timestamp, Mapping]] = ..., interval: Optional[Union[TimeInterval, Mapping]] = ...) -> None: ...

class TimeInterval(_message.Message):
    __slots__ = ["end", "start"]
    END_FIELD_NUMBER: ClassVar[int]
    START_FIELD_NUMBER: ClassVar[int]
    end: _timestamp_pb2.Timestamp
    start: _timestamp_pb2.Timestamp
    def __init__(self, start: Optional[Union[_timestamp_pb2.Timestamp, Mapping]] = ..., end: Optional[Union[_timestamp_pb2.Timestamp, Mapping]] = ...) -> None: ...
