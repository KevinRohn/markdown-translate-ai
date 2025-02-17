import os
from typing import Dict
from openai import OpenAI

from markdown_translate_ai.providers.base import APIClient
from markdown_translate_ai.config.models_config import ModelInfo
from markdown_translate_ai.util.statistics import APICallStatistics, TokenUsageTracker

class GeminiClient(APIClient):
    """Gemini API client implementation"""
    def __init__(self, model_info: ModelInfo, stats_tracker: APICallStatistics):
        self.model_info = model_info
        self.stats_tracker = stats_tracker
        self.client = OpenAI(
            api_key=os.getenv('GEMINI_API_KEY'),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        self.token_tracker = TokenUsageTracker()

    def translate(self, prompt: Dict[str, str]) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model_info.name,
                messages=[
                    {"role": "system", "content": prompt["system"]},
                    {"role": "user", "content": prompt["user"]}
                ],
                temperature=self.model_info.temperature,
                max_tokens=self.model_info.max_tokens
            )
            
            self.stats_tracker.record_call(success=True)
            self.token_tracker.update(
                "gemini",
                self.model_info.name,
                response.usage.prompt_tokens,
                response.usage.completion_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.stats_tracker.record_call(success=False, error=str(e))
            raise

    def cleanup(self) -> None:
        pass
