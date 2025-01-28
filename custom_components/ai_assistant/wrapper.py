"""This module contains the OpenAIWrapper class which is a wrapper around the OpenAI API client.

The wrapper adds re-asking logic. If the LLM returns validation errors, the wrapper re-asks the LLM to correct the errors.
"""
from abc import abstractmethod

from instructor.dsl.parallel import handle_parallel_model, ParallelModel
from instructor.utils import update_total_usage

from openai import AsyncOpenAI
from openai.types.completion import CompletionUsage
from openai.types.chat import ChatCompletion

from pydantic import BaseModel, ValidationError

from tenacity import AsyncRetrying, stop_after_attempt
from typing import TypeVar
from collections.abc import Iterable

from .const import LOGGER


class Executor(BaseModel):
    """Base class for all executors. All executors must inherit from this class.

    Attributes:
        _tool_call_id (str): The ID of the tool call

    Note:
        This class overrides __eq__ and __hash__ methods to remove the _tool_call_id field from being used for hashing and equality checks.
        This is done so that two executors are considered equal if all their fields except _tool_call_id are equal.
        The OpenAIWrapper class uses this to maintain a registry of tool calls and de-duplicate them.

    """

    _tool_call_id: str

    async def execute(self):
        """Call :meth:`on_execute' and return a message from the role 'tool' to send to the LLM."""
        outcome = await self.on_execute()
        if outcome:
            return {
                "role": "tool",
                "tool_call_id": self._tool_call_id,
                "name": self.__class__.__name__,
                "content": "Success"
            }
        else:
            return {
                "role": "tool",
                "tool_call_id": self._tool_call_id,
                "name": self.__class__.__name__,
                "content": "Failed"
            }

    @abstractmethod
    async def on_execute(self) -> bool:
        """Execute the tool and return True if successful, False otherwise."""
        pass

    def __eq__(self, value: object) -> bool:
        """Override the default Equals behavior."""
        if not isinstance(value, Executor):
            return False
        return self.model_dump(exclude={"_tool_call_id"}) == value.model_dump(exclude={"_tool_call_id"})

    def __hash__(self) -> int:
        """Override the default hash behavior."""
        return hash(tuple(self.model_dump(exclude={"_tool_call_id"}).items()))


T = TypeVar('T', bound=Executor)


