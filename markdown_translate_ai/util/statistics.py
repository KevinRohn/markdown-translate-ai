from datetime import datetime
from typing import Dict, List, Optional

class Statistics:
    """Base class for tracking various statistics"""
    def __init__(self):
        self.start_time = datetime.now()

    def _calculate_duration(self) -> float:
        """Calculate duration in seconds since start"""
        return (datetime.now() - self.start_time).total_seconds()
    
class APICallStatistics(Statistics):
    """Tracks API call statistics"""
    def __init__(self):
        super().__init__()
        self.total_calls = 0
        self.successful_calls = 0
        self.failed_calls = 0
        self.retry_calls = 0
        self.call_history: List[Dict] = []
    
    def record_call(self, success: bool, retries: int = 0, error: Optional[str] = None) -> None:
        """Record details of an API call"""
        self.total_calls += 1
        if success:
            self.successful_calls += 1
        else:
            self.failed_calls += 1
        self.retry_calls += retries
        
        self.call_history.append({
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "retries": retries,
            "error": error
        })
    
    def get_statistics(self) -> Dict:
        """Get comprehensive statistics about API usage"""
        duration = self._calculate_duration()
        minutes = duration / 60
        
        return {
            "total_calls": self.total_calls,
            "successful_calls": self.successful_calls,
            "failed_calls": self.failed_calls,
            "retry_calls": self.retry_calls,
            "duration_seconds": duration,
            "calls_per_minute": round(self.total_calls / minutes, 2) if minutes > 0 else 0,
            "success_rate": round((self.successful_calls / self.total_calls * 100), 2) if self.total_calls > 0 else 0,
            "call_history": self.call_history
        }


class TokenUsageTracker:
    """Tracks token usage for API calls"""
    def __init__(self):
        self.reset()
    
    def reset(self) -> None:
        """Reset usage statistics"""
        self.last_usage: Dict = {}
    
    def update(self, provider: str, model: str, input_tokens: int, output_tokens: int) -> None:
        """Update token usage statistics"""
        self.last_usage = {
            "provider": provider,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens
        }
    
    def get_usage(self) -> Dict:
        """Get current token usage statistics"""
        return self.last_usage