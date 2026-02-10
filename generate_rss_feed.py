#!/usr/bin/env python3
"""
Generate RSS feed for Azure AI Foundry model updates.
Fetches the Microsoft Learn page, uses Azure OpenAI to extract model updates,
and generates an RSS feed.
"""

import os
import sys
import json
from datetime import datetime, timezone
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
import hashlib

import requests
from openai import AzureOpenAI
from bs4 import BeautifulSoup


def fetch_page_content(url):
    """Fetch and parse relevant content from the Microsoft Learn page."""
    print(f"Fetching content from: {url}")
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    
    # Parse HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract relevant sections from Microsoft Learn pages
    relevant_content = []
    
    # Look for main content area (Microsoft Learn uses specific selectors)
    main_content = soup.find('main') or soup.find('article') or soup.find(id='main-content')
    if main_content:
        # Remove script, style, nav, and other non-content elements
        for element in main_content.find_all(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            element.decompose()
        
        # Extract headings and their associated content
        for heading in main_content.find_all(['h1', 'h2', 'h3', 'h4']):
            heading_text = heading.get_text(strip=True)
            if heading_text:
                relevant_content.append(f"\nHEADING: {heading_text}\n")
            
            # Get content after heading until next heading
            for sibling in heading.find_next_siblings():
                if sibling.name in ['h1', 'h2', 'h3', 'h4']:
                    break
                if sibling.name in ['p', 'ul', 'ol', 'table', 'div']:
                    text = sibling.get_text(separator=' ', strip=True)
                    if text:
                        relevant_content.append(text)
        
        # Extract tables specifically (often contain model information)
        tables = main_content.find_all('table')
        for idx, table in enumerate(tables):
            relevant_content.append(f"\nTABLE {idx + 1}:\n")
            # Extract table headers
            headers = [th.get_text(strip=True) for th in table.find_all('th')]
            if headers:
                relevant_content.append(" | ".join(headers))
            
            # Extract table rows
            for row in table.find_all('tr'):
                cells = [td.get_text(strip=True) for td in row.find_all('td')]
                if cells:
                    relevant_content.append(" | ".join(cells))
    else:
        # Fallback: extract all text if we can't find main content
        for script in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            script.decompose()
        text = soup.get_text(separator=' ', strip=True)
        relevant_content.append(text)
    
    # Join all content
    content = '\n'.join(relevant_content)
    
    # Clean up excessive whitespace
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    content = '\n'.join(lines)
    
    print(f"Extracted {len(content)} characters of relevant content")
    return content


def extract_model_updates_with_llm(content, api_key, endpoint, deployment):
    """Use Azure OpenAI to extract model updates from the page content."""
    print("Using Azure OpenAI to extract model updates...")
    
    client = AzureOpenAI(
        api_key=api_key,
        api_version="2024-02-15-preview",
        azure_endpoint=endpoint
    )
    
    # Limit content if still too large (safety measure)
    # Most LLMs have token limits, so we need to be careful
    # Note: Character to token ratio varies by content type and language
    max_chars = 12000  # Conservative estimate for ~3000 tokens
    if len(content) > max_chars:
        print(f"Content is {len(content)} chars, truncating to {max_chars} chars")
        content = content[:max_chars]
    
    prompt = f"""You are analyzing a Microsoft Learn documentation page about Azure AI Foundry models.

Extract the following information about each model mentioned:
1. Model name
2. Model description (brief summary)
3. Key features or updates
4. Any version information
5. Availability information

Format your response as a JSON array of objects, where each object represents a model with these fields:
- title: The model name
- description: A brief description (2-3 sentences)
- link: Use "https://learn.microsoft.com/en-us/azure/ai-foundry/foundry-models/concepts/models-sold-directly-by-azure" as the base link
- pubDate: Use the current date/time

Here's the relevant page content (structured with headings and tables in plain text format):

{content}

Return ONLY valid JSON, no additional text.
"""
    
    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that extracts structured information from documentation."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=2000
    )
    
    result_text = response.choices[0].message.content
    
    # Try to extract JSON from the response
    try:
        # Remove markdown code blocks if present
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0]
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0]
        
        models = json.loads(result_text.strip())
        print(f"Extracted {len(models)} model updates")
        return models
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        print(f"Response: {result_text}")
        return []


