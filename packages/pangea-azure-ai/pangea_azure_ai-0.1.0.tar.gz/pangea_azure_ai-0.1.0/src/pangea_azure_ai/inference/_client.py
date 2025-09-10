from __future__ import annotations

from collections.abc import Iterable, Mapping, MutableMapping, Sequence

from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference import models as _models
from azure.core.credentials import AzureKeyCredential, TokenCredential
from pangea.services import AIGuard
from pangea.services.ai_guard import Message as PangeaMessage
from pangea.services.ai_guard import PromptMessage
from typing_extensions import IO, Any, Dict, List, Literal, Optional, Union, overload, override

from pangea_azure_ai.errors import PangeaAIGuardBlockedError

JSON = MutableMapping[str, Any]
_Unset: Any = object()

ChatRequestMessageLike = (
    _models.AssistantMessage
    | _models.DeveloperMessage
    | _models.SystemMessage
    | _models.ToolMessage
    | _models.UserMessage
)


def normalize_messages(
    messages: Sequence[_models.ChatRequestMessage] | Sequence[Mapping[str, Any]],
) -> list[ChatRequestMessageLike]:
    result: list[ChatRequestMessageLike] = []

    for message in messages:
        if not isinstance(message, Mapping):
            result.append(message)
            continue

        if message["role"] == "assistant":
            result.append(_models.AssistantMessage(content=message["content"]))
        elif message["role"] == "developer":
            result.append(_models.DeveloperMessage(content=message["content"]))
        elif message["role"] == "system":
            result.append(_models.SystemMessage(content=message["content"]))
        elif message["role"] == "tool":
            result.append(_models.ToolMessage(content=message["content"], tool_call_id=message["tool_call_id"]))
        elif message["role"] == "user":
            result.append(_models.UserMessage(content=message["content"]))
        else:
            raise ValueError(f"Unknown message role: {message['role']}")

    return result


def normalize_content(content: str | Sequence[_models.ContentItem] | None) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, Sequence):
        return "\n".join([item.text for item in content if isinstance(item, _models.TextContentItem)])
    raise ValueError(f"Unknown content type: {type(content)}")


def to_azure_messages(messages: Sequence[PromptMessage]) -> list[_models.ChatRequestMessage]:
    return [_models.ChatRequestMessage(**message.model_dump()) for message in messages]


