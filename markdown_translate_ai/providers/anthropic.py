import os
import httpx
import time

from providers.base import APIClient
from config.models_config import ModelInfo
from util.statistics import APICallStatistics, TokenUsageTracker

class AnthropicClient(APIClient):
    """Anthropic API client implementation"""
    def __init__(self, model_info: ModelInfo, stats_tracker: APICallStatistics):
        self.model_info = model_info
        self.stats_tracker = stats_tracker
        self.token_tracker = TokenUsageTracker()
        self.client = self._create_client()

    def _create_client(self) -> httpx.Client:
        """Create and configure the HTTP client"""
        return httpx.Client(
            base_url="https://api.anthropic.com",
            headers={
                "x-api-key": os.getenv('ANTHROPIC_API_KEY'),
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
                "accept": "application/json"
            },
            timeout=httpx.Timeout(30.0, read=300.0),
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
            http2=True
        )

    def translate(self, prompt: str, max_retries: int = 3) -> str:
        retry_count = 0
        last_error = None
        
        while retry_count < max_retries:
            try:
                response = self.client.post(
                    "/v1/messages",
                    json={
                        "model": self.model_info.name,
                        "max_tokens": self.model_info.max_tokens,
                        "temperature": self.model_info.temperature,
                        "messages": [{"role": "user", "content": prompt}]
                    }
                )
                
                if response.status_code != 200:
                    response.raise_for_status()
                
                result = response.json()
                self.stats_tracker.record_call(success=True, retries=retry_count)
                
                self.token_tracker.update(
                    "anthropic",
                    self.model_info.name,
                    result.get("usage", {}).get("input_tokens", 0),
                    result.get("usage", {}).get("output_tokens", 0)
                )
                
                return result["content"][0]["text"]
                
            except (httpx.TimeoutException, httpx.ConnectError) as e:
                last_error = e
                retry_count += 1
                if retry_count == max_retries:
                    break
                
                wait_time = min(2 ** retry_count, 60)
                time.sleep(wait_time)
            
            except Exception as e:
                self.stats_tracker.record_call(success=False, retries=retry_count, error=str(e))
                raise
        
        self.stats_tracker.record_call(success=False, retries=max_retries, error=str(last_error))
        raise TimeoutError(f"Failed after {max_retries} retries. Last error: {str(last_error)}")

    def cleanup(self) -> None:
        """Clean up the HTTP client"""
        self.client.close()