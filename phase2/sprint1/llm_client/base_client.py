# phase2/sprint1/llm_client/base_client.py

import re
import json
import logging

from typing import List
from pydantic import ValidationError

logging.basicConfig(
    filename='llm_client.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BaseLLMClient:
    def __init__(self, model: str, key_manager, max_retries=3):
        self.model = model
        self.key_manager = key_manager
        self.max_retries = max_retries
        self.success_count = 0
        self.total_count = 0

    def generate(self, prompt: str, tools: List[dict]):
        """
        Provider-specific implementation for generating responses.
        """
        raise NotImplementedError("Subclasses should implement this method.")
        
    def parse_and_validate(self, text: str, schema):
        """
        Parses a JSON string and validates it against the provided Pydantic schema.
        """
        if not text or not text.strip().startswith('{'):
            return text

        try:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if not match:
                logger.warning(f"No JSON object found in response: {text}")
                return text # Return original text if no JSON is found
            
            data = json.loads(match.group(0))
            
            validated_data = schema(**data)
            return validated_data
        except json.JSONDecodeError as e:
            logger.error(f"JSON Decode Error: {e} in text: {text}")
            raise ValueError(f"Invalid JSON response: {e}")
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            raise ValueError(f"Invalid response format: {e}")
    
    def run_with_retry(self, prompt: str, tools: List[dict]):
        self.total_count += 1

        for attempt in range(self.max_retries):
            try:
                response = self.generate(prompt=prompt, tools=tools)
                validated_response = self.parse_and_validate(response)

                if validated_response:
                    self.success_count += 1
                    logger.info(f"Attempt {attempt + 1} succeeded with validated response: {validated_response}")
                    return validated_response
                
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {e}")
                if attempt == self.max_retries - 1: 
                    logger.error(f"All {self.max_retries} attempts failed.")
                    raise ValueError("Max retries exceeded")

        logger.error(f"All {self.max_retries} attempts failed.")
        raise ValueError("Max retries exceeded")
    
    def get_success_rate(self):
        if self.total_count == 0:
            return 0
        return self.success_count / self.total_count
