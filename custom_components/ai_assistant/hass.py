"""This module provides a service class for interacting with Home Assistant."""

from abc import ABC
import json
from typing import Annotated

from homeassistant.const import ATTR_ENTITY_ID
from pydantic import Field, model_validator

from .const import LOGGER

from .entity_cache import EntityCache

from .hass_provider import HassContextFactory

from .helpers import generate_available_time_slots_from_calendar_events

from .wrapper import Executor


class ThermostatAttributes:
    """Attributes of a thermostat."""

    def __init__(self, hvac_mode: str, target_temperature_low: float | None, target_temperature_high: float | None):
        """Initialize the attributes."""
        self.hvac_mode = hvac_mode
        self.target_temperature_low = target_temperature_low
        self.target_temperature_high = target_temperature_high

    def __str__(self):
        """Return a string representation of the attributes."""
        return f"Mode: {self.hvac_mode}, Low: {self.target_temperature_low}, High: {self.target_temperature_high}"


class HomeAssistantServiceResult:
    """Result of a service call."""

    def __init__(self, success: bool, error: list[str] | None = None, data=None):
        """Initialize the result."""
        self.success = success
        self.error = error
        self.data = data

    def __str__(self):
        """Return a string representation of the result."""
        return f"Success: {self.success}, Error: {self.error}"


class HomeAssistantService:
    """Service class for interacting with Home Assistant."""

    @staticmethod
    async def async_call_service(entity_ids: list[str], domain: str, service: str, data: dict = None) -> HomeAssistantServiceResult:
        """Call a service."""

        LOGGER.debug(f"Calling service {service} on entities {
                     entity_ids} in domain {domain} with data {data}")

        hass = HassContextFactory.get_instance()

        service_data = {ATTR_ENTITY_ID: entity_ids}
        if data is not None:
            service_data.update(data)

        try:
            await hass.services.async_call(
                domain,
                service,
                service_data,
                blocking=True,
            )

            return HomeAssistantServiceResult(success=True)
        except Exception as e:
            LOGGER.error(f"Error while running the service {
                         service} on entities {entity_ids}: {e}")
            return HomeAssistantServiceResult(success=False, error=[entity_ids])

    @staticmethod
    async def async_get_thermostat_mode(entity_id: str) -> ThermostatAttributes:
        """Get the current thermostat mode."""
        hass = HassContextFactory.get_instance()
        state = hass.states.get(entity_id)
        target_temperature_low = state.attributes.get("target_temp_low")
        target_temperature_high = state.attributes.get("target_temp_high")
        hvac_mode = state.state

        LOGGER.debug(f"Mode: {hvac_mode}, Low: {
                     target_temperature_low}, High: {target_temperature_high}")

        return ThermostatAttributes(hvac_mode, target_temperature_low, target_temperature_high)

    @staticmethod
    async def async_get_calendar_events(entity_ids: list[str], start_date: str, end_date: str) -> HomeAssistantServiceResult:
        """Get events from a calendar."""
        hass = HassContextFactory.get_instance()

        service_data = {ATTR_ENTITY_ID: entity_ids}
        data = {
            "start_date_time": start_date,
            "end_date_time": end_date
        }
        service_data.update(data)

        try:
            events = await hass.services.async_call(
                "calendar",
                "get_events",
                service_data,
                blocking=True,
                return_response=True
            )

            LOGGER.debug(f"Events: {events}")

            return HomeAssistantServiceResult(success=True, data=json.dumps(events))
        except Exception as e:
            LOGGER.error(f"Error while getting events for calendar {
                entity_ids}: {e}")
            return HomeAssistantServiceResult(success=False, error=[entity_ids])

    @staticmethod
    async def async_get_calendar_availability(entity_id: str, start_date: str, end_date: str) -> HomeAssistantServiceResult:
        """Get availability from a calendar."""
        hass = HassContextFactory.get_instance()

        service_data = {ATTR_ENTITY_ID: entity_id}
        data = {
            "start_date_time": start_date,
            "end_date_time": end_date
        }
        service_data.update(data)

        try:
            events = await hass.services.async_call(
                "calendar",
                "get_events",
                service_data,
                blocking=True,
                return_response=True
            )

            LOGGER.debug(f"Events: {events}")

            list_of_events = events.get(entity_id).get("events")

            available_slots = generate_available_time_slots_from_calendar_events(
                list_of_events, start_date, end_date)

            return HomeAssistantServiceResult(success=True, data=json.dumps(available_slots))

        except Exception as e:
            LOGGER.error(f"Error while getting events for calendar {
                entity_id}: {e}")
            return HomeAssistantServiceResult(success=False, error=[entity_id])

    @staticmethod
    async def async_create_calendar_event(entity_id: str, start_date: str, end_date: str, summary: str) -> HomeAssistantServiceResult:
        """Create a calendar event."""
        hass = HassContextFactory.get_instance()

        service_data = {ATTR_ENTITY_ID: entity_id}

        data = {
            "start_date_time": start_date,
            "end_date_time": end_date,
            "summary": summary
        }

        service_data.update(data)

        try:
            await hass.services.async_call(
                "calendar",
                "create_event",
                service_data,
                blocking=True
            )

            return HomeAssistantServiceResult(success=True)

        except Exception as e:
            LOGGER.error(f"Error while creating event for calendar {
                entity_id}: {e}")
            return HomeAssistantServiceResult(success=False, error=[entity_id])


