import os
import re
import subprocess
from git import Repo

# Refined regex patterns for SQL and PySpark tables
sql_table_pattern = re.compile(r'\b(from|join)\s+([a-zA-Z0-9_.]+)\b', re.IGNORECASE)
pyspark_table_pattern = re.compile(r'(spark\.table\(["\'])([a-zA-Z0-9_.]+)(["\'])')

# Function to remove comments from a line
def remove_comments(line_content):
    line_content = re.sub(r'#.*', '', line_content)  # Remove Python-style comments
    line_content = re.sub(r'--.*', '', line_content)  # Remove SQL single-line comments
    line_content = re.sub(r'/\*.*?\*/', '', line_content)  # Remove SQL multi-line comments
    return line_content

# Function to check for Python import statements and SQL functions using 'from'
def is_false_positive(line_content):
    line_content = remove_comments(line_content)
    if re.match(r'^\s*from\s+[a-zA-Z0-9_]+\s+import\s', line_content):
        return True
    if re.search(r'\bextract\s*\(.+?\bfrom\b', line_content, re.IGNORECASE):
        return True
    return False

# Function to get files modified in the last 12 months in the entire repo
def get_recent_files(repo_path, since="12 months ago"):
    command = ["git", "-C", repo_path, "log", f"--since={since}", "--name-only", "--pretty=format:"]
    result = subprocess.run(command, capture_output=True, text=True)
    # Filter for .sql and .py files only and remove duplicates
    files = set(line.strip() for line in result.stdout.splitlines() if line.endswith(('.sql', '.py')))
    return sorted(files)

# Function to search for table names in a file
def search_tables_in_file(file_path, repo_url, repo_path):
    tables_info = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for line_number, line_content in enumerate(lines, start=1):
                line_content_cleaned = remove_comments(line_content)
                if is_false_positive(line_content):
                    continue

                # Find all SQL table references
                sql_tables = sql_table_pattern.findall(line_content_cleaned)
                for match in sql_tables:
                    table_name = match[1]
                    relative_file_path = os.path.relpath(file_path, repo_path).replace(os.sep, '/')
                    github_link = f"{repo_url.replace('.git', '')}/blob/main/{relative_file_path}#L{line_number}"
                    tables_info.append({'table': table_name, 'filepath': github_link})
                
                # Find all PySpark table references
                pyspark_tables = pyspark_table_pattern.findall(line_content_cleaned)
                for match in pyspark_tables:
                    table_name = match[1]
                    github_link = f"{repo_url.replace('.git', '')}/blob/main/{relative_file_path}#L{line_number}"
                    tables_info.append({'table': table_name, 'filepath': github_link})
                
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return tables_info

# Function to search for tables in the recently modified files in the entire repo
def search_tables_in_recent_files(repo_path, repo_url):
    recent_files = get_recent_files(repo_path)  # Get files modified in the last 12 months
    repo_tables_info = []
    for file in recent_files:
        file_path = os.path.join(repo_path, file)
        tables_info = search_tables_in_file(file_path, repo_url, repo_path)
        repo_tables_info.extend(tables_info)
    return repo_tables_info

# Function to clone repos and search for tables in recent files
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
        
        print(f"Searching tables in the recently modified files of {repo_name}...")
        tables_info = search_tables_in_recent_files(repo_path, repo_url)
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
    for entry in tables_info:
        print(f"  - Table: {entry['table']}, Filepath: {entry['filepath']}")
