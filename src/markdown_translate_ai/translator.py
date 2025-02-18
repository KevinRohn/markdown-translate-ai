import argparse
import os

import logging
import json
from typing import Tuple, Dict, Any
import marko

from markdown_translate_ai.util.validator import ConfigValidator
from markdown_translate_ai.util.statistics import APICallStatistics
from markdown_translate_ai.config.models_config import ModelsRegistry, ModelInfo, ServiceProvider
from markdown_translate_ai.config.prompts import SYSTEM_PROMPT, USER_PROMPT_FIRST, USER_PROMPT_SECOND_WO_SYSTEM
from markdown_translate_ai.providers.base import APIClient
from markdown_translate_ai.providers.openai import OpenAIClient
from markdown_translate_ai.providers.anthropic import AnthropicClient
from markdown_translate_ai.providers.gemini import GeminiClient
from markdown_translate_ai.providers.deepseek import DeepSeekClient


class MarkdownProcessor:
    """Handles markdown processing and cleanup"""
    @staticmethod
    def validate_structure(content: str) -> None:
        """Validate markdown structure"""
        marko.parse(content)

    @staticmethod
    def cleanup_fences(content: str) -> str:
        """Remove unnecessary markdown fences"""
        # This is sometimes added by OpenAI outputs
        if content.startswith('```'):
            lines = content.split('\n')
            if lines[0].strip() in ['```', '```markdown']:
                lines = lines[1:]
                if lines and lines[-1].strip() == '```':
                    lines = lines[:-1]
                content = '\n'.join(lines).strip()
        
        return content

class TranslationPromptFactory:
    """Creates translation prompts based on provider"""
    @staticmethod
    def create_prompt(provider: ServiceProvider, content: str, source_lang: str, target_lang: str) -> Any:
        """Create appropriate prompt based on provider"""

        match provider:
            case ServiceProvider.OPENAI | ServiceProvider.GEMINI | ServiceProvider.DEEPSEEK:
                return {
                    "system": SYSTEM_PROMPT.format(
                        source_lang=source_lang,
                        target_lang=target_lang,
                        text=content
                    ),
                    "user": USER_PROMPT_FIRST.format(
                        source_lang=source_lang,
                        target_lang=target_lang,
                        text=content
                    )
                }
            case ServiceProvider.ANTHROPIC:
                return USER_PROMPT_SECOND_WO_SYSTEM.format(
                    source_lang=source_lang,
                    target_lang=target_lang,
                    text=content
                )
            case _:
                raise ValueError(f"Unsupported provider: {provider}")

class TranslationManager:
    """Manages the translation process"""
    def __init__(self, model_info: ModelInfo, debug: bool = False):
        self.model_info = model_info
        self.setup_logging(debug)
        self.stats_tracker = APICallStatistics()
        self.client = self._create_client()
        self.markdown_processor = MarkdownProcessor()

    def setup_logging(self, debug: bool) -> None:
        """Configure logging"""
        level = logging.DEBUG if debug else logging.INFO
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def _create_client(self) -> APIClient:
        """Create appropriate API client based on provider"""
        ConfigValidator.validate_api_keys(
            self.model_info.provider,
            os.getenv('OPENAI_API_KEY'),
            os.getenv('ANTHROPIC_API_KEY'),
            os.getenv('GEMINI_API_KEY'),
            os.getenv('DEEPSEEK_API_KEY')
        )
        
        if self.model_info.provider == ServiceProvider.OPENAI:
            return OpenAIClient(self.model_info, self.stats_tracker)
        elif self.model_info.provider == ServiceProvider.ANTHROPIC:
            return AnthropicClient(self.model_info, self.stats_tracker)
        elif self.model_info.provider == ServiceProvider.GEMINI:
            return GeminiClient(self.model_info, self.stats_tracker)
        elif self.model_info.provider == ServiceProvider.DEEPSEEK:
            return DeepSeekClient(self.model_info, self.stats_tracker)
        raise ValueError(f"Unsupported provider: {self.model_info.provider}")
    
    def translate(self, content: str, source_lang: str, target_lang: str) -> str:
        """Perform translation while maintaining markdown structure"""
        self.logger.info(f"Translating from {source_lang} to {target_lang}")
        self.logger.info(f"Using model: {self.model_info.name}")
        
        # Validate markdown structure
        self.markdown_processor.validate_structure(content)
        
        # Create appropriate prompt
        prompt = TranslationPromptFactory.create_prompt(
            self.model_info.provider,
            content,
            source_lang,
            target_lang
        )
        
        # Perform translation
        translated = self.client.translate(prompt)
        
        # Clean up and return
        return self.markdown_processor.cleanup_fences(translated)

    def get_statistics(self) -> Dict:
        """Get translation statistics"""
        return {
            "token_usage": self.client.token_tracker.get_usage(),
            "api_calls": self.stats_tracker.get_statistics()
        }

    def cleanup(self) -> None:
        """Clean up resources"""
        self.client.cleanup()


class TranslationJob:
    """Handles a complete translation job"""
    def __init__(self, args: argparse.Namespace, model_info: ModelInfo):
        self.args = args
        self.model_info = model_info
        self.translator = TranslationManager(model_info, args.debug)

    def run(self) -> None:
        """Execute the translation job"""
        try:
            # Read input
            with open(self.args.input_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Translate
            translated = self.translator.translate(
                content,
                self.args.source_lang,
                self.args.target_lang
            )
            
            # Write output
            with open(self.args.output_file, 'w', encoding='utf-8') as f:
                f.write(translated)
            
            # Handle statistics
            if self.args.stats_file:
                stats_file = f"{self.args.output_file}.stats.json"
                with open(stats_file, 'w', encoding='utf-8') as f:
                    json.dump(self.translator.get_statistics(), f, indent=2)
            
            logging.info(f"Translation completed: {self.args.output_file}")
            
        finally:
            self.translator.cleanup()


def parse_arguments() -> Tuple[argparse.Namespace, ModelInfo]:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Markdown Translation System')
    
    parser.add_argument('input_file', type=str, help='Input markdown file')
    parser.add_argument('output_file', type=str, help='Output file path')
    parser.add_argument('target_lang', help='Target language (e.g., "Spanish")')
    parser.add_argument(
        '--model',
        choices=list(ModelsRegistry.get_models().keys()),
        default='gpt-4',
        help='Model to use for translation'
    )
    parser.add_argument(
        '--source-lang',
        default='English',
        help='Source language of the content'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    parser.add_argument(
        '--stats-file',
        action='store_true',
        help='Output statistics to a separate file'
    )
    
    args = parser.parse_args()
    
    # Get and validate model info
    model_info = ModelsRegistry.get_model_info(args.model)
    if not model_info:
        parser.error(f"Invalid model: {args.model}")
    
    # Validate input file
    ConfigValidator.validate_input_file(args.input_file)
    
    return args, model_info


def main():
    """Main entry point"""
    try:
        args, model_info = parse_arguments()
        job = TranslationJob(args, model_info)
        job.run()
        
    except Exception as e:
        logging.error(f"Error during translation: {str(e)}")
        raise

if __name__ == "__main__":
    main()