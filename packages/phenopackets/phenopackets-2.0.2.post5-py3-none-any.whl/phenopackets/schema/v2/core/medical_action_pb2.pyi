from phenopackets.schema.v2.core import base_pb2 as _base_pb2
from phenopackets.schema.v2.core import measurement_pb2 as _measurement_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar, Iterable, Mapping, Optional, Union

ADMINISTRATION_RELATED_TO_PROCEDURE: DrugType
DESCRIPTOR: _descriptor.FileDescriptor
EHR_MEDICATION_LIST: DrugType
PRESCRIPTION: DrugType
UNKNOWN_DRUG_TYPE: DrugType

class DoseInterval(_message.Message):
    __slots__ = ["interval", "quantity", "schedule_frequency"]
    INTERVAL_FIELD_NUMBER: ClassVar[int]
    QUANTITY_FIELD_NUMBER: ClassVar[int]
    SCHEDULE_FREQUENCY_FIELD_NUMBER: ClassVar[int]
    interval: _base_pb2.TimeInterval
    quantity: _measurement_pb2.Quantity
    schedule_frequency: _base_pb2.OntologyClass
    def __init__(self, quantity: Optional[Union[_measurement_pb2.Quantity, Mapping]] = ..., schedule_frequency: Optional[Union[_base_pb2.OntologyClass, Mapping]] = ..., interval: Optional[Union[_base_pb2.TimeInterval, Mapping]] = ...) -> None: ...

class MedicalAction(_message.Message):
    __slots__ = ["adverse_events", "procedure", "radiation_therapy", "response_to_treatment", "therapeutic_regimen", "treatment", "treatment_intent", "treatment_target", "treatment_termination_reason"]
    ADVERSE_EVENTS_FIELD_NUMBER: ClassVar[int]
    PROCEDURE_FIELD_NUMBER: ClassVar[int]
    RADIATION_THERAPY_FIELD_NUMBER: ClassVar[int]
    RESPONSE_TO_TREATMENT_FIELD_NUMBER: ClassVar[int]
    THERAPEUTIC_REGIMEN_FIELD_NUMBER: ClassVar[int]
    TREATMENT_FIELD_NUMBER: ClassVar[int]
    TREATMENT_INTENT_FIELD_NUMBER: ClassVar[int]
    TREATMENT_TARGET_FIELD_NUMBER: ClassVar[int]
    TREATMENT_TERMINATION_REASON_FIELD_NUMBER: ClassVar[int]
    adverse_events: _containers.RepeatedCompositeFieldContainer[_base_pb2.OntologyClass]
    procedure: _base_pb2.Procedure
    radiation_therapy: RadiationTherapy
    response_to_treatment: _base_pb2.OntologyClass
    therapeutic_regimen: TherapeuticRegimen
    treatment: Treatment
    treatment_intent: _base_pb2.OntologyClass
    treatment_target: _base_pb2.OntologyClass
    treatment_termination_reason: _base_pb2.OntologyClass
    def __init__(self, procedure: Optional[Union[_base_pb2.Procedure, Mapping]] = ..., treatment: Optional[Union[Treatment, Mapping]] = ..., radiation_therapy: Optional[Union[RadiationTherapy, Mapping]] = ..., therapeutic_regimen: Optional[Union[TherapeuticRegimen, Mapping]] = ..., treatment_target: Optional[Union[_base_pb2.OntologyClass, Mapping]] = ..., treatment_intent: Optional[Union[_base_pb2.OntologyClass, Mapping]] = ..., response_to_treatment: Optional[Union[_base_pb2.OntologyClass, Mapping]] = ..., adverse_events: Optional[Iterable[Union[_base_pb2.OntologyClass, Mapping]]] = ..., treatment_termination_reason: Optional[Union[_base_pb2.OntologyClass, Mapping]] = ...) -> None: ...

class RadiationTherapy(_message.Message):
    __slots__ = ["body_site", "dosage", "fractions", "modality"]
    BODY_SITE_FIELD_NUMBER: ClassVar[int]
    DOSAGE_FIELD_NUMBER: ClassVar[int]
    FRACTIONS_FIELD_NUMBER: ClassVar[int]
    MODALITY_FIELD_NUMBER: ClassVar[int]
    body_site: _base_pb2.OntologyClass
    dosage: int
    fractions: int
    modality: _base_pb2.OntologyClass
    def __init__(self, modality: Optional[Union[_base_pb2.OntologyClass, Mapping]] = ..., body_site: Optional[Union[_base_pb2.OntologyClass, Mapping]] = ..., dosage: Optional[int] = ..., fractions: Optional[int] = ...) -> None: ...

class TherapeuticRegimen(_message.Message):
    __slots__ = ["end_time", "external_reference", "ontology_class", "regimen_status", "start_time"]
    class RegimenStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
    COMPLETED: TherapeuticRegimen.RegimenStatus
    DISCONTINUED: TherapeuticRegimen.RegimenStatus
    END_TIME_FIELD_NUMBER: ClassVar[int]
    EXTERNAL_REFERENCE_FIELD_NUMBER: ClassVar[int]
    ONTOLOGY_CLASS_FIELD_NUMBER: ClassVar[int]
    REGIMEN_STATUS_FIELD_NUMBER: ClassVar[int]
    STARTED: TherapeuticRegimen.RegimenStatus
    START_TIME_FIELD_NUMBER: ClassVar[int]
    UNKNOWN_STATUS: TherapeuticRegimen.RegimenStatus
    end_time: _base_pb2.TimeElement
    external_reference: _base_pb2.ExternalReference
    ontology_class: _base_pb2.OntologyClass
    regimen_status: TherapeuticRegimen.RegimenStatus
    start_time: _base_pb2.TimeElement
    def __init__(self, external_reference: Optional[Union[_base_pb2.ExternalReference, Mapping]] = ..., ontology_class: Optional[Union[_base_pb2.OntologyClass, Mapping]] = ..., start_time: Optional[Union[_base_pb2.TimeElement, Mapping]] = ..., end_time: Optional[Union[_base_pb2.TimeElement, Mapping]] = ..., regimen_status: Optional[Union[TherapeuticRegimen.RegimenStatus, str]] = ...) -> None: ...

class Treatment(_message.Message):
    __slots__ = ["agent", "cumulative_dose", "dose_intervals", "drug_type", "route_of_administration"]
    AGENT_FIELD_NUMBER: ClassVar[int]
    CUMULATIVE_DOSE_FIELD_NUMBER: ClassVar[int]
    DOSE_INTERVALS_FIELD_NUMBER: ClassVar[int]
    DRUG_TYPE_FIELD_NUMBER: ClassVar[int]
    ROUTE_OF_ADMINISTRATION_FIELD_NUMBER: ClassVar[int]
    agent: _base_pb2.OntologyClass
    cumulative_dose: _measurement_pb2.Quantity
    dose_intervals: _containers.RepeatedCompositeFieldContainer[DoseInterval]
    drug_type: DrugType
    route_of_administration: _base_pb2.OntologyClass
    def __init__(self, agent: Optional[Union[_base_pb2.OntologyClass, Mapping]] = ..., route_of_administration: Optional[Union[_base_pb2.OntologyClass, Mapping]] = ..., dose_intervals: Optional[Iterable[Union[DoseInterval, Mapping]]] = ..., drug_type: Optional[Union[DrugType, str]] = ..., cumulative_dose: Optional[Union[_measurement_pb2.Quantity, Mapping]] = ...) -> None: ...

class DrugType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
