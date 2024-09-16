"""Custom integration to integrate ai_assistant with Home Assistant. This agent utilizes the instructor library.

For more details about this integration, please refer to
https://github.com/hemanthpai/hass-ai-assistant
"""
from __future__ import annotations
from typing import Literal
from collections.abc import Iterable

import instructor.exceptions
from openai import OpenAI

from custom_components.ai_assistant.helpers import get_exposed_entities
from custom_components.ai_assistant.instructor_executor import ToolExecutor

from homeassistant.components import conversation
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import MATCH_ALL
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import TemplateError
from homeassistant.helpers import intent, template
from homeassistant.util import ulid

import instructor

from .hass import HomeAssistantServiceResult

from .instructor_tools import Light, Switch, Fan, Climate, Cover, CreateCalendarEvent, GetCalendarEvents, Automation, Scene, Script, Media, Lock, Vacuum

from .const import (
    CONF_CTX_SIZE, CONF_MAX_TOKENS, CONF_MODEL, CONF_PROMPT_SYSTEM, CONF_TEMPERATURE, CONF_TOP_P, DEFAULT_INSTRUCTOR_PROMPT_SYSTEM, LOGGER
)

from .helpers import system_message, user_message


class AIConversationInstructionAgent(conversation.AbstractConversationAgent):
    """Agent for handling AI conversation instructions in Home Assistant."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, client: OpenAI) -> None:
        """Initialize the AIConversationInstructionAgent.

        :param hass: Home Assistant instance.
        :param entry: Configuration entry.
        :param client: OpenAI client instance.
        """
        self.hass = hass
        self.entry = entry
        self.client = client
        self.history: dict[str, dict] = {}
        self.instructor_client = instructor.from_openai(
            client, mode=instructor.Mode.PARALLEL_TOOLS)

    @property
    def supported_languages(self) -> list[str] | Literal["*"]:
        """Return a list of supported languages."""
        return MATCH_ALL

    async def async_process(
        self, user_input: conversation.ConversationInput
    ) -> conversation.ConversationResult:
        """Process a sentence."""

        messages = []

        try:
            system_prompt = self._async_generate_prompt()
        except TemplateError as err:
            return self._handle_template_error(err, user_input.language, user_input.conversation_id)

        messages.append(
            system_message(system_prompt)
        )

        messages.append(
            user_message(user_input.text)
        )

        instructor_response = await self._query_instructor(messages)

        if instructor_response is None:
            result: list[HomeAssistantServiceResult] = []
            try:
                for response in instructor_response:
                    result.append(ToolExecutor.execute_tool(response))

            except Exception as err:
                LOGGER.error(
                    "Instructor likely did not pick the correct tool or the user request did not require a tool: %s", err)
                return self._handle_api_error(err, user_input.language, user_input.conversation_id)

        intent_response = self._generate_response_from_tool_call_results(
            result, user_input.language)

        return conversation.ConversationResult(
            response=intent_response, conversation_id=user_input.conversation_id
        )

    def _get_conversation_history(self, user_input: conversation.ConversationInput) -> tuple[str, list[dict]]:
        """Get conversation history or create a new conversation ID."""
        if user_input.conversation_id in self.history:
            conversation_id = user_input.conversation_id
            messages = self.history[conversation_id]
        else:
            conversation_id = ulid.ulid()
            messages = []
        return conversation_id, messages

    def _async_generate_prompt(self) -> str:
        """Generate a prompt for the user."""
        raw_system_prompt = self.entry.options.get(
            CONF_PROMPT_SYSTEM, DEFAULT_INSTRUCTOR_PROMPT_SYSTEM)
        exposed_entities = get_exposed_entities(self.hass)

        return template.Template(raw_system_prompt, self.hass).async_render(
            {
                "ha_name": self.hass.config.location_name,
                "exposed_entities": exposed_entities,
            },
            parse_result=False,
        )

    def _handle_template_error(self, err: TemplateError, language: str, conversation_id: str):
        """Handle template rendering errors."""
        LOGGER.error("Error rendering system prompt: %s", err)
        intent_response = intent.IntentResponse(language=language)
        intent_response.async_set_error(
            intent.IntentResponseErrorCode.UNKNOWN,
            "I had a problem with my system prompt, please check the logs for more information.",
        )
        intent_response.async_set_speech(
            "I'm sorry, I had a problem with my system prompt. Please check the logs for more information."
        )
        return conversation.ConversationResult(
            response=intent_response, conversation_id=conversation_id
        )

    async def _query_instructor(self, messages: list[dict]) -> list[dict]:
        """Query the API."""
        try:
            response = self.instructor_client.chat.completions.create(
                model=self.entry.options.get(CONF_MODEL),
                messages=messages,
                temperature=self.entry.options.get(CONF_TEMPERATURE),
                top_p=self.entry.options.get(CONF_TOP_P),
                max_retries=2,
                response_model=Iterable[Light | Switch | Fan | Climate | Cover | CreateCalendarEvent |
                                        GetCalendarEvents | Automation | Scene | Script | Media | Lock | Vacuum]
            )
            return response
        except Exception as err:
            LOGGER.error(
                "Error querying Open AI server through instructor: %s", err)
            return None

    async def _query(self, messages: list[dict]) -> list[dict]:
        """Query the API."""
        try:
            response = self.client.chat.completions.create(
                model=self.entry.options.get(CONF_MODEL),
                messages=messages,
                ctx_size=self.entry.options.get(CONF_CTX_SIZE),
                max_tokens=self.entry.options.get(CONF_MAX_TOKENS),
                temperature=self.entry.options.get(CONF_TEMPERATURE),
                top_p=self.entry.options.get(CONF_TOP_P),
            )
            return response
        except Exception as err:
            LOGGER.error("Error querying the Open AI server: %s", err)
            return None

    def _handle_api_error(self, err: Exception, language: str, conversation_id: str) -> conversation.ConversationResult:
        """Handle API errors."""
        LOGGER.error("API error: %s", err)
        intent_response = intent.IntentResponse(language=language)
        intent_response.async_set_error(
            intent.IntentResponseErrorCode.UNKNOWN,
            "There was an error communicating with the API.",
        )
        intent_response.async_set_speech(
            "I'm sorry, I couldn't process that request. There was an error communicating with the API."
        )
        return conversation.ConversationResult(
            response=intent_response, conversation_id=conversation_id
        )

    def _generate_response_from_tool_call_results(self, results: list[HomeAssistantServiceResult], language: str, ) -> intent.IntentResponse:
        """Generate a response from the results of tool calls."""
        error_message = ""
        success_count = 0
        error_count = 0
        intent_response = intent.IntentResponse(language=language)

        for result in results:
            if result.success:
                success_count += 1
            else:
                error_count += 1
                error_message += ", ".join(result.error)

        if success_count > 0 and error_count == 0:
            # No errors, all successful
            intent_response.async_set_speech("Done.")
        elif success_count > 0 and error_count > 0:
            # Some successful, some errors
            intent_response.async_set_speech(
                f"Done. But there were errors with the following entities: {error_message}")
        else:
            # All errors
            intent_response.async_set_error(
                intent.IntentResponseErrorCode.UNKNOWN,
                f"I'm sorry, I couldn't process that request. There was an error with the following entities: {
                    error_message}",
            )
            intent_response.async_set_speech(
                f"I'm sorry, I couldn't process that request. There was an error with the following entities: {error_message}")

        return intent_response
