from typing import Any
from abc import ABC, abstractmethod

class APIClient(ABC):
    """Abstract base class for API clients"""
    @abstractmethod
    def translate(self, prompt: Any) -> str:
        """Translate content using the API"""
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """Clean up any resources"""
        pass