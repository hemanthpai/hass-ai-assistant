"""This module contains classes for controlling various types of entities in Home Assistant."""

from typing import Annotated, Literal
from pydantic import Field

from ..hass import HomeAssistantService, HassMultipleEntityExecutor


class Light(HassMultipleEntityExecutor):
    """Control entities of type light."""

    entity_ids: Annotated[list[str], Field(
        description="List of entity IDs of the lights to control")]
    action: Annotated[Literal["turn_on", "turn_off", "toggle"], Field(
        description="Action to perform on the lights. Valid actions are 'turn_on', 'turn_off', and 'toggle'")]
    brightness: Annotated[int | None, Field(
        description="Brightness level of the lights. Only used if brightness needs to be increased or decreased", ge=0, le=100)] = None
    rgb_color: Annotated[list[int] | None, Field(
        description="RGB color of the lights. Only used if color needs to be changed. Color is represented as a list of 3 integers in the range 0-255")] = None
    temperature: Annotated[int | None, Field(
        description="Color temperature of the lights. Only used if color temperature needs to be changed. Color temperature is an integer in the range 2700 - 6500", ge=2700, le=6500)] = None

    async def on_execute(self) -> bool:
        """Execute the service call to control the lights."""
        data = {}
        if self.brightness is not None:
            data["brightness_pct"] = self.brightness
        if self.rgb_color is not None:
            data["rgb_color"] = self.rgb_color
        if self.temperature is not None:
            data["temperature"] = self.temperature
        result = await HomeAssistantService.async_call_service(
            self.corrected_entity_ids(), self.get_domain(), self.action, data)

        # TODO: What to do when the service call fails?
        return result.success

    def get_domain(self) -> str:
        """Return the domain of the entity."""
        return "light"


class Climate(HassMultipleEntityExecutor):
    """Control entities of type climate, such as thermostats, air conditioners, etc."""

    entity_ids: Annotated[list[str], Field(
        description="List of entity IDs of the climate devices to control")]
    hvac_mode: Annotated[Literal["off", "heat", "cool", "auto", "heat/cool"] | None, Field(
        description="HVAC mode to set the climate devices to. Valid HVAC modes are 'off', 'heat', 'cool', 'auto', and 'heat_cool'")] = None
    temperature: Annotated[float | None, Field(
        description="Temperature to set the climate devices to. Temperature is a float in the range 0-100", ge=0, le=100)] = None
    humidity: Annotated[float | None, Field(
        description="Humidity to set the climate devices to. Humidity is a float in the range 0-100", ge=0, le=100)] = None
    fan_mode: Annotated[Literal["auto", "on", "off", "low", "medium", "high"] | None, Field(
        description="Fan mode to set the climate devices to. Valid fan modes are 'auto', 'on', 'off', 'low', 'medium', and 'high'")] = None
    preset_mode: Annotated[Literal["none", "away", "home"] | None, Field(
        description="Preset mode to set the climate devices to. Valid preset modes are 'none', 'away', 'home', and 'sleep'")] = None

    def get_domain(self) -> str:
        """Return the domain of the entity."""
        return "climate"

    async def on_execute(self) -> bool:
        """Execute the service call to control the climate devices."""
        data = {}
        if self.hvac_mode is not None:
            data["hvac_mode"] = self.hvac_mode
        if self.temperature is not None:
            data["temperature"] = self.temperature
        if self.humidity is not None:
            data["humidity"] = self.humidity
        if self.fan_mode is not None:
            data["fan_mode"] = self.fan_mode
        if self.preset_mode is not None:
            data["preset_mode"] = self.preset_mode
        # TODO: Implement the service call for controlling climate devices
        return False


class Media(HassMultipleEntityExecutor):
    """Control entities of type media player, such as TVs, speakers, etc."""

    entity_ids: Annotated[list[str], Field(
        description="List of entity IDs of the media players to control")]
    action: Annotated[Literal["play", "pause", "stop", "next", "previous", "volume_up", "volume_down", "volume_mute", "turn_on", "turn_off", "toggle"],
                      Field(description="Action to perform on the media players. Valid actions are 'play', 'pause', 'stop', 'next', 'previous', 'volume_up', 'volume_down', 'volume_mute', 'turn_on', 'turn_off', and 'toggle'")]

    def get_domain(self) -> str:
        """Return the domain of the entity."""
        return "media_player"
