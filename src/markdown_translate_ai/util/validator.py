import os
from typing import Optional
from pathlib import Path
from markdown_translate_ai.config.models_config import ModelsRegistry, ServiceProvider


class ConfigValidator:
    """Validator for translation configuration"""
    
    @staticmethod
    def validate_input_file(file_path: str) -> None:
        """Validate that input file exists"""
        if not Path(file_path).is_file():
            raise ValueError(f"Input file does not exist: {file_path}")
        
    @staticmethod
    def validate_output_file(file_path: str, update_mode: bool) -> None:
        """Validate that output file path is valid"""
        if file_path is not None:
            if not update_mode and os.path.exists(file_path):
                raise ValueError(f"Output file already exists: {file_path}")
        else:
            raise ValueError("Output file path is required")
        
    @staticmethod
    def validate_model(model: str, provider: ServiceProvider) -> None:
        """Validate that model exists and belongs to the specified provider"""
        model_info = ModelsRegistry.get_model_info(model)
        
        if not model_info:
            valid_models = ModelsRegistry.get_models_for_provider(provider)
            raise ValueError(
                f"Invalid model: {model}. "
                f"Valid models for {provider.value}: {valid_models}"
            )
        
        if model_info.provider != provider:
            raise ValueError(
                f"Model {model} belongs to {model_info.provider.value}, "
                f"but {provider.value} was specified"
            )

    @staticmethod
    def validate_api_keys(
        provider: ServiceProvider,
        openai_key: Optional[str],
        anthropic_key: Optional[str],
        gemini_key: Optional[str],
        deepseek_key: Optional[str]
    ) -> None:
        """Validate that required API keys are available"""
        if provider == ServiceProvider.OPENAI and not openai_key:
            raise ValueError("OpenAI API key is required for OpenAI models")
        if provider == ServiceProvider.ANTHROPIC and not anthropic_key:
            raise ValueError("Anthropic API key is required for Anthropic models")
        if provider == ServiceProvider.GEMINI and not gemini_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        if provider == ServiceProvider.DEEPSEEK and not deepseek_key:
            raise ValueError("DEEPSEEK_API_KEY environment variable is required")