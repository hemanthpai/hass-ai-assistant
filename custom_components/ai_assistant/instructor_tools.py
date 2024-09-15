"""This module defines various Pydantic models for controlling different types of entities.

In a home automation system, such as lights, switches, locks, covers, climate devices,
media players, fans, vacuums, scenes, scripts, automations, and calendar events.
"""

from typing import Annotated, Literal
from pydantic import BaseModel, Field


class Light(BaseModel):
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


class Switch(BaseModel):
    """Control entities of type switch."""

    entity_ids: Annotated[list[str], Field(
        description="List of entity IDs of the switches to control")]
    action: Annotated[Literal["turn_on", "turn_off", "toggle"], Field(
        description="Action to perform on the switches. Valid actions are 'turn_on', 'turn_off', and 'toggle'")]


class Lock(BaseModel):
    """Control entities of type lock."""

    entity_ids: Annotated[list[str], Field(
        description="List of entity IDs of the locks to control")]
    action: Annotated[Literal["lock", "unlock"], Field(
        description="Action to perform on the locks. Valid actions are 'lock' and 'unlock'")]


class Cover(BaseModel):
    """Control entities of type cover, such as windows, garage doors, blinds, etc."""

    entity_ids: Annotated[list[str], Field(
        description="List of entity IDs of the covers to control")]
    action: Annotated[Literal["open", "close"], Field(
        description="Action to perform on the covers. Valid actions are 'open' and 'close'")]


class Climate(BaseModel):
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


class Media(BaseModel):
    """Control entities of type media player, such as TVs, speakers, etc."""

    entity_ids: Annotated[list[str], Field(
        description="List of entity IDs of the media players to control")]
    action: Annotated[Literal["play", "pause", "stop", "next", "previous", "volume_up", "volume_down", "volume_mute", "turn_on", "turn_off", "toggle"],
                      Field(description="Action to perform on the media players. Valid actions are 'play', 'pause', 'stop', 'next', 'previous', 'volume_up', 'volume_down', 'volume_mute', 'turn_on', 'turn_off', and 'toggle'")]


class Fan(BaseModel):
    """Control entities of type fan."""

    entity_ids: Annotated[list[str], Field(
        description="List of entity IDs of the fans to control")]
    action: Annotated[Literal["turn_on", "turn_off", "toggle", "increase_speed", "decrease_speed"], Field(
        description="Action to perform on the fans. Valid actions are 'turn_on', 'turn_off', 'toggle', 'increase_speed', and 'decrease_speed'")]


class Vacuum(BaseModel):
    """Control entities of type vacuum."""

    entity_ids: Annotated[list[str], Field(
        description="List of entity IDs of the vacuums to control")]
    action: Annotated[Literal["start", "stop", "return_to_base", "locate", "pause", "turn_on", "turn_off", "toggle"],
                      Field(description="Action to perform on the vacuums. Valid actions are 'start', 'stop', 'return_to_base', 'locate', 'pause', 'turn_on', 'turn_off', and 'toggle'")]


class Scene(BaseModel):
    """Control entities of type scene."""

    entity_ids: Annotated[list[str], Field(
        description="List of entity IDs of the scenes to activate")]


class Script(BaseModel):
    """Control entities of type script."""

    entity_ids: Annotated[list[str], Field(
        description="List of entity IDs of the scripts to run")]


class Automation(BaseModel):
    """Control entities of type automation."""

    entity_ids: Annotated[list[str], Field(
        description="List of entity IDs of the automations to trigger")]
    action: Annotated[Literal["trigger", "turn_on", "turn_off"], Field(
        description="Action to perform on the automations. Valid actions are 'trigger', 'turn_on', and 'turn_off'")]


class CreateCalendarEvent(BaseModel):
    """Create an event on a calendar."""

    entity_id: Annotated[str, Field(
        description="Entity ID of the calendar to create the event on")]
    title: Annotated[str, Field(description="Title of the event to create")]
    start_time: Annotated[str, Field(
        description="Start time of the event to create. Specfied in the format YYYY-MM-DD HH:MM:SS")]
    end_time: Annotated[str, Field(
        description="End time of the event to create. Specfied in the format YYYY-MM-DD HH:MM:SS")]


class GetCalendarEvents(BaseModel):
    """Get events from a calendar."""

    entity_ids: Annotated[list[str], Field(
        description="Entity IDs of the calendars to get the events from")]
    start_time: Annotated[str, Field(
        description="Start time to get the events from. Specfied in the format YYYY-MM-DD HH:MM:SS")]
    end_time: Annotated[str, Field(
        description="End time to get the events from. Specfied in the format YYYY-MM-DD HH:MM:SS")]
