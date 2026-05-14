import os
import json
import logging
from typing import List, Dict, Any, Optional
from groq import Groq
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

class GroqClient:
    def __init__(self):
        # Allow loading from environment variable
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            logger.warning("GROQ_API_KEY environment variable not set. API calls will fail.")
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"
        self.fallback_model = "mixtral-8x7b-32768"

    def get_chat_completion(self, messages: List[Dict[str, str]], schema: BaseModel, temperature: float = 0.2) -> Optional[BaseModel]:
        """
        Calls Groq API and expects a JSON response conforming to the given Pydantic schema.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=1024,
                response_format={"type": "json_object"},
                timeout=25.0
            )
            content = response.choices[0].message.content
            
            # Parse and validate JSON
            parsed_data = json.loads(content)
            validated_data = schema(**parsed_data)
            return validated_data
            
        except Exception as e:
            logger.error(f"Groq API call failed with primary model: {e}")
            logger.info(f"Retrying with fallback model {self.fallback_model}...")
            try:
                response = self.client.chat.completions.create(
                    model=self.fallback_model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=1024,
                    response_format={"type": "json_object"},
                    timeout=25.0
                )
                content = response.choices[0].message.content
                parsed_data = json.loads(content)
                validated_data = schema(**parsed_data)
                return validated_data
            except Exception as fallback_e:
                logger.error(f"Groq fallback API call failed: {fallback_e}")
                return None

groq_client = GroqClient()
