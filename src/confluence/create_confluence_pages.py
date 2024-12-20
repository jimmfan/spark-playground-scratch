# create_confluence_pages.py

from atlassian import Confluence
import markdown2
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

def create_page(title, content, space, parent_id=None):
    """
    Creates a Confluence page with the given title and content.
    """
    # Check if the page already exists under the given parent
    existing_page = confluence.get_page_by_title(space, title, parent_id=parent_id)
    if existing_page:
        print(f"Page '{title}' already exists under parent ID {parent_id}. Skipping creation.")
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

def convert_markdown_to_html(markdown_content):
    """
    Converts a Markdown string to HTML.
    """
    html_content = markdown2.markdown(markdown_content)
    return html_content

def traverse_structure(structure, parent_id=None):
    """
    Recursively traverses the documentation structure and creates pages.
    Consolidates subsections into single pages.
    """
    for project_name, project_sections in structure.items():
        print(f"Processing project: {project_name}")
        # Create or get the project page
        project_page_id = create_page(project_name, "", SPACE_KEY, parent_id)
        
        for section_name, subsections in project_sections.items():
            print(f"  Creating section: {section_name}")
            # Consolidate all subsections into one content string
            consolidated_content = ""
            for subsection_title, subsection_content in subsections.items():
                consolidated_content += subsection_content + "\n\n"
            
            # Convert the consolidated Markdown to HTML
            html_content = convert_markdown_to_html(consolidated_content)
            
            # Create the section page under the project page
            create_page(section_name, html_content, SPACE_KEY, parent_id=project_page_id)

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
