"""Provides a high-level abstraction for extracting patient info from FHIR R4 APIs."""

from __future__ import annotations

from datetime import date, datetime
import hashlib
import logging
from typing import Any, Final, Literal, Mapping, Optional, Sequence, Union

from dateutil.parser import ParserError, parse as dateutil_parse
from fhirpy import SyncFHIRClient
from fhirpy.base.exceptions import MultipleResourcesFound, ResourceNotFound
from fhirpy.base.utils import AttrDict
import pydash

from bitfount.data.persistence.caching import (
    EncryptedDiskcacheFunctionCache,
    FunctionCache,
)
from bitfount.externals.ehr.exceptions import GetPatientInfoError
from bitfount.externals.ehr.fhir_r4.exceptions import (
    FHIRR4APIError,
    NoFHIRR4PatientIDError,
    NoMatchingFHIRR4PatientError,
    NonSpecificFHIRR4PatientError,
)
from bitfount.externals.ehr.fhir_r4.types import (
    FHIRAppointment,
    FHIRCondition,
    FHIRPatient,
)
from bitfount.externals.ehr.nextgen.types import (
    PatientCodeDetails,
    RetrievedPatientDetailsJSON,
)
from bitfount.externals.ehr.types import EHRAppointment

_logger = logging.getLogger(__name__)

func_cache: FunctionCache = EncryptedDiskcacheFunctionCache()

DEFAULT_DUMP_ELEMENTS: frozenset[str] = frozenset(
    (
        "patientInfo",
        "appointments",
        "chart",
        "conditions",
        "encounters",
        "medications",
        "procedures",
    )
)

# Status for conditions, see for definition:
#    https://www.hl7.org/fhir/R4/valueset-condition-clinical.html
ClinicalStatus = Literal[
    "active", "recurrence", "relapse", "inactive", "remission", "resolved"
]

# Statuses for procedures, see for definition:
#    http://hl7.org/fhir/ValueSet/event-status
ProcedureStatus = Literal[
    "preparation",
    "in-progress",
    "not-done",
    "on-hold",
    "stopped",
    "completed",
    "entered-in-error",
    "unknown",
]

CodeSystems = Literal["icd10", "snomed", "cpt4"]

ICD_10_SYSTEM_IDENTIFIER: Final[str] = "http://hl7.org/fhir/sid/icd-10-cm"
SNOMED_SYSTEM_IDENTIFIER: Final[str] = "http://snomed.info/sct"
CPT_4_SYSTEM_IDENTIFIER: Final[str] = "http://www.ama-assn.org/go/cpt"

CODE_SYSTEM_TO_IDENTIFIER: dict[str, str] = {
    "icd10": ICD_10_SYSTEM_IDENTIFIER,
    "snomed": SNOMED_SYSTEM_IDENTIFIER,
    "cpt4": CPT_4_SYSTEM_IDENTIFIER,
}

EHR_PROVIDER_HAS_APPT_ENDPOINT: dict[Optional[str], bool] = {
    None: True,
    "nextech": False,
    "epic": True,
}


def _get_token_hash(
    fhir_client: SyncFHIRClient,
) -> str:
    """Get a hashed token to use as cache key."""
    token = fhir_client.authorization
    if token is None:
        return ""
    return hashlib.sha256(token.encode("UTF-8")).hexdigest()


@func_cache.memoize(ignore=(0, "fhir_client"))
def _cached_search_resources(
    fhir_client: SyncFHIRClient,
    resource_type: str,
    token_hash: str,
    search_params: Mapping[str, Union[str, Sequence[str]]],
) -> list[dict[str, Any]]:
    """Cached search for FHIR resources.

    Args:
        fhir_client: The FHIR client instance (ignored in cache key).
        resource_type: The type of FHIR resource to search for.
        token_hash: Hash of current token as cache key, cache will be
          invalidated when token is refreshed.
        search_params: JSON-serializable search parameters.

    Returns:
        List of serialized FHIR resources.
    """
    resources = fhir_client.resources(resource_type).search(**search_params).fetch_all()
    return [dict(resource) for resource in resources]


