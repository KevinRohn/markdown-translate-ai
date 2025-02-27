from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, List

class ServiceProvider(Enum):
    """Available service providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    DEEPSEEK = "deepseek"

    @classmethod
    def from_string(cls, value: str) -> 'ServiceProvider':
        """Convert string to ServiceProvider enum"""
        try:
            return cls(value.lower())
        except ValueError:
            raise ValueError(f"Invalid service provider: {value}. Valid options: {[p.value for p in cls]}")

@dataclass
class ModelInfo:
    """Model Info dataclass"""
    name: str
    provider: ServiceProvider
    description: str
    max_tokens: int = 4096
    temperature: float = 0.1

class ModelsRegistry:
    """Registry of available AI models"""
    
    @classmethod
    def get_models(cls) -> Dict[str, ModelInfo]:
        """Get all available models"""
        return {
            # OpenAI Models
            "gpt-4o": ModelInfo(
                name="gpt-4o",
                provider=ServiceProvider.OPENAI,
                description="GPT-4 Optimized",
                max_tokens= 16384
            ),
            "gpt-4o-mini": ModelInfo(
                name="gpt-4o-mini",
                provider=ServiceProvider.OPENAI,
                description="GPT-4 Optimized Mini",
                max_tokens= 16384
            ),
            "gpt-3.5-turbo": ModelInfo(
                name="gpt-3.5-turbo",
                provider=ServiceProvider.OPENAI,
                description="GPT-3.5 Turbo",
                max_tokens= 4096
            ),
            "gpt-4" : ModelInfo(
                name="gpt-4",
                provider=ServiceProvider.OPENAI,
                description="GPT-4",
                max_tokens= 6000
            ),
            "gpt-4-turbo": ModelInfo(
                name="gpt-4-turbo",
                provider=ServiceProvider.OPENAI,
                description="GPT-4 Turbo",
                max_tokens= 4096
            ),
            "o1": ModelInfo(
                name="o1",
                provider=ServiceProvider.OPENAI,
                description="O1",
                max_tokens= 100000
            ),
            "o1-mini": ModelInfo(
                name="o1-mini",
                provider=ServiceProvider.OPENAI,
                description="O1 Mini",
                max_tokens= 65536
            ),
            "o3-mini": ModelInfo(
                name="o3-mini",
                provider=ServiceProvider.OPENAI,
                description="O3 Mini",
                max_tokens= 100000
            ),
            "o1-preview": ModelInfo(
                name="o1-preview",
                provider=ServiceProvider.OPENAI,
                description="O1 Preview",
                max_tokens= 32768
            ),
            
            # Anthropic Models
            "claude-3.5-sonnet": ModelInfo(
                name="claude-3-5-sonnet-20241022",
                provider=ServiceProvider.ANTHROPIC,
                description="Claude 3.5 Sonnet",
                max_tokens=4096
            ),
            "claude-3.7-sonnet-latest": ModelInfo(
                name="claude-3-7-sonnet-latest",
                provider=ServiceProvider.ANTHROPIC,
                description="Claude 3.7 Sonnet",
                max_tokens=8192
            ),
            "claude-3.5-sonnet-latest": ModelInfo(
                name="claude-3-5-sonnet-latest",
                provider=ServiceProvider.ANTHROPIC,
                description="Claude 3.5 Sonnet",
                max_tokens=4096
            ),

            "claude-3.5-haiku": ModelInfo(
                name="claude-3-5-haiku-20241022",
                provider=ServiceProvider.ANTHROPIC,
                description="Claude 3.5 Haiku",
                max_tokens=4096
            ),
            "claude-3.5-haiku-latest": ModelInfo(
                name="claude-3-5-haiku-latest",
                provider=ServiceProvider.ANTHROPIC,
                description="Claude 3.5 Haiku",
                max_tokens=4096
            ),

            "claude-3-sonnet": ModelInfo(
                name="claude-3-sonnet-20240229",
                provider=ServiceProvider.ANTHROPIC,
                description="Claude 3 Sonnet",
                max_tokens=4096
            ),
            "claude-3-haiku": ModelInfo(
                name="claude-3-haiku-20240307",
                provider=ServiceProvider.ANTHROPIC,
                description="Claude 3 Haiku",
                max_tokens=4096
            ),
            "claude-3-opus-latest": ModelInfo(
                name="claude-3-opus-latest",
                provider=ServiceProvider.ANTHROPIC,
                description="Claude 3 Opus",
                max_tokens=4096
            ),

            # Gemini Models
            "gemini-1.5-flash": ModelInfo(
                name="gemini-1.5-flash",
                provider=ServiceProvider.GEMINI,
                description="Gemini 1.5 Flash",
                max_tokens=8192
            ),
            "gemini-1.5-pro": ModelInfo(
                name="gemini-1.5-pro",
                provider=ServiceProvider.GEMINI,
                description="Gemini 1.5 Pro",
                max_tokens=8192
            ),
            "gemini-2.0-flash": ModelInfo(
                name="gemini-2.0-flash",
                provider=ServiceProvider.GEMINI,
                description="Gemini 1.5 Pro",
                max_tokens=8192
            ),

            # DeepSeek Models
            "deepseek-chat": ModelInfo(
                name="deepseek-chat",
                provider=ServiceProvider.DEEPSEEK,
                description="DeepSeek Chat",
                max_tokens=8192
            )
        }

    @classmethod
    def get_models_for_provider(cls, provider: ServiceProvider) -> List[str]:
        """Get available model IDs for a specific provider"""
        return [
            model_id for model_id, info in cls.get_models().items()
            if info.provider == provider
        ]

    @classmethod
    def get_model_info(cls, model_id: str) -> Optional[ModelInfo]:
        """Get information about a specific model"""
        return cls.get_models().get(model_id)