# phase2/sprint1/llm_client/openai_client.py

import json
import logging
import openai

from typing import List, Tuple, Union
from openai import OpenAI
from phase2.sprint1.llm_client.base_client import BaseLLMClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenAIClient(BaseLLMClient):
    def __init__(self, model: str, key_manager, max_retries=3):
        super().__init__(model, key_manager, max_retries)
        openai.api_key = self.key_manager.get_next_key()

    def generate(self, prompt: str, tools: List[dict]) -> Tuple[Union[str, None], str]:
        try:
            api_key = self.key_manager.get_next_key()

            openai_client = openai.OpenAI(api_key=api_key)

            response = openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that generates JSON responses according to the provided schema. If the user is just chatting, respond in a conversational manner.",
                    },
                    {
                        "role": "user",
                        "content": prompt
                    },
                ],
                tools=tools,
                tool_choice="auto",
                temperature=0.1,
            )

            if response.choices[0].message.tool_calls:
                function_call = response.choices[0].message.tool_calls[0]
                args_str = function_call.function.arguments
                try:
                    args = json.loads(args_str)
                    return args
                except Exception as e:
                    logger.error(f"Failed to parse function arguments: {args_str}, error: {e}")
                    return args_str
            else:
                return response.choices[0].message.content

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise ValueError(f"Failed to generate response: {e}")