def generate_rss_feed(models, output_file):
    """Generate RSS feed XML from model information."""
    print(f"Generating RSS feed with {len(models)} items...")
    
    # Create RSS structure
    rss = Element('rss', version='2.0')
    channel = SubElement(rss, 'channel')
    
    # Channel metadata
    title = SubElement(channel, 'title')
    title.text = 'Azure AI Foundry Model Updates'
    
    link = SubElement(channel, 'link')
    link.text = 'https://learn.microsoft.com/en-us/azure/ai-foundry/foundry-models/concepts/models-sold-directly-by-azure'
    
    description = SubElement(channel, 'description')
    description.text = 'Latest updates on Azure AI Foundry models sold directly by Azure'
    
    language = SubElement(channel, 'language')
    language.text = 'en-us'
    
    last_build_date = SubElement(channel, 'lastBuildDate')
    last_build_date.text = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S +0000')
    
    # Add items for each model
    for model_info in models:
        item = SubElement(channel, 'item')
        
        item_title = SubElement(item, 'title')
        item_title.text = model_info.get('title', 'Unknown Model')
        
        item_link = SubElement(item, 'link')
        item_link.text = model_info.get('link', link.text)
        
        item_description = SubElement(item, 'description')
        item_description.text = model_info.get('description', '')
        
        item_pub_date = SubElement(item, 'pubDate')
        if 'pubDate' in model_info:
            item_pub_date.text = model_info['pubDate']
        else:
            item_pub_date.text = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S +0000')
        
        # Generate a unique GUID for each item based on title using SHA256
        item_guid = SubElement(item, 'guid', isPermaLink='false')
        guid_hash = hashlib.sha256(model_info.get('title', '').encode()).hexdigest()[:32]
        item_guid.text = f"azure-foundry-model-{guid_hash}"
    
    # Pretty print XML
    xml_str = minidom.parseString(tostring(rss, encoding='unicode')).toprettyxml(indent="  ")
    
    # Remove extra blank lines
    xml_lines = [line for line in xml_str.split('\n') if line.strip()]
    xml_str = '\n'.join(xml_lines)
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(xml_str)
    
    print(f"RSS feed written to {output_file}")


def main():
    """Main function to orchestrate RSS feed generation."""
    # Configuration
    url = "https://learn.microsoft.com/en-us/azure/ai-foundry/foundry-models/concepts/models-sold-directly-by-azure?view=foundry&preserve-view=true&tabs=global-standard-aoai%2Cglobal-standard&pivots=azure-openai"
    output_file = "foundry-models.rss"
    
    # Get Azure OpenAI credentials from environment
    api_key = os.environ.get('AZURE_OPENAI_API_KEY')
    endpoint = os.environ.get('AZURE_OPENAI_ENDPOINT')
    deployment = os.environ.get('AZURE_OPENAI_DEPLOYMENT', 'gpt-4')
    
    if not api_key or not endpoint:
        print("Error: AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT environment variables must be set")
        sys.exit(1)
    
    try:
        # Fetch page content
        content = fetch_page_content(url)
        
        # Extract model updates using Azure OpenAI
        models = extract_model_updates_with_llm(content, api_key, endpoint, deployment)
        
        if not models:
            print("Warning: No models extracted. Generating empty feed.")
            models = [{
                'title': 'No updates available',
                'description': 'Failed to extract model information from the page.',
                'link': url,
                'pubDate': datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S +0000')
            }]
        
        # Generate RSS feed
        generate_rss_feed(models, output_file)
        
        print("RSS feed generation completed successfully!")
        
    except Exception as e:
        print(f"Error generating RSS feed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
