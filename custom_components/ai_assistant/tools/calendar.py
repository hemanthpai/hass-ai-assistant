"""This module contains classes for creating and retrieving calendar events using the Home Assistant API."""

from typing import Annotated

from pydantic import Field
from ..hass import HassSingleEntityExecutor

class CreateCalendarEvent(HassSingleEntityExecutor):
    """Create an event on a calendar."""

    entity_id: Annotated[str, Field(
        description="Entity ID of the calendar to create the event on")]
    title: Annotated[str, Field(description="Title of the event to create")]
    start_time: Annotated[str, Field(
        description="Start time of the event to create. Specfied in the format YYYY-MM-DD HH:MM:SS")]
    end_time: Annotated[str, Field(
        description="End time of the event to create. Specfied in the format YYYY-MM-DD HH:MM:SS")]


class GetCalendarEvents(HassSingleEntityExecutor):
    """Get events from a calendar."""

    entity_ids: Annotated[list[str], Field(
        description="Entity IDs of the calendars to get the events from")]
    start_time: Annotated[str, Field(
        description="Start time to get the events from. Specfied in the format YYYY-MM-DD HH:MM:SS")]
    end_time: Annotated[str, Field(
        description="End time to get the events from. Specfied in the format YYYY-MM-DD HH:MM:SS")]
