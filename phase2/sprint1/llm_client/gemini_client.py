# phase2/sprint1/llm_client/gemini_client.py

import os
import json
import logging

from google import genai
from google.genai import types
from typing import List, Tuple, Union
from phase2.sprint1.llm_client.base_client import BaseLLMClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiClient(BaseLLMClient):
    def __init__(self, model, key_manager, max_retries=3):
        super().__init__(model, key_manager, max_retries)

    def generate(self, prompt: str, tools: List[dict]) -> Tuple[Union[str, None], str]:
        try:
            api_key = self.key_manager.get_next_key()
            genai_client = genai.Client(api_key=api_key)

            response = genai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that generates JSON responses according to the provided schema. If the user is just chatting, respond in a conversational manner.",
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                tools=tools,
                tool_choice="auto",
            )
            tool_call = response.choices[0].message.tool_calls[0]
            return tool_call.function.arguments
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise ValueError(f"Failed to generate response: {e}")