class OpenAIWrapper:
    """A wrapper around the OpenAI API client that adds re-asking logic for validation errors.

    This class interacts with the OpenAI API to create chat completions and handles validation errors by re-asking the LLM to correct them.
    """

    def __init__(self, client: AsyncOpenAI):
        """Initialize the OpenAIWrapper with an OpenAI API client.

        Args:
            client (AsyncOpenAI): The OpenAI API client to use for making requests.

        """
        self.client = client

    async def create(self, model: str, messages: list[dict], response_model: Iterable[type[T]], max_retries: int | AsyncRetrying = 1, **kwargs) -> Iterable[type[T]]:
        """Create a chat completion with the specified model and messages, handling validation errors by re-asking the LLM.

        Args:
            model (str): The model to use for the chat completion.
            messages (list[dict]): The messages to send to the LLM.
            response_model (Iterable[type[T]]): The response models to validate the LLM's output.
            max_retries (int | AsyncRetrying): The maximum number of retries or a tenacity.AsyncRetrying object.
            **kwargs: Additional keyword arguments to pass to the OpenAI API client.

        Returns:
            Iterable[type[T]]: The validated tool calls returned by the LLM.

        """
        # Generate tools from response models specified
        tools = handle_parallel_model(response_model)
        LOGGER.debug("Tools: %s\n", tools)

        # Maintain a registry of tools
        tool_registry = ParallelModel(response_model)

        # Keep track of token usage
        total_token_usage = CompletionUsage(
            completion_tokens=0, prompt_tokens=0, total_tokens=0)

        if isinstance(max_retries, int):
            LOGGER.debug("max_retries: %s", max_retries)
            max_retries = AsyncRetrying(
                stop=stop_after_attempt(max_retries),
            )
        if not isinstance(max_retries, AsyncRetrying):
            raise TypeError(
                "max_retries must be an int or a `tenacity.AsyncRetrying` object")

        response = None
        tool_calls: Iterable[type[T]] = []

        async for attempt in max_retries:
            LOGGER.debug(f"Retrying, attempt: {
                attempt.retry_state.attempt_number}, message: {messages}")
            with attempt:
                try:
                    response: ChatCompletion = await self.client.chat.completions.create(model=model, messages=messages, tools=tools, tool_choice="auto", **kwargs)
                except Exception as e:
                    LOGGER.error("Error: %s", e)
                    raise e
                response = update_total_usage(response, total_token_usage)
                LOGGER.debug("Response: %s\n", response)
                valid_models, validation_errors = await self.process_response_async(response, tool_registry)

                if len(valid_models) > 0:
                    # De-duplicate tool calls. Since we are re-asking the LLM to correct validation errors, there's no guarantee that it will return all the tool calls or only the ones with errors.
                    # So, we need to keep track of all the tool calls returned by the LLM and de-duplicate them ourselves.
                    for v in valid_models:
                        if v in tool_calls:
                            v_i = tool_calls.index(v)
                            tool_calls.pop(v_i)
                            tool_calls.append(v)
                        else:
                            tool_calls.append(v)

                if len(validation_errors) == 0:
                    break
                else:
                    reask_messages = self.reask_messages(
                        response, validation_errors)
                    messages.extend(reask_messages)
                    raise ValidationError(
                        "Validation errors found, retrying...")

        return tool_calls

    async def process_response_async(self, response: ChatCompletion, tool_registry: ParallelModel) -> tuple[list[type[T]], list[dict[str, ValidationError]]]:
        """Process the response from the OpenAI API asynchronously.

        Args:
            response (ChatCompletion): The response from the OpenAI API.
            tool_registry (ParallelModel): The registry of tools to validate the response.

        Returns:
            tuple[list[type[T]], list[dict[str, ValidationError]]]: A tuple containing a list of valid models and a list of validation errors.

        """
        valid_models: list[type[T]] = []
        validation_errors: list[dict[str, ValidationError]] = []

        for tool_call in response.choices[0].message.tool_calls:
            name = tool_call.function.name
            arguments = tool_call.function.arguments
            tool = tool_registry.registry[name]
            try:
                validated_model = tool.model_validate_json(arguments)
                validated_model._tool_call_id = tool_call.id
                valid_models.append(validated_model)
            except ValidationError as e:
                validation_errors.append({name: e})
            except Exception as e:
                LOGGER.error("Error while creating model: %s", e)

        return valid_models, validation_errors

    def reask_messages(self, response: ChatCompletion, errors: list[dict[str, ValidationError]]) -> list[dict]:
        """Generate re-ask messages based on validation errors.

        Args:
            response (ChatCompletion): The response from the OpenAI API.
            errors (list[dict[str, ValidationError]]): A list of validation errors.

        Returns:
            list[dict]: A list of messages to re-ask the LLM to correct the errors.

        """
        messages = []
        for tool_call in response.choices[0].message.tool_calls:
            name = tool_call.function.name
            for error in errors:
                if name in error:
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": name,
                            "content": f"Validation errors found. {self.construct_error_message_from_error(error.get(name))}. Please correct the errors on your own and try again. Do not ask the user for input."
                        }
                    )
        return messages

    def construct_error_message_from_error(self, error: ValidationError) -> str:
        """Construct an error message string from a ValidationError.

        Args:
            error (ValidationError): The validation error to process.

        Returns:
            str: A formatted error message string.

        """
        error_list = error.errors(
            include_url=False, include_input=False, include_context=False)
        error_message = ""
        for e in error_list:
            error_message += f"{e.get("msg")},"

        error_message = error_message.rstrip(",")
        return error_message
