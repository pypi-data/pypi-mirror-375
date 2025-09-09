# -*- coding: utf-8 -*-
from typing import cast

from pydantic import BaseModel, ConfigDict, Field
from sinapsis_chatbots_base.helpers.llm_keys import LLMChatKeys
from sinapsis_chatbots_base.helpers.postprocess_text import postprocess_text
from sinapsis_chatbots_base.helpers.tags import Tags
from sinapsis_chatbots_base.templates.llm_text_completion_base import LLMTextCompletionAttributes, LLMTextCompletionBase
from sinapsis_core.data_containers.data_packet import DataContainer, TextPacket
from sinapsis_core.template_base.base_models import TemplateAttributeType
from transformers import AutoProcessor, Llama4ForConditionalGeneration

LLama4TextToTextUIProperties = LLMTextCompletionBase.UIProperties
LLama4TextToTextUIProperties.tags.extend([Tags.CONVERSATIONAL, Tags.LLAMA, Tags.TEXT_TO_TEXT])


class LLamaMultiModalKeys(LLMChatKeys):
    """Keys for specific Llama format for chat template
    type (str): key for type
    text (str): key for text
    image (str): key for image
    video (str): key for video
    """

    type: str = "type"
    text: str = "text"
    image: str = "image"
    video: str = "video"


class Llama4ModelKwargs(BaseModel):
    """Defines and validates keyword arguments for loading a Llama 4 model.

    Attributes:
        torch_dtype (str | torch.dtype | None): The data type for the model's tensors
            (e.g., "auto", "float16"). Defaults to "auto".
        max_memory (dict | None): A dictionary mapping devices (e.g., "cpu", 0 for the
            first GPU) to their maximum memory allocation (e.g., "10GiB").
    """

    torch_dtype: str | None = "auto"
    max_memory: dict | None = None
    model_config = ConfigDict(extra="allow")


class LLama4TextToText(LLMTextCompletionBase):
    """Template for text-to-text chat processing using the
    LLama 4 model. This template provides support for text-to-text
    conversational chatbots and all the LLama4 models for Scout and Maverick versions.

    Usage example:

    agent:
      name: my_test_agent
    templates:
    - template_name: InputTemplate
      class_name: InputTemplate
      attributes: {}
    - template_name: LLama4
      class_name: LLama4TextToText
      template_input: InputTemplate
      attributes:
        llm_model_name: "meta-llama/Llama-4-Scout-17B-16E-Instruct"
        n_ctx: 9000
        role: assistant
        system_prompt: You are an AI and Python expert, and you should reason in every response you provide
        chat_format: chatml
        context_max_len: 6
        pattern: null
        keep_before: true
        device_map: auto
        max_new_tokens: 256
        hf_access_token: null
        extra_args:
          torch_dtype: auto
          max_memory:
            0: "8GiB"
            cpu: "10GiB"

    """

    UIProperties = LLama4TextToTextUIProperties

    class AttributesBaseModel(LLMTextCompletionAttributes):
        """Attributes for the template:
                llm_model_name (str): The name of the LLM model to use.
        n_ctx (int): Maximum context size for the model.
        role (Literal["system", "user", "assistant"]): The role in the conversation,
            such as "system", "user", or
            "assistant". Defaults to "assistant".
        prompt (str): A set of instructions provided to the LLM to guide how to respond.
            The default
            value is an empty string.
        system_prompt (str | None): The prompt that indicates the LLM how to behave
            (e.g. you are an expert on...)
        chat_format (str | None): The format for the chat messages
            (e.g., llama-2, chatml, etc.).
        context_max_len (int): The maximum length for the conversation context.
            The default value is 6.
        pattern (str | None): A regex pattern to match delimiters. The default value is
            `<|...|>` and `</...>`.
        keep_before (bool): If True, returns the portion before the first match;
            if False, returns the portion after the first match.
        device_map (str): The device where the model is loaded. Defaults to auto
        max_new_tokens (int): The maximum number of generated tokens
        hf_access_token (str | None): The huggingface access token necessary to use the models.

        """

        device_map: str = "auto"
        max_new_tokens: int = 256
        hf_access_token: str | None = None
        extra_args: Llama4ModelKwargs = Field(default_factory=Llama4ModelKwargs)

    def __init__(self, attributes: TemplateAttributeType) -> None:
        super().__init__(attributes)
        self.processor = AutoProcessor.from_pretrained(self.attributes.llm_model_name)

    def init_llm_model(self):
        """Uses LLama4ForConditionalGeneration to initialize
        a pretrained model with the corresponding memory.
        """
        model = Llama4ForConditionalGeneration.from_pretrained(
            self.attributes.llm_model_name,
            device_map=self.attributes.device_map,
            **self.attributes.extra_args.model_dump(exclude_none=True),
        )
        return model

    def reset_llm_state(self) -> None:
        self._clear_context()

    def infer(self, text: str | list) -> str | None:
        """
        Specific method to apply a chat template before using the get_response method

        Args:
            text (str | list): text to be processed by the llm
        Returns:
            str | None: If a response is generated by the llm, it returns the processed string
        """
        inputs = self.processor.apply_chat_template(
            text, add_generation_prompt=True, tokenize=True, return_dict=True, return_tensors="pt"
        ).to(self.llm.device)
        response = self.get_response(inputs)
        return response

    @staticmethod
    def process_packets(messages: list, container: DataContainer) -> list:
        """abstract method for processing extra packets in the DataContainer
        before passing the message to the llm"""
        _ = container
        return messages

    def generate_response(self, container: DataContainer) -> DataContainer:
        """Method that checks the container and depending on the type of
        packets inside, generates the necessary dictionaries to be passed
        to the model for response generation

        Args:
            container (DataContainer): Input DataContainer with packet or packets to be processed

        Returns:
            DataContainer: The DataContainer with a text response for each of the input text packets
        """
        message: list = []
        responses: list = []
        system_prompt_msg: dict = {}

        for text in container.texts:
            message = self.process_packets(message, container)
            message.append({LLamaMultiModalKeys.type: LLamaMultiModalKeys.text, LLamaMultiModalKeys.text: text.content})
            message_for_model = self.generate_dict_msg(LLMChatKeys.user_value, message)
            if self.system_prompt:
                prompt_message = [
                    {LLamaMultiModalKeys.type: LLamaMultiModalKeys.text, LLamaMultiModalKeys.text: self.system_prompt}
                ]
                system_prompt_msg = self.generate_dict_msg(LLMChatKeys.system_value, prompt_message)
            input_msg = [message_for_model, system_prompt_msg]
            response = self.infer(input_msg)
            if response:
                responses.append(TextPacket(content=response))
        container.texts.extend(responses)
        return container

    def get_response(self, input_message: str | list | dict) -> str | None:
        """Specific method to get the response using the generate method for the llm model.
        It unwraps the input message that comes as a dictionary, and returns the response as a dictionary,
        to be post-processed and returns a string with the model response.

        Args:
            input_message (str | list | dict): Dictionary with the input message to be passed to the
            generate method
        Returns:
            the response as a string after being post-processed.
        """
        input_message = cast(dict, input_message)
        response = self.llm.generate(**input_message, max_new_tokens=self.attributes.max_new_tokens)
        input_len = input_message.get("input_ids", None)
        if input_len is not None:
            input_len = input_len.shape[-1]
        new_tokens = response[:, input_len:]
        response = self.processor.batch_decode(new_tokens)[0]
        if response:
            response = postprocess_text(str(response), self.attributes.pattern, self.attributes.keep_before)
            return response
        return None
