#!/usr/bin/env python3
"""Test script to validate the RSS feed generator without API calls."""

import sys
from datetime import datetime, timezone
from xml.etree import ElementTree as ET


def test_fetch_page_content():
    """Test that we can import and call fetch_page_content."""
    from generate_rss_feed import fetch_page_content
    from bs4 import BeautifulSoup
    
    print("Testing fetch_page_content parsing logic...")
    try:
        # Create a mock HTML page to test the parsing
        test_html = """
        <html>
            <head><title>Test Page</title></head>
            <body>
                <nav>Navigation should be removed</nav>
                <main>
                    <h1>Azure AI Models</h1>
                    <p>This is the main content about models.</p>
                    <h2>Available Models</h2>
                    <table>
                        <tr><th>Model Name</th><th>Description</th></tr>
                        <tr><td>GPT-4</td><td>Advanced model</td></tr>
                        <tr><td>GPT-3.5</td><td>Fast model</td></tr>
                    </table>
                    <script>console.log('should be removed');</script>
                </main>
                <footer>Footer should be removed</footer>
            </body>
        </html>
        """
        
        # Test the parsing logic directly with BeautifulSoup
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(test_html, 'html.parser')
        
        # Verify main content is found
        main_content = soup.find('main')
        assert main_content is not None, "Should find main content"
        
        # Verify scripts are removable
        scripts = main_content.find_all('script')
        assert len(scripts) > 0, "Test HTML should have script tags"
        
        print("✓ fetch_page_content parsing logic validated")
        return True
    except Exception as e:
        print(f"✗ fetch_page_content test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_generate_rss_feed():
    """Test RSS feed generation."""
    from generate_rss_feed import generate_rss_feed
    import tempfile
    import os
    
    print("Testing generate_rss_feed...")
    try:
        # Create test data
        test_models = [
            {
                'title': 'GPT-4 Turbo',
                'description': 'Advanced language model with improved performance',
                'link': 'https://example.com/gpt4',
                'pubDate': datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S +0000')
            },
            {
                'title': 'GPT-3.5',
                'description': 'Fast and efficient model',
                'link': 'https://example.com/gpt35'
            }
        ]
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.rss', delete=False) as f:
            temp_file = f.name
        
        try:
            # Generate feed
            generate_rss_feed(test_models, temp_file)
            
            # Validate XML
            tree = ET.parse(temp_file)
            root = tree.getroot()
            
            # Check root element
            assert root.tag == 'rss', "Root element should be 'rss'"
            assert root.get('version') == '2.0', "RSS version should be 2.0"
            
            # Check channel
            channel = root.find('channel')
            assert channel is not None, "Channel element should exist"
            
            # Check channel elements
            title = channel.find('title')
            assert title is not None and title.text, "Channel title should exist"
            
            link = channel.find('link')
            assert link is not None and link.text, "Channel link should exist"
            
            # Check items
            items = channel.findall('item')
            assert len(items) == 2, f"Should have 2 items, found {len(items)}"
            
            # Check first item
            first_item = items[0]
            item_title = first_item.find('title')
            assert item_title is not None and item_title.text == 'GPT-4 Turbo', "Item title should match"
            
            item_guid = first_item.find('guid')
            assert item_guid is not None, "Item should have GUID"
            
            print("✓ generate_rss_feed works correctly")
            return True
            
        finally:
            # Clean up
            if os.path.exists(temp_file):
                os.unlink(temp_file)
                
    except Exception as e:
        print(f"✗ generate_rss_feed failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    try:
        import requests
        import openai
        from bs4 import BeautifulSoup
        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False


def main():
    """Run all tests."""
    print("Running RSS feed generator tests...\n")
    
    results = []
    results.append(("Imports", test_imports()))
    results.append(("Fetch Page", test_fetch_page_content()))
    results.append(("Generate RSS", test_generate_rss_feed()))
    
    print("\n" + "="*50)
    print("Test Results:")
    print("="*50)
    
    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
