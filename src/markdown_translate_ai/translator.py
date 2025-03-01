import argparse
import os
import re
from difflib import SequenceMatcher
import hashlib
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

def get_block_id(text: str) -> str:
    return hashlib.md5(text.strip().encode('utf-8')).hexdigest()

class DiffTranslator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_markdown(self, node) -> str:
        """Return a markdown representation using MarkdownRenderer."""
        from marko.md_renderer import MarkdownRenderer
        renderer = MarkdownRenderer()
        return renderer.render(node).strip()

    def find_changed_blocks(self, old_source: str, new_source: str) -> list[tuple[int, str]]:
        """Find changed block-level markdown elements using marko AST.
        
        The returned block texts are extracted as markdown
        Deletions are marked with an emnpty string.
        """
        old_doc = marko.parse(old_source)
        new_doc = marko.parse(new_source)
        old_blocks = [self.get_markdown(child) for child in old_doc.children if self.get_markdown(child)]
        new_blocks = [self.get_markdown(child) for child in new_doc.children if self.get_markdown(child)]

        self.logger.info(f"Comparing blocks - Old blocks: {len(old_blocks)}, New blocks: {len(new_blocks)}")
        matcher = SequenceMatcher(None, old_blocks, new_blocks)
        changed_blocks = []
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag in ('replace', 'insert'):
                block_text = "\n\n".join(new_blocks[j1:j2]).strip()
                if block_text:
                    self.logger.info(f"Found {tag} starting at new block index {j1}: {block_text[:100]}...")
                    changed_blocks.append((j1, block_text))
            elif tag == 'delete':
                self.logger.info(f"Found deletion at old block indices {i1}-{i2}, corresponding new index {j1}")
                changed_blocks.append((j1, ""))
        self.logger.info(f"Found {len(changed_blocks)} changed blocks")
        return changed_blocks

    def merge_translations(self, old_source: str, new_source: str, old_translation: str,
                           new_block_translations: list[tuple[int, str]]) -> str:
        """
        Sequentially merge translations using the diff opcodes.
        new_block_translations is a list of tuples (new_index, translated_text)
        obtained from find_changed_blocks (with index from new source).
        """
        old_doc = marko.parse(old_source)
        new_doc = marko.parse(new_source)
        trans_doc = marko.parse(old_translation)
        old_blocks = [self.get_markdown(child) for child in old_doc.children if self.get_markdown(child)]
        new_blocks = [self.get_markdown(child) for child in new_doc.children if self.get_markdown(child)]
        trans_blocks = [self.get_markdown(child) for child in trans_doc.children if self.get_markdown(child)]
        
        matcher = SequenceMatcher(None, old_blocks, new_blocks)

        changed_sorted = sorted(new_block_translations, key=lambda t: t[0])
        changed_iter = iter(changed_sorted)
        try:
            current_changed = next(changed_iter)
        except StopIteration:
            current_changed = None
        
        merged = []

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                for offset, new_idx in enumerate(range(j1, j2)):
                    old_idx = i1 + offset
                    if old_idx < len(trans_blocks):
                        merged.append(trans_blocks[old_idx])
                    else:
                        merged.append(new_blocks[new_idx])
            elif tag in ("insert", "replace"):
                for new_idx in range(j1, j2):
                    if current_changed and current_changed[0] == new_idx:
                        merged.append(current_changed[1])
                        try:
                            current_changed = next(changed_iter)
                        except StopIteration:
                            current_changed = None
                    else:
                        merged.append(new_blocks[new_idx])
            elif tag == "delete":
                continue
        
        result = "\n\n".join(merged)
        result = re.sub(r'\n{3,}', '\n\n', result)
        return result.strip()
    
class TranslationJob:
    """Handles a complete translation job"""
    def __init__(self, args: argparse.Namespace, model_info: ModelInfo):
        self.args = args
        self.model_info = model_info
        self.translator = TranslationManager(model_info, args.debug)
        self.diff_translator = DiffTranslator()

    def run(self) -> None:
        """Execute the translation job"""
        try:
            self.logger = logging.getLogger(__name__)
            self.logger.info(f"Starting translation job for {self.args.input_file}")
            
            with open(self.args.input_file, 'r', encoding='utf-8') as f:
                new_source = f.read()
            
            old_source = ""
            if self.args.update_mode:
                self.logger.info("Running in update mode")
                if self.args.previous_source:
                    with open(self.args.previous_source, 'r', encoding='utf-8') as f:
                        old_source = f.read()
                    self.logger.info(f"Loaded previous source: {self.args.previous_source}")
                else:
                    self.logger.warning("No previous source file provided for update mode")
            
            if old_source:
                self.logger.info("Performing selective translation of changed content")
                changed_blocks = self.diff_translator.find_changed_blocks(old_source, new_source)

                translated_blocks = []
                for new_index, block in changed_blocks:
                    if not block.strip():
                        self.logger.info(f"Skipping translation for empty block at new index {new_index}")
                        continue  # Do not add empty block
                    self.logger.info(f"Translating block at new index {new_index} ({len(block)} chars)")
                    translated = self.translator.translate(
                        block,
                        self.args.source_lang,
                        self.args.target_lang
                    )
                    translated_blocks.append((new_index, translated))

                if os.path.exists(self.args.output_file):
                    with open(self.args.output_file, 'r', encoding='utf-8') as f:
                        old_translation = f.read()
                    self.logger.info(f"Loaded existing translation: {self.args.output_file}")
                else:
                    self.logger.warning("No existing translated file found; using new source as fallback")
                    old_translation = new_source

                translated = self.diff_translator.merge_translations(
                    old_source,
                    new_source,
                    old_translation,
                    translated_blocks
                )
                self.logger.info(f"Merged {len(translated_blocks)} translated blocks")
            else:
                self.logger.info("Running in full translation mode")
                translated = self.translator.translate(
                    new_source,
                    self.args.source_lang,
                    self.args.target_lang
                )
    
            with open(self.args.output_file, 'w', encoding='utf-8') as f:
                f.write(translated)
            self.logger.info(f"Wrote {len(translated)} characters to {self.args.output_file}")
            
            if self.args.stats_file:
                stats_file = f"{self.args.output_file}.stats.json"
                stats = self.translator.get_statistics()
                with open(stats_file, 'w', encoding='utf-8') as f:
                    json.dump(stats, f, indent=2)
                self.logger.info(f"Wrote statistics to {stats_file}")
                self.logger.debug(f"Statistics: {json.dumps(stats, indent=2)}")
            
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
        '--update-mode',
        action='store_true',
        help='Enable update mode for selective translation'
    )
    parser.add_argument(
        '--previous-source',
        type=str,
        help='Path to previous version of source file for comparison'
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