# markdown-translate-ai

This application allows you to translate Markdown files using various AI models.

## Install with pip

This package is available on PyPi, so you can install it with pip

`pip install markdown-translate-ai`

## Local installation form the repository

Ensure you have Python installed and install the required dependencies:

```bash
pip install -r requirements.txt
```

## Environment Variables (API Keys)

```bash
export OPENAI_API_KEY="your_openai_api_key"
export ANTHROPIC_API_KEY="your_anthropic_api_key"
export GEMINI_API_KEY="your_gemini_api_key"
export DEEPSEEK_API_KEY="your_deepseek_api_key"
```

<details><summary>On Windows (PowerShell)</summary>

```powershell
$env:OPENAI_API_KEY="your_openai_api_key"
$env:ANTHROPIC_API_KEY="your_anthropic_api_key"
$env:GEMINI_API_KEY="your_gemini_api_key"
$env:DEEPSEEK_API_KEY="your_deepseek_api_key"
```
</details>

## Usage

Run the application with the following arguments:

```bash
markdown-translate-ai <input_file> <output_file> <target_lang> --model <model_name> [options]
```

### Arguments:
- `<input_file>`: Path to the input Markdown file.
- `<output_file>`: Path to save the translated Markdown file.
- `<target_lang>`: Target language for translation (e.g., `"Spanish"`).
- `--model <model_name>`: AI model to use for translation. See [Available models](#Available-models)

### Optional Flags:
- `--source-lang <language>`: Specify the source language (default: `"English"`).
- `--debug`: Enable debug logging.
- `--stats-file`: Save translation statistics as a JSON file.

### Available models

The application supports multiple AI providers, including:

- OpenAI (`gpt-4o`, `gpt-3.5-turbo`, etc.)
- Anthropic (`claude-3.5-sonnet`, `claude-3-haiku`, etc.)
- Gemini (`gemini-1.5-flash`, `gemini-1.5-pro`, etc.)
- DeepSeek (`deepseek-chat`)

Full list of available models to use with the `--models` argument:

| Name                       | Points to                    |
| -------------------------- | ---------------------------- |
| `gpt-4o`                   | `gpt-4o`                     |
| `gpt-4o-mini`              | `gpt-4o-mini`                |
| `gpt-3.5-turbo`            | `gpt-3.5-turbo`              |
| `gpt-4`                    | `gpt-4`                      |
| `gpt-4-turbo`              | `gpt-4-turbo`                |
| `o1`                       | `o1`                         |
| `o1-mini`                  | `o1-mini`                    |
| `o3-mini`                  | `o3-mini`                    |
| `o1-preview`               | `o1-preview`                 |
| `claude-3.5-sonnet`        | `claude-3-5-sonnet-20241022` |
| `claude-3.5-sonnet-latest` | `claude-3-5-sonnet-latest`   |
| `claude-3.5-haiku`         | `claude-3-5-haiku-20241022`  |
| `claude-3.5-haiku-latest`  | `claude-3-5-haiku-latest`    |
| `claude-3-sonnet`          | `claude-3-sonnet-20240229`   |
| `claude-3-haiku`           | `claude-3-haiku-20240307`    |
| `claude-3-opus-latest`     | `claude-3-opus-latest`       |
| `gemini-1.5-flash`         | `gemini-1.5-flash`           |
| `gemini-1.5-pro`           | `gemini-1.5-pro`             |
| `gemini-2.0-flash`         | `gemini-2.0-flash`           |
| `deepseek-chat`            | `deepseek-chat`              |