@func_cache.memoize(ignore=(0, "fhir_client"))
def _cached_get_resource(
    fhir_client: SyncFHIRClient,
    resource_type: str,
    token_hash: str,
    search_params: dict[str, str],
) -> Optional[dict[str, Any]]:
    """Cached get for a single FHIR resource.

    Args:
        fhir_client: The FHIR client instance (ignored in cache key).
        resource_type: The type of FHIR resource to search for.
        token_hash: Hash of current token as cache key, cache will be
          invalidated when token is refreshed.
        search_params: JSON-serializable search parameters.

    Returns:
        Serialized FHIR resource or None if not found.
    """
    try:
        resource = fhir_client.resources(resource_type).search(**search_params).get()
        return dict(resource) if resource else None
    except (ResourceNotFound, MultipleResourcesFound):
        # Let the original method handle these exceptions with proper context
        raise


@func_cache.memoize(ignore=(0, "fhir_client"))
def _cached_first_resource(
    fhir_client: SyncFHIRClient,
    resource_type: str,
    token_hash: str,
    search_params: Mapping[str, Union[str, Sequence[str]]],
) -> Optional[dict[str, Any]]:
    """Cached first for a single FHIR resource.

    Args:
        fhir_client: The FHIR client instance (ignored in cache key).
        resource_type: The type of FHIR resource to search for.
        token_hash: Hash of current token as cache key, cache will be
          invalidated when token is refreshed.
        search_params: JSON-serializable search parameters.

    Returns:
        Serialized FHIR resource or None if not found.
    """
    resource = fhir_client.resources(resource_type).search(**search_params).first()
    return dict(resource) if resource else None