class HassBaseExecutor(Executor, ABC):
    """Base class for all Home Assistant executors.

    All home assistant executors must inherit from this class. This class adds a domain property to the executor.
    """

    action: Annotated[str | None, Field(
        "Action to perform on the entities")] = ""

    @property
    def domain(self):
        """Get the domain of the executor."""
        return self._domain

    @domain.setter
    def domain(self, value):
        self._domain = value


class HassMultipleEntityExecutor(HassBaseExecutor, ABC):
    """Base class for all Home Assistant executors that deal with a list of entity IDs.

    Provides a default implementation of :meth:`Executor.execute` that calls :meth:`HomeAssistantService.async_call_service` with the list of entity IDs and action.
    This method can be overridden by subclasses to provide custom implementations.
    """

    entity_ids: Annotated[list[str], Field(
        "Entity IDs of the entities to control")]

    @model_validator(mode="after")
    def validate_entity_ids(self) -> "HassMultipleEntityExecutor":
        """Validate the entity IDs provided in the tool call."""

        # Get a list of corrected entity IDs
        entity_id_list = self.corrected_entity_ids()

        # Get cached map of entity IDs to domains
        entity_cache = EntityCache.get_instance()

        invalid_entity_ids = []
        non_existent_entity_ids = []
        incorrect_domain_entity_ids = []

        # Check if the entity IDs provided are valid
        for entity_id in entity_id_list:
            if not entity_cache.is_exposed_entity(entity_id, self.domain):
                invalid_entity_ids.append(entity_id)

        for entity_id in invalid_entity_ids:
            if entity_id.split(".")[0] != self.domain:
                incorrect_domain_entity_ids.append(entity_id)
            else:
                non_existent_entity_ids.append(entity_id)

        error_message = ""
        if non_existent_entity_ids:
            error_message += f"Entity IDs {
                non_existent_entity_ids} do not exist. Please provide valid entity IDs from the list provided to you."

        if incorrect_domain_entity_ids:
            error_message += f"Entity IDs {incorrect_domain_entity_ids} do not belong to the {
                self.domain} domain. Please provide valid entity IDs from the list provided to you."

        if len(invalid_entity_ids) > 0:
            raise ValueError(error_message)

        return self

    # TODO: Consider making this a stored property
    def corrected_entity_ids(self) -> list[str]:
        """Check if every entity ID is the list is appended with domain. Appends the domain if not."""
        corrected_entity_ids = []
        for entity_id in self.entity_ids:
            if "." not in entity_id:
                LOGGER.debug(
                    f"Prepending {self.domain} domain to entity ID: {entity_id}")
                entity_id = f"{self.domain}.{entity_id}"
            corrected_entity_ids.append(entity_id)
        return corrected_entity_ids

    async def execute(self) -> HomeAssistantServiceResult:
        """Execute the tool call by calling the service on the list of entity IDs.

        Returns:
            HomeAssistantServiceResult: Result of the service call.

        """
        result = await HomeAssistantService.async_call_service(
            self.corrected_entity_ids(), self.domain, self.action)

        return result.success


class HassSingleEntityExecutor(HassBaseExecutor, ABC):
    """Base class for all Home Assistant executors that deal with a single entity ID.

    Provides a default implementation of :meth:`Executor.execute` that calls :meth:`HomeAssistantService.async_call_service` with the entity ID and action.
    This method can be overridden by subclasses to provide custom implementations.

    All Home Assistant executors must inherit from this class.
    """

    entity_id: Annotated[str, Field("Entity ID of the entity to control")]

    @model_validator(mode="after")
    def validate_entity_id(self) -> "HassSingleEntityExecutor":
        """Validate the entity ID provided in the tool call."""

        # Get a list of corrected entity IDs
        entity_id = self.corrected_entity_id()

        # Get cached map of entity IDs to domains
        entity_cache = EntityCache.get_instance()

        # Check if the entity ID provided is valid
        if not entity_cache.is_exposed_entity(entity_id, self.domain):
            if entity_id.split(".")[0] != self.domain:
                raise ValueError(
                    f"Entity ID {entity_id} does not belong to the {self.domain} domain. Please provide a valid entity ID from the list provided to you.")
            else:
                raise ValueError(
                    f"Entity ID {entity_id} does not exist. Please provide a valid entity ID from the list provided to you.")

        return self

    def corrected_entity_id(self) -> str:
        """Check if the entity ID is appended with domain. Appends the domain if not."""
        if "." not in self.entity_id:
            LOGGER.debug(
                f"Prepending {self.domain} domain to entity ID: {self.entity_id}")
            self.entity_id = f"{self.domain}.{self.entity_id}"

        return self.entity_id

    async def execute(self) -> HomeAssistantServiceResult:
        """Execute the tool call by calling the service on the entity ID.

        Returns:
            HomeAssistantServiceResult: Result of the service call.

        """
        result = await HomeAssistantService.async_call_service(
            [self.corrected_entity_id()], self.domain, self.action)

        return result.success
