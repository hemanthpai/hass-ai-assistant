"""Custom integration to integrate ai_assistant with Home Assistant.

For more details about this integration, please refer to
https://github.com/hemanthpai/hass-ai-assistant
"""
from __future__ import annotations

from .agent import AIConversationAgent

from homeassistant.components import conversation
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import VllmApiClient
from .const import (
    DOMAIN, CONF_BASE_URL,
    CONF_TIMEOUT,
    DEFAULT_TIMEOUT
)
from .coordinator import AIConversationDataUpdateCoordinator
from .exceptions import (
    ApiClientError
)
from .hass_provider import HassContextFactory


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up AI Assistant using UI."""
    HassContextFactory.set_instance(hass)
    hass.data.setdefault(DOMAIN, {})
    client = VllmApiClient(
        base_url=entry.data[CONF_BASE_URL],
        timeout=entry.options.get(CONF_TIMEOUT, DEFAULT_TIMEOUT),
        session=async_get_clientsession(hass),
    )

    hass.data[DOMAIN][entry.entry_id] = coordinator = AIConversationDataUpdateCoordinator(
        hass,
        client,
    )
    # https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
    await coordinator.async_config_entry_first_refresh()

    try:
        response = await client.async_get_heartbeat()
        if not response:
            raise ApiClientError("Invalid vLLM server")
    except ApiClientError as err:
        raise ConfigEntryNotReady(err) from err

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    conversation.async_set_agent(
        hass, entry, AIConversationAgent(hass, entry, client))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload AI conversation."""
    conversation.async_unset_agent(hass, entry)
    return True


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload AI conversation."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
