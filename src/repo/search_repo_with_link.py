import os
import re
from git import Repo

# Define a regex pattern for SQL tables (adjust as needed based on your SQL syntax)
sql_table_pattern = re.compile(r'(from|join)\s+([a-zA-Z0-9_.]+)', re.IGNORECASE)
pyspark_table_pattern = re.compile(r'(spark\.table\(["\'])([a-zA-Z0-9_.]+)(["\'])')

# Function to search for table names in a file
def search_tables_in_file(file_path, repo_url, repo_path):
    tables_info = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for line_number, line_content in enumerate(lines, start=1):
                # Find all SQL table references
                sql_tables = sql_table_pattern.findall(line_content)
                for match in sql_tables:
                    table_name = match[1]
                    if table_name not in tables_info:
                        tables_info[table_name] = []
                    # Construct the GitHub link
                    relative_file_path = os.path.relpath(file_path, repo_path).replace(os.sep, '/')
                    github_link = f"{repo_url}/blob/main/{relative_file_path}#L{line_number}"
                    tables_info[table_name].append(github_link)
                
                # Find all PySpark table references
                pyspark_tables = pyspark_table_pattern.findall(line_content)
                for match in pyspark_tables:
                    table_name = match[1]
                    if table_name not in tables_info:
                        tables_info[table_name] = []
                    # Construct the GitHub link
                    github_link = f"{repo_url}/blob/main/{relative_file_path}#L{line_number}"
                    tables_info[table_name].append(github_link)
                
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return tables_info

# Function to search through a repository
def search_tables_in_repo(repo_path, repo_url):
    repo_tables_info = {}
    for root, dirs, files in os.walk(repo_path):
        for file in files:
            if file.endswith(('.sql', '.py')):
                file_path = os.path.join(root, file)
                tables_info = search_tables_in_file(file_path, repo_url, repo_path)
                for table, links in tables_info.items():
                    if table not in repo_tables_info:
                        repo_tables_info[table] = set()
                    repo_tables_info[table].update(links)
    return repo_tables_info

# Function to clone repos and search for tables
def process_repos(repo_urls, base_dir):
    all_repo_tables_info = {}
    for repo_url in repo_urls:
        repo_name = repo_url.split('/')[-1].replace('.git', '')
        repo_path = os.path.join(base_dir, repo_name)
        
        # Clone the repo if not already cloned
        if not os.path.exists(repo_path):
            print(f"Cloning {repo_url}...")
            Repo.clone_from(repo_url, repo_path)
        else:
            print(f"Updating {repo_name}...")
            repo = Repo(repo_path)
            repo.remote().pull()
        
        print(f"Searching tables in {repo_name}...")
        tables_info = search_tables_in_repo(repo_path, repo_url)
        all_repo_tables_info[repo_name] = tables_info
    
    return all_repo_tables_info

# Example usage
repo_urls = [
    'https://github.com/yourorg/repo1.git',
    'https://github.com/yourorg/repo2.git',
    # Add more repositories here
]

base_dir = '/path/to/store/cloned/repos'  # Change this to where you want the repos to be stored
all_tables_info = process_repos(repo_urls, base_dir)

# Output results
for repo, tables_info in all_tables_info.items():
    print(f"\nTables found in {repo}:")
    for table, links in tables_info.items():
        print(f"  - {table}:")
        for link in links:
            print(f"      * {link}")
