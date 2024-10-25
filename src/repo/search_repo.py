# pip3 install gitpython

import os
import re
from git import Repo

# Define a regex pattern for SQL tables (adjust as needed based on your SQL syntax)
sql_table_pattern = re.compile(r'(from|join)\s+([a-zA-Z0-9_.]+)', re.IGNORECASE)
pyspark_table_pattern = re.compile(r'(spark\.table\(["\'])([a-zA-Z0-9_.]+)(["\'])')

# Function to search for table names in a file
def search_tables_in_file(file_path):
    tables = set()
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
            # Find all SQL table references
            sql_tables = sql_table_pattern.findall(content)
            for match in sql_tables:
                tables.add(match[1])
                
            # Find all PySpark table references
            pyspark_tables = pyspark_table_pattern.findall(content)
            for match in pyspark_tables:
                tables.add(match[1])
                
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return tables

# Function to search through a repository
def search_tables_in_repo(repo_path):
    repo_tables = set()
    for root, dirs, files in os.walk(repo_path):
        for file in files:
            if file.endswith(('.sql', '.py')):
                file_path = os.path.join(root, file)
                tables = search_tables_in_file(file_path)
                repo_tables.update(tables)
    return repo_tables

# Function to clone repos and search for tables
def process_repos(repo_urls, base_dir):
    all_repo_tables = {}
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
        tables = search_tables_in_repo(repo_path)
        all_repo_tables[repo_name] = tables
    
    return all_repo_tables

# Example usage
repo_urls = [
    'https://github.com/yourorg/repo1.git',
    'https://github.com/yourorg/repo2.git',
    # Add more repositories here
]

base_dir = '/path/to/store/cloned/repos'  # Change this to where you want the repos to be stored
all_tables = process_repos(repo_urls, base_dir)

# Output results
for repo, tables in all_tables.items():
    print(f"\nTables found in {repo}:")
    for table in tables:
        print(f"  - {table}")
