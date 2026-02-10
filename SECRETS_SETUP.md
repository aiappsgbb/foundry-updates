# GitHub Secrets Setup Guide

To enable the RSS feed generator workflow, you need to configure the following secrets in your GitHub repository.

## Required Secrets

### 1. AZURE_OPENAI_API_KEY
- **Description**: Your Azure OpenAI API key
- **How to get it**: 
  1. Go to [Azure Portal](https://portal.azure.com)
  2. Navigate to your Azure OpenAI resource
  3. Click on "Keys and Endpoint" in the left menu
  4. Copy either KEY 1 or KEY 2
- **Format**: String value (e.g., `abc123xyz456...`)

### 2. AZURE_OPENAI_ENDPOINT
- **Description**: Your Azure OpenAI endpoint URL
- **How to get it**:
  1. Go to [Azure Portal](https://portal.azure.com)
  2. Navigate to your Azure OpenAI resource
  3. Click on "Keys and Endpoint" in the left menu
  4. Copy the Endpoint value
- **Format**: URL (e.g., `https://your-resource-name.openai.azure.com/`)

### 3. AZURE_OPENAI_DEPLOYMENT
- **Description**: The name of your Azure OpenAI deployment
- **How to get it**:
  1. Go to [Azure Portal](https://portal.azure.com)
  2. Navigate to your Azure OpenAI resource
  3. Click on "Model deployments" or go to Azure OpenAI Studio
  4. Find your deployment name (e.g., `gpt-4`, `gpt-35-turbo`)
- **Format**: String value (e.g., `gpt-4`)

## How to Add Secrets to GitHub

1. Go to your GitHub repository
2. Click on **Settings** (top navigation)
3. In the left sidebar, click on **Secrets and variables** → **Actions**
4. Click the **New repository secret** button
5. Enter the secret name (e.g., `AZURE_OPENAI_API_KEY`)
6. Enter the secret value
7. Click **Add secret**
8. Repeat steps 4-7 for each required secret

## Testing the Workflow

After adding all secrets, you can manually trigger the workflow to test it:

1. Go to the **Actions** tab in your GitHub repository
2. Select the "Update Azure AI Foundry Models RSS Feed" workflow
3. Click the **Run workflow** button
4. Select the branch and click **Run workflow**

The workflow will run and commit the updated RSS feed to your repository.

## Troubleshooting

### Workflow fails with authentication error
- Verify that `AZURE_OPENAI_API_KEY` is correct
- Check that the key hasn't expired in Azure Portal

### Workflow fails with endpoint error
- Ensure `AZURE_OPENAI_ENDPOINT` is in the correct format with `https://` and trailing slash
- Verify the endpoint URL matches your Azure resource

### Workflow fails with model/deployment error
- Check that `AZURE_OPENAI_DEPLOYMENT` matches an actual deployment name in your Azure OpenAI resource
- Ensure the deployment is in a "Succeeded" state
