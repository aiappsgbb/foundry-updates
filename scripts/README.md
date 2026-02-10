# Scripts

This directory contains the Python scripts for generating the Azure AI Foundry models RSS feed.

## Files

- `generate_rss_feed.py`: Main script that fetches the Microsoft Learn page, uses Azure OpenAI to extract model information, and generates the RSS feed
- `test_generate_rss.py`: Test script to validate the RSS feed generator
- `pyproject.toml`: Project dependencies and configuration for uv

## Usage

### With uv (recommended)

```bash
# From this directory
uv run generate_rss_feed.py
```

### With pip

```bash
# Install dependencies
pip install requests openai beautifulsoup4

# Run the script
python generate_rss_feed.py
```

## Environment Variables

The script requires the following environment variables:

- `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key
- `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint URL
- `AZURE_OPENAI_DEPLOYMENT`: Your Azure OpenAI deployment name (optional, defaults to 'gpt-4')

## Output

The RSS feed is written to `../foundry-models.rss` (repository root).