class PangeaChatCompletionsClient(ChatCompletionsClient):
    ai_guard_client: AIGuard
    pangea_input_recipe: str | None = None
    pangea_output_recipe: str | None = None

    def __init__(
        self,
        endpoint: str,
        credential: Union[AzureKeyCredential, TokenCredential],
        *,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[Union[Literal["text", "json_object"], _models.JsonSchemaFormat]] = None,
        stop: Optional[List[str]] = None,
        tools: Optional[List[_models.ChatCompletionsToolDefinition]] = None,
        tool_choice: Optional[
            Union[str, _models.ChatCompletionsToolChoicePreset, _models.ChatCompletionsNamedToolChoice]
        ] = None,
        seed: Optional[int] = None,
        model: Optional[str] = None,
        model_extras: Optional[Dict[str, Any]] = None,
        # Pangea
        pangea_api_key: str,
        pangea_input_recipe: Optional[str] = None,
        pangea_output_recipe: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            endpoint=endpoint,
            credential=credential,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            response_format=response_format,
            stop=stop,
            tools=tools,
            tool_choice=tool_choice,
            seed=seed,
            model=model,
            model_extras=model_extras,
            **kwargs,
        )
        self.ai_guard_client = AIGuard(token=pangea_api_key)
        self.pangea_input_recipe = pangea_input_recipe
        self.pangea_output_recipe = pangea_output_recipe

    @overload
    def complete(
        self,
        *,
        messages: Union[List[_models.ChatRequestMessage], List[Dict[str, Any]]],
        stream: Literal[False] = False,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[Union[Literal["text", "json_object"], _models.JsonSchemaFormat]] = None,
        stop: Optional[List[str]] = None,
        tools: Optional[List[_models.ChatCompletionsToolDefinition]] = None,
        tool_choice: Optional[
            Union[str, _models.ChatCompletionsToolChoicePreset, _models.ChatCompletionsNamedToolChoice]
        ] = None,
        seed: Optional[int] = None,
        model: Optional[str] = None,
        model_extras: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> _models.ChatCompletions: ...

    @overload
    def complete(
        self,
        *,
        messages: Union[List[_models.ChatRequestMessage], List[Dict[str, Any]]],
        stream: Literal[True],
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[Union[Literal["text", "json_object"], _models.JsonSchemaFormat]] = None,
        stop: Optional[List[str]] = None,
        tools: Optional[List[_models.ChatCompletionsToolDefinition]] = None,
        tool_choice: Optional[
            Union[str, _models.ChatCompletionsToolChoicePreset, _models.ChatCompletionsNamedToolChoice]
        ] = None,
        seed: Optional[int] = None,
        model: Optional[str] = None,
        model_extras: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Iterable[_models.StreamingChatCompletionsUpdate]: ...

    @overload
    def complete(
        self,
        *,
        messages: Union[List[_models.ChatRequestMessage], List[Dict[str, Any]]],
        stream: Optional[bool] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[Union[Literal["text", "json_object"], _models.JsonSchemaFormat]] = None,
        stop: Optional[List[str]] = None,
        tools: Optional[List[_models.ChatCompletionsToolDefinition]] = None,
        tool_choice: Optional[
            Union[str, _models.ChatCompletionsToolChoicePreset, _models.ChatCompletionsNamedToolChoice]
        ] = None,
        seed: Optional[int] = None,
        model: Optional[str] = None,
        model_extras: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Union[Iterable[_models.StreamingChatCompletionsUpdate], _models.ChatCompletions]:
        """Gets chat completions for the provided chat messages.
        Completions support a wide variety of tasks and generate text that continues from or
        "completes" provided prompt data. The method makes a REST API call to the `/chat/completions` route
        on the given endpoint.
        When using this method with `stream=True`, the response is streamed
        back to the client. Iterate over the resulting StreamingChatCompletions
        object to get content updates as they arrive. By default, the response is a ChatCompletions object
        (non-streaming).

        :keyword messages: The collection of context messages associated with this chat completions
         request.
         Typical usage begins with a chat message for the System role that provides instructions for
         the behavior of the assistant, followed by alternating messages between the User and
         Assistant roles. Required.
        :paramtype messages: list[~azure.ai.inference.models.ChatRequestMessage] or list[dict[str, Any]]
        :keyword stream: A value indicating whether chat completions should be streamed for this request.
         Default value is False. If streaming is enabled, the response will be a StreamingChatCompletions.
         Otherwise the response will be a ChatCompletions.
        :paramtype stream: bool
        :keyword frequency_penalty: A value that influences the probability of generated tokens
         appearing based on their cumulative frequency in generated text.
         Positive values will make tokens less likely to appear as their frequency increases and
         decrease the likelihood of the model repeating the same statements verbatim.
         Supported range is [-2, 2].
         Default value is None.
        :paramtype frequency_penalty: float
        :keyword presence_penalty: A value that influences the probability of generated tokens
         appearing based on their existing
         presence in generated text.
         Positive values will make tokens less likely to appear when they already exist and increase
         the model's likelihood to output new topics.
         Supported range is [-2, 2].
         Default value is None.
        :paramtype presence_penalty: float
        :keyword temperature: The sampling temperature to use that controls the apparent creativity of
         generated completions.
         Higher values will make output more random while lower values will make results more focused
         and deterministic.
         It is not recommended to modify temperature and top_p for the same completions request as the
         interaction of these two settings is difficult to predict.
         Supported range is [0, 1].
         Default value is None.
        :paramtype temperature: float
        :keyword top_p: An alternative to sampling with temperature called nucleus sampling. This value
         causes the
         model to consider the results of tokens with the provided probability mass. As an example, a
         value of 0.15 will cause only the tokens comprising the top 15% of probability mass to be
         considered.
         It is not recommended to modify temperature and top_p for the same completions request as the
         interaction of these two settings is difficult to predict.
         Supported range is [0, 1].
         Default value is None.
        :paramtype top_p: float
        :keyword max_tokens: The maximum number of tokens to generate. Default value is None.
        :paramtype max_tokens: int
        :keyword response_format: The format that the AI model must output. AI chat completions models typically output
         unformatted text by default. This is equivalent to setting "text" as the response_format.
         To output JSON format, without adhering to any schema, set to "json_object".
         To output JSON format adhering to a provided schema, set this to an object of the class
         ~azure.ai.inference.models.JsonSchemaFormat. Default value is None.
        :paramtype response_format: Union[Literal['text', 'json_object'], ~azure.ai.inference.models.JsonSchemaFormat]
        :keyword stop: A collection of textual sequences that will end completions generation. Default
         value is None.
        :paramtype stop: list[str]
        :keyword tools: The available tool definitions that the chat completions request can use,
         including caller-defined functions. Default value is None.
        :paramtype tools: list[~azure.ai.inference.models.ChatCompletionsToolDefinition]
        :keyword tool_choice: If specified, the model will configure which of the provided tools it can
         use for the chat completions response. Is either a Union[str,
         "_models.ChatCompletionsToolChoicePreset"] type or a ChatCompletionsNamedToolChoice type.
         Default value is None.
        :paramtype tool_choice: str or ~azure.ai.inference.models.ChatCompletionsToolChoicePreset or
         ~azure.ai.inference.models.ChatCompletionsNamedToolChoice
        :keyword seed: If specified, the system will make a best effort to sample deterministically
         such that repeated requests with the
         same seed and parameters should return the same result. Determinism is not guaranteed.
         Default value is None.
        :paramtype seed: int
        :keyword model: ID of the specific AI model to use, if more than one model is available on the
         endpoint. Default value is None.
        :paramtype model: str
        :keyword model_extras: Additional, model-specific parameters that are not in the
         standard request payload. They will be added as-is to the root of the JSON in the request body.
         How the service handles these extra parameters depends on the value of the
         ``extra-parameters`` request header. Default value is None.
        :paramtype model_extras: dict[str, Any]
        :return: ChatCompletions for non-streaming, or Iterable[StreamingChatCompletionsUpdate] for streaming.
        :rtype: ~azure.ai.inference.models.ChatCompletions or ~azure.ai.inference.models.StreamingChatCompletions
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def complete(
        self,
        body: JSON,
        *,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> Union[Iterable[_models.StreamingChatCompletionsUpdate], _models.ChatCompletions]:
        """Gets chat completions for the provided chat messages.
        Completions support a wide variety of tasks and generate text that continues from or
        "completes" provided prompt data.

        :param body: An object of type MutableMapping[str, Any], such as a dictionary, that
         specifies the full request payload. Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: ChatCompletions for non-streaming, or Iterable[StreamingChatCompletionsUpdate] for streaming.
        :rtype: ~azure.ai.inference.models.ChatCompletions or ~azure.ai.inference.models.StreamingChatCompletions
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def complete(
        self,
        body: IO[bytes],
        *,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> Union[Iterable[_models.StreamingChatCompletionsUpdate], _models.ChatCompletions]:
        """Gets chat completions for the provided chat messages.
        Completions support a wide variety of tasks and generate text that continues from or
        "completes" provided prompt data.

        :param body: Specifies the full request payload. Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: ChatCompletions for non-streaming, or Iterable[StreamingChatCompletionsUpdate] for streaming.
        :rtype: ~azure.ai.inference.models.ChatCompletions or ~azure.ai.inference.models.StreamingChatCompletions
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @override
    def complete(
        self,
        body: Union[JSON, IO[bytes]] = _Unset,
        *,
        messages: Union[List[_models.ChatRequestMessage], List[Dict[str, Any]]] = _Unset,
        stream: Optional[bool] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[Union[Literal["text", "json_object"], _models.JsonSchemaFormat]] = None,
        stop: Optional[List[str]] = None,
        tools: Optional[List[_models.ChatCompletionsToolDefinition]] = None,
        tool_choice: Optional[
            Union[str, _models.ChatCompletionsToolChoicePreset, _models.ChatCompletionsNamedToolChoice]
        ] = None,
        seed: Optional[int] = None,
        model: Optional[str] = None,
        model_extras: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Union[Iterable[_models.StreamingChatCompletionsUpdate], _models.ChatCompletions]:
        """Gets chat completions for the provided chat messages.
        Completions support a wide variety of tasks and generate text that continues from or
        "completes" provided prompt data. When using this method with `stream=True`, the response is streamed
        back to the client. Iterate over the resulting :class:`~azure.ai.inference.models.StreamingChatCompletions`
        object to get content updates as they arrive.

        :param body: Is either a MutableMapping[str, Any] type (like a dictionary) or a IO[bytes] type
         that specifies the full request payload. Required.
        :type body: JSON or IO[bytes]
        :keyword messages: The collection of context messages associated with this chat completions
         request.
         Typical usage begins with a chat message for the System role that provides instructions for
         the behavior of the assistant, followed by alternating messages between the User and
         Assistant roles. Required.
        :paramtype messages: list[~azure.ai.inference.models.ChatRequestMessage] or list[dict[str, Any]]
        :keyword stream: A value indicating whether chat completions should be streamed for this request.
         Default value is False. If streaming is enabled, the response will be a StreamingChatCompletions.
         Otherwise the response will be a ChatCompletions.
        :paramtype stream: bool
        :keyword frequency_penalty: A value that influences the probability of generated tokens
         appearing based on their cumulative frequency in generated text.
         Positive values will make tokens less likely to appear as their frequency increases and
         decrease the likelihood of the model repeating the same statements verbatim.
         Supported range is [-2, 2].
         Default value is None.
        :paramtype frequency_penalty: float
        :keyword presence_penalty: A value that influences the probability of generated tokens
         appearing based on their existing
         presence in generated text.
         Positive values will make tokens less likely to appear when they already exist and increase
         the model's likelihood to output new topics.
         Supported range is [-2, 2].
         Default value is None.
        :paramtype presence_penalty: float
        :keyword temperature: The sampling temperature to use that controls the apparent creativity of
         generated completions.
         Higher values will make output more random while lower values will make results more focused
         and deterministic.
         It is not recommended to modify temperature and top_p for the same completions request as the
         interaction of these two settings is difficult to predict.
         Supported range is [0, 1].
         Default value is None.
        :paramtype temperature: float
        :keyword top_p: An alternative to sampling with temperature called nucleus sampling. This value
         causes the
         model to consider the results of tokens with the provided probability mass. As an example, a
         value of 0.15 will cause only the tokens comprising the top 15% of probability mass to be
         considered.
         It is not recommended to modify temperature and top_p for the same completions request as the
         interaction of these two settings is difficult to predict.
         Supported range is [0, 1].
         Default value is None.
        :paramtype top_p: float
        :keyword max_tokens: The maximum number of tokens to generate. Default value is None.
        :paramtype max_tokens: int
        :keyword response_format: The format that the AI model must output. AI chat completions models typically output
         unformatted text by default. This is equivalent to setting "text" as the response_format.
         To output JSON format, without adhering to any schema, set to "json_object".
         To output JSON format adhering to a provided schema, set this to an object of the class
         ~azure.ai.inference.models.JsonSchemaFormat. Default value is None.
        :paramtype response_format: Union[Literal['text', 'json_object'], ~azure.ai.inference.models.JsonSchemaFormat]
        :keyword stop: A collection of textual sequences that will end completions generation. Default
         value is None.
        :paramtype stop: list[str]
        :keyword tools: The available tool definitions that the chat completions request can use,
         including caller-defined functions. Default value is None.
        :paramtype tools: list[~azure.ai.inference.models.ChatCompletionsToolDefinition]
        :keyword tool_choice: If specified, the model will configure which of the provided tools it can
         use for the chat completions response. Is either a Union[str,
         "_models.ChatCompletionsToolChoicePreset"] type or a ChatCompletionsNamedToolChoice type.
         Default value is None.
        :paramtype tool_choice: str or ~azure.ai.inference.models.ChatCompletionsToolChoicePreset or
         ~azure.ai.inference.models.ChatCompletionsNamedToolChoice
        :keyword seed: If specified, the system will make a best effort to sample deterministically
         such that repeated requests with the
         same seed and parameters should return the same result. Determinism is not guaranteed.
         Default value is None.
        :paramtype seed: int
        :keyword model: ID of the specific AI model to use, if more than one model is available on the
         endpoint. Default value is None.
        :paramtype model: str
        :keyword model_extras: Additional, model-specific parameters that are not in the
         standard request payload. They will be added as-is to the root of the JSON in the request body.
         How the service handles these extra parameters depends on the value of the
         ``extra-parameters`` request header. Default value is None.
        :paramtype model_extras: dict[str, Any]
        :return: ChatCompletions for non-streaming, or Iterable[StreamingChatCompletionsUpdate] for streaming.
        :rtype: ~azure.ai.inference.models.ChatCompletions or ~azure.ai.inference.models.StreamingChatCompletions
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        if stream:
            return super().complete(
                body=body,
                messages=messages,
                stream=stream,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens,
                response_format=response_format,
                stop=stop,
                tools=tools,
                tool_choice=tool_choice,
                seed=seed,
                model=model,
                model_extras=model_extras,
                **kwargs,
            )

        if messages is _Unset:
            raise TypeError("missing required argument: messages")

        norm_messages = normalize_messages(messages)
        pangea_messages = [
            PangeaMessage(role=message.role, content=normalize_content(message.content)) for message in norm_messages
        ]

        guard_input_response = self.ai_guard_client.guard_text(
            messages=pangea_messages, recipe=self.pangea_input_recipe
        )

        assert guard_input_response.result is not None

        if guard_input_response.result.blocked:
            raise PangeaAIGuardBlockedError()

        if guard_input_response.result.transformed and guard_input_response.result.prompt_messages is not None:
            messages = to_azure_messages(guard_input_response.result.prompt_messages)

        azure_response = super().complete(
            # Exclude `body` because our `_Unset` is different from the one used
            # by the super class. We want `messages` to be the source of truth
            # anyways.
            # body=body,
            messages=messages,
            stream=stream,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            response_format=response_format,
            stop=stop,
            tools=tools,
            tool_choice=tool_choice,
            seed=seed,
            model=model,
            model_extras=model_extras,
            **kwargs,
        )

        if not isinstance(azure_response, _models.ChatCompletions):
            return azure_response

        guard_output_response = self.ai_guard_client.guard_text(
            messages=pangea_messages
            + [PangeaMessage(role="assistant", content=azure_response.choices[0].message.content)],
            recipe=self.pangea_output_recipe,
        )

        assert guard_output_response.result is not None

        if guard_output_response.result.blocked:
            raise PangeaAIGuardBlockedError()

        if guard_output_response.result.transformed and guard_output_response.result.prompt_messages is not None:
            azure_response.choices[0].message.content = guard_output_response.result.prompt_messages[-1].content

        return azure_response
