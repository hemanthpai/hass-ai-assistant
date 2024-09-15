"""This module contains the ToolExecutor class which is responsible for executing various Home Assistant tools."""

from .hass import HomeAssistantService, HomeAssistantServiceResult

from .instructor_tools import Automation, Climate, Cover, CreateCalendarEvent, Fan, GetCalendarEvents, Light, Media, Scene, Script, Switch, Lock, Vacuum


class ToolExecutor:
    """Executes various Home Assistant tools."""

    async def async_execute_tool(self, tool: any) -> HomeAssistantServiceResult:
        """Execute a given Home Assistant tool.

        Args:
            tool (any): The tool to be executed.

        Returns:
            HomeAssistantServiceResult: The result of the tool execution.

        """
        if (isinstance(tool, Light)):
            light: Light = tool
            self._prepend_entity_domain(light.entity_ids, "light")
            data = {}
            if light.brightness is not None:
                data["brightness"] = light.brightness
            if light.rgb_color is not None:
                data["rgb_color"] = light.rgb_color
            if light.temperature is not None:
                data["temperature"] = light.temperature
            result = await HomeAssistantService.async_call_service(
                light.entity_ids, "light", light.action, tool.data, data)
            return result
        elif (isinstance(tool, Switch)):
            switch: Switch = tool
            self._prepend_entity_domain(switch.entity_ids, "switch")
            result = await HomeAssistantService.async_call_service(
                switch.entity_ids, "switch", switch.action)
            return result
        elif (isinstance(tool, Lock)):
            lock: Lock = tool
            self._prepend_entity_domain(lock.entity_ids, "lock")
            result = await HomeAssistantService.async_call_service(
                lock.entity_ids, "lock", lock.action)
            return result
        elif (isinstance(tool, Cover)):
            cover: Cover = tool
            self._prepend_entity_domain(cover.entity_ids, "cover")
            result = await HomeAssistantService.async_call_service(
                cover.entity_ids, "cover", cover.action)
            return result
        elif (isinstance(tool, Climate)):
            climate: Climate = tool
            self._prepend_entity_domain(climate.entity_ids, "climate")
            data = {}
            if climate.hvac_mode is not None:
                data["hvac_mode"] = climate.hvac_mode
            if climate.temperature is not None:
                data["temperature"] = climate.temperature
            if climate.humidity is not None:
                data["humidity"] = climate.humidity
            if climate.fan_mode is not None:
                data["fan_mode"] = climate.fan_mode
            if climate.preset_mode is not None:
                data["preset_mode"] = climate.preset_mode
            # TODO: Implement the service call for controlling climate devices
            return HomeAssistantServiceResult(success=False)
        elif (isinstance(tool, Media)):
            media: Media = tool
            self._prepend_entity_domain(media.entity_ids, "media_player")
            data = {}
            # TODO: Implement the service call for controlling media players
            return HomeAssistantServiceResult(success=False)
        elif (isinstance(tool, Fan)):
            fan: Fan = tool
            self._prepend_entity_domain(fan.entity_ids, "fan")
            result = await HomeAssistantService.async_call_service(
                fan.entity_ids, "fan", fan.action)
            return result
        elif (isinstance(tool, Vacuum)):
            vacuum: Vacuum = tool
            self._prepend_entity_domain(vacuum.entity_ids, "vacuum")
            result = await HomeAssistantService.async_call_service(
                vacuum.entity_ids, "vacuum", vacuum.action)
            return result
        elif (isinstance(tool, Scene)):
            scene: Scene = tool
            self._prepend_entity_domain(scene.entity_ids, "scene")
            result = await HomeAssistantService.async_call_service(
                scene.entity_ids, "scene", "turn_on")
            return result
        elif (isinstance(tool, Script)):
            script: Script = tool
            self._prepend_entity_domain(script.entity_ids, "script")

            # TODO: Implement the service call for controlling scripts

            return HomeAssistantServiceResult(success=False)
        elif (isinstance(tool, Automation)):
            automation: Automation = tool
            self._prepend_entity_domain(automation.entity_ids, "automation")
            result = await HomeAssistantService.async_call_service(
                automation.entity_ids, "automation", automation.action)
            return result
        elif (isinstance(tool, CreateCalendarEvent)):
            calendar_event: CreateCalendarEvent = tool
            if "." not in calendar_event.entity_id:
                calendar_event.entity_id = f"calendar.{
                    calendar_event.entity_id}"
            result = await HomeAssistantService.async_create_calendar_event(
                calendar_event.entity_id, calendar_event.start_time, calendar_event.end_time, calendar_event.title)
        elif (isinstance(tool, GetCalendarEvents)):
            get_calendar_events: GetCalendarEvents = tool
            self._prepend_entity_domain(
                get_calendar_events.entity_ids, "calendar")
            result = await HomeAssistantService.async_get_calendar_events(
                get_calendar_events.entity_ids, get_calendar_events.start_time, get_calendar_events.end_time)
            return result
        else:
            return HomeAssistantServiceResult(success=False)

    def _prepend_entity_domain(self, entity_ids: list[str], domain: str):
        for entity_id in entity_ids:
            if "." not in entity_id:
                entity_ids.remove(entity_id)
                entity_ids.append(f"{domain}.{entity_id}")