class FHIRR4PatientQuerier:
    """Provides query/data extraction methods for a given patient.

    This class is a higher-level abstraction than the direct API interactions,
    providing methods for extracting/munging data from the API responses.
    """

    def __init__(
        self,
        patient_id: str,
        *,
        fhir_client: SyncFHIRClient,
        fhir_patient_info: Optional[RetrievedPatientDetailsJSON] = None,
        ehr_provider: Optional[str] = None,
    ) -> None:
        """Create a FHIRR4PatientQuerier instance.

        Args:
            patient_id: The patient ID this querier corresponds to.
            fhir_client: FHIRClient instance.
            fhir_patient_info: FHIR Patient Info with contact details.
            ehr_provider: The EHR provider eg. "nextech", "epic"
        """
        self.patient_id = patient_id
        self.fhir_client = fhir_client
        self.fhir_patient_info: Optional[RetrievedPatientDetailsJSON] = (
            fhir_patient_info
        )
        self.ehr_provider = ehr_provider

    @classmethod
    def from_patient_query(
        cls,
        patient_dob: str | date,
        given_name: Optional[str] = None,
        family_name: Optional[str] = None,
        *,
        fhir_client: SyncFHIRClient,
        ehr_provider: Optional[str] = None,
    ) -> FHIRR4PatientQuerier:
        """Build a FHIRR4PatientQuerier from patient query details.

        Args:
            patient_dob: Patient date of birth.
            given_name: Patient given name.
            family_name: Patient family name.
            fhir_client: FHIRClient instance
            ehr_provider: The EHR provider eg. "nextech", "epic"

        Returns:
            NextGenPatientQuerier for the target patient.

        Raises:
            NoMatchingFHIRR4PatientError: No patients matching the name/dob criteria
               could be found
            NonSpecificFHIRR4PatientError: Multiple patients match the criteria, could
               not determine the correct one
            NoFHIRR4PatientIDError: Patient matching the criteria was found, but no
               patient ID was associated
        """
        # There also exists a Patient/$match operation in FHIR R4
        # Which exists for services that have an MPI (Master Patient Index)
        # However it's not a first class operation in most FHIR clients,
        # probably as most servers don't have an MPI.
        # So we'll use the Patient.where operation for now until we know how to identify
        # if $match is supported.
        if isinstance(patient_dob, str):
            patient_dob_str = patient_dob
        else:
            patient_dob_str = patient_dob.strftime("%Y-%m-%d")

        try:
            # Use cached search for patient lookup
            search_params = {}
            if given_name:
                search_params["name"] = given_name
            if family_name:
                search_params["family"] = family_name
            search_params["birthdate"] = patient_dob_str

            patient_dict = _cached_get_resource(
                fhir_client=fhir_client,
                resource_type="Patient",
                token_hash=_get_token_hash(fhir_client),
                search_params=search_params,
            )

            if patient_dict is None:
                fhir_patient = None
            else:
                fhir_patient = fhir_client.resource(FHIRPatient, **patient_dict)

        except ResourceNotFound as e:
            _logger.error(
                f"Unable to find patient record based on name and dob: {str(e)}"
            )
            raise NoMatchingFHIRR4PatientError(
                "Unable to find patient record based on name and dob"
            ) from e
        except MultipleResourcesFound as e:
            raise NonSpecificFHIRR4PatientError(
                "Multiple patients found based on name and dob"
            ) from e

        if fhir_patient is None:
            _logger.warning("Unable to find patient record based on name and dob")
            raise NoMatchingFHIRR4PatientError(
                "Unable to find patient record based on name and dob"
            )

        patient_id = fhir_patient.id

        if not patient_id:
            raise NoFHIRR4PatientIDError(
                "Found matching patient information but could not extract patient ID."
            )

        dob_string: Optional[str] = None
        if isinstance(patient_dob, str):
            dob_string = patient_dob
        elif isinstance(patient_dob, date):
            dob_string = patient_dob.strftime("%Y-%m-%d")

        patient_info = RetrievedPatientDetailsJSON(
            id=patient_id,
            given_name=given_name,
            family_name=family_name,
            date_of_birth=dob_string,
            gender=fhir_patient.gender,
            home_numbers=cls._get_phone_number_from_patient(fhir_patient, use="home"),
            cell_numbers=cls._get_phone_number_from_patient(fhir_patient, use="mobile"),
            emails=[
                tel.value for tel in fhir_patient.telecom or [] if tel.system == "email"
            ],
            mailing_address=cls._get_address_from_patient(fhir_patient),
            medical_record_number=cls._extract_mrn(fhir_patient),
        )

        return cls(
            patient_id,
            fhir_client=fhir_client,
            fhir_patient_info=patient_info,
            ehr_provider=ehr_provider,
        )

    @staticmethod
    def _get_phone_number_from_patient(patient: FHIRPatient, use: str) -> list[str]:
        """Extract phone number from FHIRPatient object."""
        # Refer to https://build.fhir.org/datatypes.html#ContactPoint
        # use values: home | work | temp | old | mobile
        # system values: phone | fax | email | pager | url | sms | other
        return [
            tel.value
            for tel in patient.telecom
            if tel.use == use and tel.system not in ("email", "url")
        ]

    @staticmethod
    def _get_address_from_patient(patient: FHIRPatient) -> Optional[str]:
        """Extract address from FHIRPatient object."""
        if not patient.address:
            return None

        # Refer to https://build.fhir.org/datatypes.html#Address
        address_object = patient.address[0]

        # It might already exist fully constructed
        if address_object.text:
            address_string: Optional[str] = address_object.text
            return address_string

        # If text is not available, build it from its parts.
        if not address_object.line:
            address_string = ""
        else:
            address_string = " ".join(address_object.line)

        for address_part in [
            getattr(address_object, "city", ""),
            getattr(address_object, "district", ""),
            getattr(address_object, "state", ""),
            getattr(address_object, "postalCode", ""),
        ]:
            if address_part:
                address_string += f" {address_part}"

        return address_string

    @staticmethod
    def _extract_mrn(patient_entry: FHIRPatient) -> Optional[str]:
        """Extract MRN from FHIRPatient object."""
        mrns = pydash.filter_(
            getattr(patient_entry, "identifier", []),
            {"type": {"text": "Medical Record Number"}},
        )

        if len(mrns) == 0:
            _logger.info("No MRN identifier found.")
            return None

        if len(mrns) > 1:
            _logger.info("Found more than one MRN, returning the first one found.")

        mrn_value: str = mrns[0].value
        return mrn_value

    def get_patient_condition_code_states(
        self,
        statuses_filter: Optional[list[ClinicalStatus]] = None,
        code_types_filter: Optional[list[CodeSystems]] = None,
    ) -> list[str]:
        """Get condition codes related to this patient.

        Args:
            statuses_filter: If provided, returns only conditions of that status
               e.g. ['active','recurrence']
            code_types_filter: If provided, returns only conditions with codes
               of a specific code system (ICD10, Snomed) e.g. ["icd10"]

        Returns:
            A list of condition codes diagnosed for the patient.

        Raises:
            FHIRR4GetPatientInfoError: If unable to retrieve patient condition
            information.
        """
        params = {}
        if statuses_filter:
            params["clinical_status"] = ",".join(statuses_filter)
        if code_types_filter:
            params["code"] = ",".join(
                CODE_SYSTEM_TO_IDENTIFIER[code_type] + "|"
                for code_type in code_types_filter
            )

        try:
            # Use cached search for conditions
            search_params = {"patient": self.patient_id}
            search_params.update(params)

            condition_dicts = _cached_search_resources(
                fhir_client=self.fhir_client,
                resource_type="Condition",
                token_hash=_get_token_hash(self.fhir_client),
                search_params=search_params,
            )

            patient_conditions = [
                self.fhir_client.resource(FHIRCondition, **resource_dict)
                for resource_dict in condition_dicts
            ]
        except Exception as e:
            # If an error occurred, raise an exception for this
            _logger.error(
                f"Unable to retrieve conditions information for patient: {str(e)}"
            )
            raise FHIRR4GetPatientInfoError(
                "Unable to retrieve conditions information for patient"
            ) from e

        # If None is returned, it's not just that there were no entries, it's that
        # there was an issue retrieving the list itself. Raise an error in this event.
        if patient_conditions is None:
            message = "Patient conditions/diagnoses information could not be retrieved"  # type: ignore[unreachable] # Reason: error handling # noqa: E501
            _logger.warning(message)
            raise FHIRR4GetPatientInfoError(message)

        # Extract all codes from each condition
        icd10_codes_in_conditions: set[str] = set()
        for condition in patient_conditions:
            # a condition can have multiple codes
            # likely to handle different systems of coding
            condition_codes = [
                coding.code
                for coding in condition.code.coding
                if coding.code is not None
            ]
            icd10_codes_in_conditions.update(condition_codes)

        return list(icd10_codes_in_conditions)

    def get_patient_procedure_code_states(
        self,
        statuses_filter: Optional[list[ProcedureStatus]] = None,
        code_types_filter: Optional[list[CodeSystems]] = None,
    ) -> list[str]:
        """Get information of procedure codes this patient has.

        Args:
            statuses_filter: If provided, returns only procedures of that status
               e.g. ['completed', 'in-progress']
            code_types_filter: If provided, returns only conditions with codes
               of a specific code system (CPT4, Snomed) e.g. ["cpt4", "snomed"]

        Returns:
            A list of procedure codes relevant for the patient.

        Raises:
            FHIRR4GetPatientInfoError: If unable to retrieve patient procedures
            information.
        """
        params = {}
        if statuses_filter:
            params["status"] = ",".join(statuses_filter)
        if code_types_filter:
            params["code"] = ",".join(
                CODE_SYSTEM_TO_IDENTIFIER[code_type] + "|"
                for code_type in code_types_filter
            )

        try:
            # Use cached search for procedures
            search_params = {"patient": self.patient_id}
            search_params.update(params)

            procedure_dicts = _cached_search_resources(
                fhir_client=self.fhir_client,
                resource_type="Procedure",
                token_hash=_get_token_hash(self.fhir_client),
                search_params=search_params,
            )

            patient_procedures = [
                self.fhir_client.resource("Procedure", **resource_dict)
                for resource_dict in procedure_dicts
            ]

        except Exception as e:
            # If an error occurred, raise an exception for this
            _logger.error(
                f"Unable to retrieve procedures information for patient: {str(e)}"
            )
            raise FHIRR4GetPatientInfoError(
                "Unable to retrieve procedures information for patient"
            ) from e

        # If None is returned, it's not just that there were no entries, it's that
        # there was an issue retrieving the list itself. Raise an error in this event.
        if patient_procedures is None:
            _logger.warning("Patient procedures information could not be retrieved")  # type: ignore[unreachable] # Reason: error handling # noqa: E501
            raise FHIRR4GetPatientInfoError(
                "Patient procedures information could not be retrieved"
            )

        # Extract the codes from each procedure
        cpt4_codes_in_procedures: set[str] = set()
        for procedure in patient_procedures:
            procedure_codes = [
                coding.code
                for coding in procedure.code.coding
                if coding.code is not None
            ]
            cpt4_codes_in_procedures.update(procedure_codes)

        return list(cpt4_codes_in_procedures)

    def get_patient_code_states(self) -> PatientCodeDetails:
        """Get information of Conditions and Procedures codes this patient has.

        Sugar method that combines get_patient_condition_code_states() and
        get_patient_procedure_code_states() and returns a pre-constructed
        PatientCodeDetails container.

        Returns:
            A PatientCodeDetails instance detailing the presence or absence of the
            provided Conditions and Procedures codes for the patient.

        Raises:
            FHIRR4GetPatientInfoError: If unable to retrieve condition information.
        """
        try:
            condition_code_states = self.get_patient_condition_code_states()
        except FHIRR4GetPatientInfoError:
            # If error occurred, mark all entries as unknown, carry on
            condition_code_states = None

        # Extract CPT4 Code details for patient
        try:
            procedure_code_states = self.get_patient_procedure_code_states()
        except FHIRR4GetPatientInfoError:
            # If error occurred, mark all entries as unknown, carry on
            procedure_code_states = None

        # Construct code details object
        return PatientCodeDetails(
            condition_codes=condition_code_states, procedure_codes=procedure_code_states
        )

    def get_next_appointment(self) -> Optional[date]:
        """Get the next appointment date for the patient.

        Falls back to encounters if appointments are not available or empty.

        Returns:
            The next appointment date for the patient from today, or None if they
            have no future appointment. Any cancelled or errored appointments
            are ignored.

        Raises:
            FHIRR4GetPatientInfoError: If unable to retrieve patient information.
        """
        if EHR_PROVIDER_HAS_APPT_ENDPOINT.get(self.ehr_provider, True):
            try:
                appointment_date = (
                    self._get_next_appointment_from_appointments_endpoint()
                )
                if appointment_date is not None:
                    return appointment_date
            except Exception as e:
                _logger.warning(
                    f"Failed to retrieve next appointment, trying encounters: {str(e)}"
                )
            else:
                _logger.info(
                    "Did not find a next appointment date, trying encounters endpoint."
                )

        # Fallback to encounters if appointments failed or returned None
        try:
            encounter_date = self._get_next_appointment_from_encounters_endpoint()
            return encounter_date
        except Exception as e:
            _logger.error(
                f"Unable to retrieve upcoming appointments/encounters"
                f" for patient: {str(e)}"
            )
            raise FHIRR4GetPatientInfoError(
                "Unable to retrieve upcoming appointments/encounters for patient"
            ) from e

    def _get_next_appointment_from_appointments_endpoint(self) -> Optional[date]:
        """Get next appointment from Appointment resources."""
        search_params = {
            "patient": self.patient_id,
            "date__gt": datetime.now().date().strftime("%Y-%m-%d"),
            "status__not": ["cancelled", "entered-in-error"],
            "_sort": "date",
        }

        appointment_dict = _cached_first_resource(
            fhir_client=self.fhir_client,
            resource_type="Appointment",
            token_hash=_get_token_hash(self.fhir_client),
            search_params=search_params,
        )

        if appointment_dict is None:
            return None

        next_appointment = self.fhir_client.resource(
            FHIRAppointment, **appointment_dict
        )
        appointment_date: Optional[datetime] = next_appointment.start

        if appointment_date is None:
            # start date may be None if status is proposed/waitlist/cancelled
            return None

        return appointment_date.date()

    def _get_next_appointment_from_encounters_endpoint(self) -> Optional[date]:
        """Get next appointment from Encounter resources."""
        # We use period.start instead of date, and different status values
        # planned | arrived | triaged | in-progress | onleave | finished | cancelled
        search_params = {
            "patient": self.patient_id,
            "date__gt": datetime.now().date().strftime("%Y-%m-%d"),
            "status__not": "cancelled",
            "_sort": "date",
        }
        encounter_dict = _cached_first_resource(
            fhir_client=self.fhir_client,
            resource_type="Encounter",
            token_hash=_get_token_hash(self.fhir_client),
            search_params=search_params,
        )

        if encounter_dict is None:
            return None

        # Extract the start date from the encounter period
        period = encounter_dict.get("period")
        if period and period.get("start"):
            next_encounter_date = self._parse_timestamp(period["start"], "encounter")
            if next_encounter_date:
                return next_encounter_date.date()

        return None

    def _get_previous_appointment_details(
        self,
        include_maybe_attended: bool = True,
    ) -> list[FHIRAppointment] | list[dict]:
        """Get the FHIRAppointment details of previous appointments.

        Falls back to encounters if appointments are not available or empty.

        Returns:
            The list of previous appointments for the patient, sorted
            chronologically, or an empty list if they have no
            previous appointments.

        Raises:
            FHIRR4GetPatientInfoError: If unable to retrieve patient information.
        """
        # First try to get appointments
        try:
            appointments = self._get_previous_appointments_from_appointments_endpoint(
                include_maybe_attended
            )
            if appointments:
                return appointments
        except Exception as e:
            _logger.warning(
                f"Failed to retrieve past appointments, trying encounters: {str(e)}"
            )
        else:
            _logger.info("Did not find any past appointment, trying encounters.")

        # Fallback to encounters if appointments failed or returned empty list
        try:
            appointments_from_encounters: list[dict] = (
                self._get_previous_appointments_from_encounters(include_maybe_attended)
            )
            return appointments_from_encounters
        except Exception as e:
            _logger.error(
                f"Unable to retrieve past appointments/encounters for patient: {str(e)}"
            )
            raise FHIRR4GetPatientInfoError(
                "Unable to retrieve past appointments/encounters for patient"
            ) from e

    def _get_previous_appointments_from_appointments_endpoint(
        self,
        include_maybe_attended: bool = True,
    ) -> list[FHIRAppointment]:
        """Get previous appointments from Appointment resources."""
        # Definitely attended: arrived | fulfilled | checked-in
        # Maybe attended: waitlist | booked | pending | proposed
        # Not attended: cancelled | entered-in-error | noshow

        if include_maybe_attended:
            excluded_status = ["cancelled", "entered-in-error", "noshow"]
        else:
            excluded_status = [
                "cancelled",
                "entered-in-error",
                "noshow",
                "waitlist",
                "booked",
                "pending",
                "proposed",
            ]

        # Use cached search for previous appointments
        search_params = {
            "patient": self.patient_id,
            "date__lt": datetime.now().date().strftime("%Y-%m-%d"),
            "status__not": excluded_status,
            "_sort": "date",
        }

        appointment_dicts = _cached_search_resources(
            fhir_client=self.fhir_client,
            resource_type="Appointment",
            token_hash=_get_token_hash(self.fhir_client),
            search_params=search_params,
        )

        # Creates FHIRAppointment object from dict
        previous_appointments: list[FHIRAppointment] = [
            self.fhir_client.resource(FHIRAppointment, **resource_dict)
            for resource_dict in appointment_dicts
        ]

        return previous_appointments

    def _get_previous_appointments_from_encounters(
        self,
        include_maybe_attended: bool = True,
    ) -> list[dict]:
        """Get previous appointments from Encounters."""
        # Definitely attended: arrived | finished
        # Maybe attended: planned | in-progress | triaged
        # Not attended: cancelled | onleave

        if include_maybe_attended:
            excluded_status = ["cancelled", "onleave"]
        else:
            excluded_status = [
                "cancelled",
                "onleave",
                "planned",
                "in-progress",
                "triaged",
            ]

        # Use cached search for previous encounters
        search_params = {
            "patient": self.patient_id,
            "date__lt": datetime.now().date().strftime("%Y-%m-%d"),
            "status__not": excluded_status,
            "_sort": "date",
        }

        encounter_dicts = _cached_search_resources(
            fhir_client=self.fhir_client,
            resource_type="Encounter",
            token_hash=_get_token_hash(self.fhir_client),
            search_params=search_params,
        )

        return encounter_dicts

    @staticmethod
    def _parse_timestamp(
        datetime_str: str, containing_entry_type_str: str
    ) -> Optional[datetime]:
        """Parses the timestamp string from an encounter to a datetime object.

        Timestamp string may contain milliseconds or not, so we use a more lenient
        parser than tying it to a specific format.

        Args:
            datetime_str: The timestamp string to be parsed.
            containing_entry_type_str: Type of entry that contains the timestamp,
                e.g. "appointment" or "encounter".

        Returns:
            The parsed datetime object, or None if the parsing failed.
        """
        try:
            return dateutil_parse(datetime_str)
        except (ParserError, TypeError) as e:
            _logger.warning(
                f"Unable to parse '{datetime_str}'; error was '{str(e)}'."
                f" Ignoring {containing_entry_type_str}."
            )
            return None

    def get_previous_appointment_details(
        self,
        include_maybe_attended: bool = True,
    ) -> list[EHRAppointment]:
        """Get list of previous appointments for the patient.

        Returns:
            A list of EHRAppointment for the patient, sorted
            chronologically, or an empty list if they have no
            previous appointments.

        Raises:
            FHIRR4GetPatientInfoError: If unable to retrieve patient information.
        """
        previous_appointments_or_encounters: list[FHIRAppointment] | list[dict] = (
            self._get_previous_appointment_details(
                include_maybe_attended=include_maybe_attended
            )
        )

        appointments_list: list[EHRAppointment] = []
        for appt in previous_appointments_or_encounters:
            if isinstance(appt, FHIRAppointment):
                appointment_date: Optional[date] = None
                if getattr(appt, "start", None):
                    appointment_date = appt.start.date()
                event_name = getattr(appt, "description", "")
            elif isinstance(appt, dict):
                # if it was a dict, it was retrieve from Encounters
                appointment_date = None
                if start := appt.get("period", {}).get("start", None):
                    if isinstance(start, str):
                        appointment_datetime = self._parse_timestamp(start, "encounter")
                    else:
                        appointment_datetime = start

                    if appointment_datetime is not None:
                        appointment_date = appointment_datetime.date()

                # We use the encounter type display as an event name, eg.
                # "type" : [{
                #     "coding" : [{
                #       "system" : "http://snomed.info/sct",
                #       "code" : "183807002",
                #       "display" : "Inpatient stay 9 days"
                #     }]
                #   }],
                event_name = ""
                if appt_type := appt.get("type"):
                    if coding := appt_type[0].get("coding"):
                        event_name = coding[0].get("display", "")

            appointments_list.append(
                EHRAppointment(
                    appointment_date=appointment_date,
                    location_name=None,
                    event_name=event_name,
                )
            )

        return appointments_list

    def get_patient_latest_medical_practitioner(self) -> Optional[str]:
        """Retrieves the latest medical practitioner for the patient.

        This is the rendering provider for the patient's last encounter.

        Returns:
            The name of the latest medical practitioner for the patient, or None if
            there is no name listed on the latest encounter.

        Raises:
            FHIRR4GetPatientInfoError: If unable to retrieve patient encounter
            information.
        """
        # This list of appointments is sorted chronologically
        previous_appointments: list[FHIRAppointment] | list[dict] = (
            self._get_previous_appointment_details()
        )

        # Iterate through list of appointment/encounter starting from latest
        #  to find a Practitioner
        # Practitioners will be found amongst list of participants of the appointment
        # and can be identified by the actor.reference "Practitioner/{practitioner-id}"
        # See https://build.fhir.org/appointment.html
        practitioner_id = None
        for appt in previous_appointments[::-1]:
            if isinstance(appt, FHIRAppointment):
                participants = getattr(appt, "participant", [])
                for participant in participants:
                    actor = getattr(participant, "actor", None)
                    if actor and (
                        practitioner := getattr(actor, "reference", "")
                    ).startswith("Practitioner"):
                        practitioner_id = practitioner.split("/")[1]
                        break
            elif isinstance(appt, dict):
                participants = appt.get("participant", [])
                for participant in participants:
                    individual = participant.get("individual")
                    if individual and (
                        practitioner := individual.get("reference", "")
                    ).startswith("Practitioner"):
                        practitioner_id = practitioner.split("/")[1]
                        break

            if practitioner_id is not None:
                break

        if practitioner_id is None:
            # We were unable to find any Practitioner records in previous appointments
            return None

        try:
            # Use cached search for practitioner
            search_params = {"_id": practitioner_id}

            practitioner_dict = _cached_first_resource(
                fhir_client=self.fhir_client,
                resource_type="Practitioner",
                token_hash=_get_token_hash(self.fhir_client),
                search_params=search_params,
            )

            if practitioner_dict is None:
                result = None
            else:
                result = self.fhir_client.resource("Practitioner", **practitioner_dict)

        except Exception as e:
            # If an error occurred, raise an exception for this
            _logger.error(
                f"Unable to retrieve latest medical practitioner for patient: {str(e)}"
            )
            raise FHIRR4GetPatientInfoError(
                "Unable to retrieve latest medical practitioner for patient"
            ) from e

        if result is None:
            # Could not find any Practitioners with this reference id
            return None

        if result.name:
            # result.name is a list of HumanName, we'll use the first one
            # https://build.fhir.org/datatypes.html#HumanName
            return self._format_practitioner_name(result.name[0])

        return None

    def _format_practitioner_name(self, practitioner_name: AttrDict) -> str:
        """Formats name of practioner by prefix-given-family name."""
        # See HumanName https://build.fhir.org/datatypes.html#HumanName
        name_parts = []

        if prefix := (practitioner_name.get("prefix") or [""])[0]:
            name_parts.append(prefix)

        if given := (practitioner_name.get("given") or [""])[0]:
            name_parts.append(given)

        if family := practitioner_name.get("family", ""):
            name_parts.append(family)

        return " ".join(name_parts)


# DEV: This exception is here because it is explicitly tied to this class. If
#      they begin to be used externally they should be moved to a common exceptions.py.
class FHIRR4GetPatientInfoError(GetPatientInfoError, FHIRR4APIError):
    """Could not retrieve patient info."""

    pass
