# AI Assistant

The AI Assistant integration adds a conversation agent, powered by a self hosted LLM, in Home Assistant.

## Requirements

This integration requires setting up [Functionary's][functionary] vLLM based inferencing server. Refer to their Setup section for instructions on how to get the inferencing server up and running. The recommended model to use is **meetkai/functionary-small-v3.2**.

Functionary was chosen because it's one of the best LLMs for tool calling. Check out [Berkeley's Function-Calling leaderboard][berkeley] for more information.

The integration can work with any inferencing server that offers an Open AI API endpoint and supports tool calling, in combination with a LLM that also supports tool calling. However, the integration has not yet been tested with such a setup. Support for this setup will be added in the future. The current priority is to add more functionality.

## Features

The assistant currently supports the following device types and operations:

- Light: turn on, turn off, set brightness, change color and temperature when the light supports it
- Switch: turn on, turn off
- Climate: set temperature, HVAC mode, fan mode, and control humidity
- Media Player: turn on, turn off, play, pause, stop, next/previous track, volume up/down/mute, set shuffle mode
- Cover: open, close
- Scene: set a scene
- Automation: turn on or off an existing automation
- Script: run an existing script
- Vacuum: start, stop, pause, send back to docking station
- Calendar: get agenda for the specified time frame (ex: today, tomorrow, this week, next week etc.), create events, find open time slots on the calendar

This integration is a work in progress and the list of features will continue to grow!

## Options

Options for AI Assistant can be set via the user interface, by taking the following steps:

- Browse to your Home Assistant instance.
- Go to Settings > Devices & Services.
- If multiple instances of AI Conversation are configured, choose the instance you want to configure.
- Select the integration, then select **_Configure_**.

#### Note:

HACS does not "configure" the integration for you, You must add AI Assistant after installing via HACS.

- Browse to your Home Assistant instance.
- Go to Settings > Devices & Services.
- In the bottom right corner, select the **_Add Integration_** button.
- From the list, select AI Assistant.
- Follow the instructions on screen to complete the setup.

#### General Settings

Settings relating to the integration itself.

| Option      | Description                                                               |
| ----------- | ------------------------------------------------------------------------- |
| API Timeout | The maximum amount of time to wait for a response from the API in seconds |

#### System Prompt

The starting text for the AI language model to generate new text from. This text can include information about your Home Assistant instance, devices, and areas and is written using Home Assistant Templating.

#### Model Configuration

The language model and additional parameters to fine tune the responses.

| Option         | Description                                                                                                                                                              |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Model          | The model used to generate response.                                                                                                                                     |
| Context Size   | Sets the size of the context window used to generate the next token.                                                                                                     |
| Maximum Tokens | The maximum number of words or “tokens” that the AI model should generate in its completion of the prompt.                                                               |
| Temperature    | The temperature of the model. A higher value (e.g., 0.95) will lead to more unexpected results, while a lower value (e.g. 0.5) will be more deterministic results.       |
| Top P          | Works together with top-k. A higher value (e.g., 0.95) will lead to more diverse text, while a lower value (e.g., 0.5) will generate more focused and conservative text. |

### Discussions

Discussions for this integration over on the [discussions][discussions] page

---

[ollamaconversation]: https://github.com/ej52/hass-ollama-conversation
[discussions]: https://github.com/hemanthpai/hass-ai-assistant/discussions/
[functionary]: https://github.com/MeetKai/functionary
[berkeley]: https://gorilla.cs.berkeley.edu/leaderboard.html
[homellm]: https://github.com/acon96/home-llm
