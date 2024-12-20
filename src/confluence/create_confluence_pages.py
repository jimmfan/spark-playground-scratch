# create_confluence_pages.py

from atlassian import Confluence
import os

# Import the updated documentation structure
from documentation_structure import documentation_structure

# Confluence credentials and settings
CONFLUENCE_URL = 'https://your-domain.atlassian.net/wiki'  # Replace with your Confluence URL
USERNAME = 'your-email@example.com'  # Your Confluence username/email
API_TOKEN = 'your-api-token'  # Your Confluence API token
SPACE_KEY = 'YOURSPACEKEY'  # Replace with your target Confluence space key
ROOT_PAGE_TITLE = 'Automation & Innovation Projects'  # Root page title for all projects

# Initialize Confluence API
confluence = Confluence(
    url=CONFLUENCE_URL,
    username=USERNAME,
    password=API_TOKEN
)

def page_exists_under_parent(space, title, parent_id):
    """
    Checks if a page with the given title exists under the specified parent using CQL.
    """
    # Construct the CQL query
    cql = f'title = "{title}" AND ancestor = {parent_id}'
    
    # Execute the CQL query
    result = confluence.cql(cql, limit=1)
    
    # Check if any results were returned
    if result.get('results'):
        return result['results'][0]  # Page exists under the parent
    return None  # Page does not exist under the parent


def create_page(title, content, space, parent_id=None):
    """
    Creates a Confluence page under the specified parent if it doesn't already exist.
    """
    if parent_id:
        existing_page = page_exists_under_parent(space, title, parent_id)
        if existing_page:
            print(f"Page '{title}' already exists under parent ID {parent_id}. Skipping creation.")
            return existing_page['id']
    else:
        # If no parent_id is specified, check globally within the space
        existing_page = confluence.get_page_by_title(space, title)
        if existing_page:
            print(f"Page '{title}' already exists in space '{space}'. Skipping creation.")
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
        if isinstance(content, dict):
            # If content is a dictionary, create the page and recurse
            page_id = create_page(title, "", SPACE_KEY, parent_id)
            traverse_structure(content, parent_id=page_id)
        else:
            # If content is a string, create the page with the content
            create_page(title, content, SPACE_KEY, parent_id)

def main():
    # Create the root page if it doesn't exist
    root_page = confluence.get_page_by_title(SPACE_KEY, ROOT_PAGE_TITLE)
    if not root_page:
        root_page = confluence.create_page(
            space=SPACE_KEY,
            title=ROOT_PAGE_TITLE,
            body="Root page for Automation & Innovation Projects Documentation."
        )
        print(f"Created root page: {ROOT_PAGE_TITLE}")
    else:
        print(f"Root page '{ROOT_PAGE_TITLE}' already exists.")
    
    root_page_id = root_page['id']
    
    # Start traversing and creating pages for each project
    traverse_structure(documentation_structure, parent_id=root_page_id)

if __name__ == "__main__":
    main()
