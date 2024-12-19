# create_confluence_pages.py

from atlassian import Confluence
import os

# Import the documentation structure
from documentation_structure import documentation_structure

# Confluence credentials and settings
CONFLUENCE_URL = 'https://your-domain.atlassian.net/wiki'  # Replace with your Confluence URL
USERNAME = 'your-email@example.com'  # Your Confluence username/email
API_TOKEN = 'your-api-token'  # Your Confluence API token
SPACE_KEY = 'YOURSPACEKEY'  # Replace with your target Confluence space key
PARENT_PAGE_TITLE = 'Automation & Innovation Documentation'  # Root page title

# Initialize Confluence API
confluence = Confluence(
    url=CONFLUENCE_URL,
    username=USERNAME,
    password=API_TOKEN
)

def create_page(title, content, space, parent_id=None):
    """
    Creates a Confluence page.
    """
    # Check if the page already exists
    existing_page = confluence.get_page_by_title(space, title)
    if existing_page:
        print(f"Page '{title}' already exists. Skipping creation.")
        return existing_page['id']
    
    # Create the page
    page = confluence.create_page(
        space=space,
        title=title,
        body=content,
        parent_id=parent_id
    )
    print(f"Created page: {title}")
    return page['id']

def traverse_structure(structure, parent_id=None):
    """
    Recursively traverses the documentation structure and creates pages.
    """
    for title, content in structure.items():
        page_id = create_page(title, content if isinstance(content, str) else "", SPACE_KEY, parent_id)
        if isinstance(content, dict):
            traverse_structure(content, parent_id=page_id)

def main():
    # Create the root page if it doesn't exist
    root_page = confluence.get_page_by_title(SPACE_KEY, PARENT_PAGE_TITLE)
    if not root_page:
        root_page = confluence.create_page(
            space=SPACE_KEY,
            title=PARENT_PAGE_TITLE,
            body="Root page for Automation & Innovation Documentation."
        )
        print(f"Created root page: {PARENT_PAGE_TITLE}")
    else:
        print(f"Root page '{PARENT_PAGE_TITLE}' already exists.")
    
    root_page_id = root_page['id']
    
    # Start traversing and creating pages
    traverse_structure(documentation_structure, parent_id=root_page_id)

if __name__ == "__main__":
    main()
