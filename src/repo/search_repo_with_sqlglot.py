import os
import re
import subprocess
import ast
from git import Repo
import sqlglot

# Function to remove comments from a block of text
def remove_comments(text):
    # Remove Python-style comments (#)
    text = re.sub(r'#.*', '', text)
    # Remove SQL single-line comments (--)
    text = re.sub(r'--.*', '', text)
    # Remove all multi-line SQL comments (/* ... */) across multiple lines
    text = re.sub(r'/\*[\s\S]*?\*/', '', text)
    return text

# Function to get files modified in the last 12 months, checking only the main branch
def get_recent_files(repo_path, since="12 months ago"):
    command = ["git", "-C", repo_path, "log", f"--since={since}", "--name-only", "--pretty=format:", "main"]
    result = subprocess.run(command, capture_output=True, text=True)
    # Filter for .sql and .py files only and remove duplicates
    files = set(line.strip() for line in result.stdout.splitlines() if line.endswith(('.sql', '.py')))
    return sorted(files)

# Function to search for table names in a file using sqlglot
def search_tables_in_file(file_path, repo_url, repo_path):
    tables_info = []
    relative_file_path = os.path.relpath(file_path, repo_path).replace(os.sep, '/')

    # Determine the file extension
    _, file_extension = os.path.splitext(file_path)

    # Read the file content with encoding handling
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='latin-1') as file:
                content = file.read()
        except UnicodeDecodeError:
            print(f"Skipping file due to encoding issue: {file_path}")
            return tables_info

    # Remove comments
    content_cleaned = remove_comments(content)

    if file_extension.lower() == '.sql':
        try:
            parsed = sqlglot.parse_one(content_cleaned)
            # Extract CTE aliases
            ctes = parsed.ctes or []
            cte_aliases = {cte.alias_or_name.lower() for cte in ctes}

            # Find all table references, excluding CTEs
            tables = parsed.find_all(sqlglot.exp.Table)
            for table in tables:
                table_name = table.sql(dialect='spark').lower()
                if table_name not in cte_aliases:
                    github_link = f"{repo_url.replace('.git', '')}/blob/main/{relative_file_path}"
                    tables_info.append({'table': table_name, 'filepath': github_link})
        except Exception as e:
            print(f"Error parsing SQL file {file_path}: {e}")
    elif file_extension.lower() == '.py':
        # Try to extract SQL code from the Python file
        try:
            # Parse the Python file to extract strings
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, (ast.Str, ast.Constant)):
                    if isinstance(node, ast.Constant):
                        value = node.value
                    else:
                        value = node.s
                    if isinstance(value, str) and len(value.strip()) > 0 and '\n' in value:
                        sql_code = value.strip()
                        # Remove comments from the extracted string
                        sql_code_cleaned = remove_comments(sql_code)
                        # Attempt to parse the SQL code
                        try:
                            parsed = sqlglot.parse_one(sql_code_cleaned)
                            # Extract CTE aliases
                            ctes = parsed.ctes or []
                            cte_aliases = {cte.alias_or_name.lower() for cte in ctes}

                            # Find all table references, excluding CTEs
                            tables = parsed.find_all(sqlglot.exp.Table)
                            for table in tables:
                                table_name = table.sql(dialect='spark').lower()
                                if table_name not in cte_aliases:
                                    # Get line number
                                    line_number = node.lineno
                                    github_link = f"{repo_url.replace('.git', '')}/blob/main/{relative_file_path}#L{line_number}"
                                    tables_info.append({'table': table_name, 'filepath': github_link})
                        except Exception:
                            # Not valid SQL code, skip
                            continue
        except Exception as e:
            print(f"Error parsing Python file {file_path}: {e}")
    else:
        # Other file types can be ignored or processed as needed
        pass

    return tables_info

# Function to search for tables in the recently modified files in the main branch
def search_tables_in_recent_files(repo_path, repo_url):
    recent_files = get_recent_files(repo_path)  # Get files modified in the last 12 months
    repo_tables_info = []
    for file in recent_files:
        file_path = os.path.join(repo_path, file)
        if not os.path.exists(file_path):
            print(f"File does not exist in the main branch, skipping: {file_path}")
            continue
        tables_info = search_tables_in_file(file_path, repo_url, repo_path)
        repo_tables_info.extend(tables_info)
    return repo_tables_info

# Function to clone repos and search for tables in recent files
def process_repos(repo_urls, base_dir):
    all_repo_tables_info = []
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
        all_repo_tables_info += tables_info

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
for entry in all_tables_info:
    print(f"  - Table: {entry['table']}, Filepath: {entry['filepath']}")
