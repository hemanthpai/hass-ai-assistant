"""This module contains classes to control various Home Assistant entities such as switches, locks, covers, fans, vacuums, automations, scenes, and scripts."""

from typing import Annotated, Literal

from pydantic import Field
from ..hass import HassMultipleEntityExecutor, HassSingleEntityExecutor, HomeAssistantService


class Switch(HassMultipleEntityExecutor):
    """Control entities of type switch."""

    entity_ids: Annotated[list[str], Field(
        description="List of entity IDs of the switches to control")]
    action: Annotated[Literal["turn_on", "turn_off", "toggle"], Field(
        description="Action to perform on the switches. Valid actions are 'turn_on', 'turn_off', and 'toggle'")]

    def get_domain(self) -> str:
        """Return the domain of the entity."""
        return "switch"


class Lock(HassMultipleEntityExecutor):
    """Control entities of type lock."""

    entity_ids: Annotated[list[str], Field(
        description="List of entity IDs of the locks to control")]
    action: Annotated[Literal["lock", "unlock"], Field(
        description="Action to perform on the locks. Valid actions are 'lock' and 'unlock'")]

    def get_domain(self) -> str:
        """Return the domain of the entity."""
        return "lock"


class Cover(HassMultipleEntityExecutor):
    """Control entities of type cover, such as windows, garage doors, blinds, etc."""

    entity_ids: Annotated[list[str], Field(
        description="List of entity IDs of the covers to control")]
    action: Annotated[Literal["open", "close"], Field(
        description="Action to perform on the covers. Valid actions are 'open' and 'close'")]

    def get_domain(self) -> str:
        """Return the domain of the entity."""
        return "cover"


class Fan(HassMultipleEntityExecutor):
    """Control entities of type fan."""

    entity_ids: Annotated[list[str], Field(
        description="List of entity IDs of the fans to control")]
    action: Annotated[Literal["turn_on", "turn_off", "toggle", "increase_speed", "decrease_speed"], Field(
        description="Action to perform on the fans. Valid actions are 'turn_on', 'turn_off', 'toggle', 'increase_speed', and 'decrease_speed'")]

    def get_domain(self) -> str:
        """Return the domain of the entity."""
        return "fan"


class Vacuum(HassMultipleEntityExecutor):
    """Control entities of type vacuum."""

    entity_ids: Annotated[list[str], Field(
        description="List of entity IDs of the vacuums to control")]
    action: Annotated[Literal["start", "stop", "return_to_base", "locate", "pause", "turn_on", "turn_off", "toggle"],
                      Field(description="Action to perform on the vacuums. Valid actions are 'start', 'stop', 'return_to_base', 'locate', 'pause', 'turn_on', 'turn_off', and 'toggle'")]

    def get_domain(self) -> str:
        """Return the domain of the entity."""
        return "vacuum"


class Automation(HassMultipleEntityExecutor):
    """Control entities of type automation."""

    entity_ids: Annotated[list[str], Field(
        description="List of entity IDs of the automations to trigger")]
    action: Annotated[Literal["trigger", "turn_on", "turn_off"], Field(
        description="Action to perform on the automations. Valid actions are 'trigger', 'turn_on', and 'turn_off'")]

    def get_domain(self) -> str:
        """Return the domain of the entity."""
        return "automation"


class Scene(HassSingleEntityExecutor):
    """Sets the scene specified by the entity ID."""

    entity_id: Annotated[str, Field("Entity ID of the scene to set")]

    def get_domain(self) -> str:
        """Return the domain of the entity."""
        return "scene"

    async def on_execute(self) -> bool:
        """Override default behavior."""

        result = await HomeAssistantService.async_call_service([self.corrected_entity_id()], self.domain, "turn_on")
        return result.success


class Script(HassSingleEntityExecutor):
    """Runs the script specified by the entity ID."""

    entity_id: Annotated[str, Field("Entity ID of the script to run")]

    def get_domain(self) -> str:
        """Return the domain of the entity."""
        return "script"

    async def on_execute(self) -> bool:
        """Override default behavior."""
        result = await HomeAssistantService.async_call_service([self.corrected_entity_id()], self.domain, "turn_on")
        return result.success
