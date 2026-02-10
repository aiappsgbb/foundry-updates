# foundry-updates

Automated RSS feed generator for Azure AI Foundry model updates.

## Overview

This repository contains a GitHub Action that automatically generates an RSS feed from the [Azure AI Foundry models documentation page](https://learn.microsoft.com/en-us/azure/ai-foundry/foundry-models/concepts/models-sold-directly-by-azure). The feed is updated daily and provides information about models sold directly by Azure.

## How It Works

1. **Daily Schedule**: The GitHub Action runs daily at 2 AM UTC
2. **Page Fetching**: Fetches content from the Microsoft Learn page
3. **AI Processing**: Uses Azure OpenAI to extract and structure model information
4. **RSS Generation**: Creates an RSS feed (`foundry-models.rss`) with the extracted updates
5. **Auto-commit**: Automatically commits and pushes the updated RSS feed to the repository

## Setup

### Required GitHub Secrets

To run this workflow, you need to configure the following secrets in your GitHub repository:

- `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key
- `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint URL (e.g., `https://your-resource.openai.azure.com/`)
- `AZURE_OPENAI_DEPLOYMENT`: Your Azure OpenAI deployment name (e.g., `gpt-4`)

### Manual Trigger

You can manually trigger the workflow from the GitHub Actions tab using the "Run workflow" button.

## Files

- `scripts/generate_rss_feed.py`: Python script that fetches the page, processes it with Azure OpenAI, and generates the RSS feed
- `scripts/test_generate_rss.py`: Test script to validate the RSS feed generator
- `scripts/pyproject.toml`: Python dependencies and project configuration (using uv)
- `.github/workflows/update-rss-feed.yml`: GitHub Actions workflow configuration
- `foundry-models.rss`: Generated RSS feed (updated automatically)

## Local Development

To run the script locally using uv:

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Set environment variables
export AZURE_OPENAI_API_KEY="your-key"
export AZURE_OPENAI_ENDPOINT="your-endpoint"
export AZURE_OPENAI_DEPLOYMENT="gpt-4"

# Run the script
cd scripts
uv run generate_rss_feed.py
```

Alternatively, using pip:

```bash
# Install dependencies
cd scripts
pip install -r pyproject.toml  # or manually: pip install requests openai beautifulsoup4

# Set environment variables
export AZURE_OPENAI_API_KEY="your-key"
export AZURE_OPENAI_ENDPOINT="your-endpoint"
export AZURE_OPENAI_DEPLOYMENT="gpt-4"

# Run the script
python generate_rss_feed.py
```

## RSS Feed

The generated RSS feed (`foundry-models.rss`) can be subscribed to in any RSS reader to stay updated with Azure AI Foundry model changes.