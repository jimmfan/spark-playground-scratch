# create_confluence_pages.py

from atlassian import Confluence
import os
import logging
from documentation_structure import documentation_structure

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Confluence credentials and settings
CONFLUENCE_URL = os.getenv('CONFLUENCE_URL', 'https://your-domain.atlassian.net/wiki')  # Replace with your Confluence URL or set as environment variable
USERNAME = os.getenv('CONFLUENCE_USERNAME', 'your-email@example.com')  # Your Confluence username/email
API_TOKEN = os.getenv('CONFLUENCE_API_TOKEN', 'your-api-token')  # Your Confluence API token
SPACE_KEY = os.getenv('CONFLUENCE_SPACE_KEY', 'YOURSPACEKEY')  # Replace with your target Confluence space key
ROOT_PAGE_TITLE = os.getenv('CONFLUENCE_ROOT_PAGE_TITLE', 'Automation & Innovation Projects')  # Root page title for all projects

# Initialize Confluence API
confluence = Confluence(
    url=CONFLUENCE_URL,
    username=USERNAME,
    password=API_TOKEN
)

def page_exists_under_parent(title, parent_id):
    """
    Checks if a page with the given title exists under the specified parent using CQL.
    """
    cql = f'title = "{title}" AND ancestor = {parent_id} AND type = page'
    result = confluence.cql(cql, limit=1)
    
    if result.get('results'):
        logging.info(f"Page '{title}' already exists under parent ID {parent_id}.")
        return result['results'][0]['id']
    return None

def create_page(title, content, space, parent_id=None):
    """
    Creates a Confluence page under the specified parent if it doesn't already exist.
    Returns the page ID.
    """
    try:
        if parent_id:
            existing_page_id = page_exists_under_parent(title, parent_id)
            if existing_page_id:
                return existing_page_id
        else:
            # If no parent_id is specified, check globally within the space
            existing_page = confluence.get_page_by_title(space, title)
            if existing_page:
                logging.info(f"Page '{title}' already exists in space '{space}'.")
                return existing_page['id']
        
        # Create the page
        page = confluence.create_page(
            space=space,
            title=title,
            body=content,
            parent_id=parent_id
        )
        logging.info(f"Created page: '{title}' with ID {page['id']}.")
        return page['id']
    except Exception as e:
        logging.error(f"Error creating page '{title}': {e}")
        return None

def traverse_structure(structure, parent_id=None):
    """
    Recursively traverses the documentation structure and creates pages.
    """
    for title, content in structure.items():
        if isinstance(content, dict):
            # If content is a dictionary, create/check the page and recurse
            page_id = create_page(title, "", SPACE_KEY, parent_id)
            if page_id:
                traverse_structure(content, parent_id=page_id)
        else:
            # If content is a string, create/check the page with the content
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
        logging.info(f"Created root page: '{ROOT_PAGE_TITLE}' with ID {root_page['id']}.")
    else:
        logging.info(f"Root page '{ROOT_PAGE_TITLE}' already exists with ID {root_page['id']}.")
    
    root_page_id = root_page['id']
    
    # Start traversing and creating pages for each project
    traverse_structure(documentation_structure, parent_id=root_page_id)

if __name__ == "__main__":
    main()
