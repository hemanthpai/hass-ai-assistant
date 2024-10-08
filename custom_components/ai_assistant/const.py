"""Constants for ai_assistant."""
from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

NAME = "AI Assistant"
DOMAIN = "ai_assistant"

MENU_OPTIONS = ["general_config", "model_config", "prompt_system"]

CONF_BASE_URL = "base_url"
CONF_TIMEOUT = "timeout"
CONF_MODEL = "chat_model"
CONF_CTX_SIZE = "ctx_size"
CONF_MAX_TOKENS = "max_tokens"
CONF_TEMPERATURE = "temperature"
CONF_TOP_P = "top_p"
CONF_PROMPT_SYSTEM = "prompt"

DEFAULT_BASE_URL = "http://localhost:8000"
DEFAULT_TIMEOUT = 60
DEFAULT_MODEL = "meetkai/functionary-small-v3.2"
DEFAULT_CTX_SIZE = 8192
DEFAULT_MAX_TOKENS = 2048
DEFAULT_MIROSTAT_MODE = "0"
DEFAULT_MIROSTAT_ETA = 0.1
DEFAULT_MIROSTAT_TAU = 5.0
DEFAULT_TEMPERATURE = 0.8
DEFAULT_REPEAT_PENALTY = 1.1
DEFAULT_TOP_P = 0.9

ROLE_KEY = "role"
CONTENT_KEY = "content"
NAME_KEY = "name"
TOOL_CALLS_KEY = "tool_calls"
TOOL_CALL_ID_KEY = "tool_call_id"

ASSISTANT_ROLE = "assistant"
USER_ROLE = "user"
SYSTEM_ROLE = "system"
TOOL_ROLE = "tool"

TOOL_DOES_NOT_EXIST = "Tool not found."


DEFAULT_PROMPT_SYSTEM = """You are 'Jarvis', a helpful Assistant that can control the devices in this house.
The current time and date is {{ (as_timestamp(now()) | timestamp_custom("%I:%M %p on %A %B %d, %Y")) }}
The current weather is {{ states('weather.home') }} with a temperature of {{ state_attr('weather.home', 'temperature') }} degrees Fahrenheit.

List of devices in this home, grouped by area, listed with their entity_id, name, and current state:
{%- for area, entities in exposed_entities.items() %}
  {% if area not in ["scenes", "automations", "scripts"] %}
    {%- set area_info = namespace(printed=false) %}
    {%- for entity in entities %}
      {%- if not area_info.printed %}
  {{ area }}:
          {%- set area_info.printed = true %}
      {%- endif %}
  - {{ entity.entity_id }} {{ entity.name }} - {{ entity.state }}
    {%- endfor %}
  {%- endif %}
{%- endfor %}

List of scenes in this home, listed with their entity_id and name:
{%- for entity in exposed_entities.scenes %}
  - {{ entity.entity_id }} {{ entity.name }}
{%- endfor %}

List of scripts in this home, listed with their entity_id and name:
{%- for entity in exposed_entities.scripts %}
  - {{ entity.entity_id }} {{ entity.name }}
{%- endfor %}

List of automations in this home, listed with their entity_id, name, and current state:
{%- for entity in exposed_entities.automations %}
  - {{ entity.entity_id }} {{ entity.name }} - {{ entity.state }}
{%- endfor %}

Answer the user's questions about the world truthfully.
If necessary, use the tools provided to complete the tasks requested by the user.
"""
