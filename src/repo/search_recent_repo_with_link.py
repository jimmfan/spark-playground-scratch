import os
import re
import subprocess
from git import Repo

# Refined regex patterns for SQL, PySpark tables, and CTEs
sql_table_pattern = re.compile(r'\b(from|join)\s+([a-zA-Z0-9_.]+)\b', re.IGNORECASE)
pyspark_table_pattern = re.compile(r'(spark\.table\(["\'])([a-zA-Z0-9_.]+)(["\'])')
cte_pattern = re.compile(r'\bwith\s+([a-zA-Z0-9_]+)\s+as\s*\(', re.IGNORECASE)

# Function to remove comments from a line
# Function to remove comments from a line or block of text

def manual_remove_comments(line_content):
    cleaned_text = []
    in_comment = False
    i = 0
    
    while i < len(line_content):
        # Check for the start of a comment
        if not in_comment and line_content[i:i+2] == '/*':
            in_comment = True
            i += 2  # Move past '/*'
        # Check for the end of a comment
        elif in_comment and line_content[i:i+2] == '*/':
            in_comment = False
            i += 2  # Move past '*/'
        # If we're not in a comment, add the character to the result
        elif not in_comment:
            cleaned_text.append(line_content[i])
            i += 1
        # If we're inside a comment, skip to the next character
        else:
            i += 1
    
    return '\n'.join(cleaned_text).strip()

def remove_comments(line_content):
    # Remove Python-style comments (#)
    # r'/\*\s*[\s\S]*?\s*\*/'
    line_content = re.sub(r'#.*', '', line_content)  # Remove Python-style comments
    # Remove SQL single-line comments (--)
    line_content = re.sub(r'--.*', '', line_content)  # Remove SQL single-line comments
    # Remove all multi-line SQL comments (/* ... */) across multiple lines
    line_content = re.sub(r'/\*[\s\S]*?\*/', '', line_content)  # Remove SQL multi-line comments
    return line_content

# Function to check for Python import statements and SQL functions using 'from'
def is_false_positive(line_content_cleaned):
    # Directly using the cleaned line content
    if re.match(r'^\s*from\s+[a-zA-Z0-9_]+\s+import\s', line_content_cleaned):
        return True
    if re.search(r'\bextract\s*\(.+?\bfrom\b', line_content_cleaned, re.IGNORECASE):
        return True
    return False

# Function to get files modified in the last 12 months, checking only the main branch
def get_recent_files(repo_path, since="12 months ago"):
    command = ["git", "-C", repo_path, "log", f"--since={since}", "--name-only", "--pretty=format:", "main"]
    result = subprocess.run(command, capture_output=True, text=True)
    # Filter for .sql and .py files only and remove duplicates
    files = set(line.strip() for line in result.stdout.splitlines() if line.endswith(('.sql', '.py')))
    return sorted(files)

# Function to search for table names in a file with encoding handling and CTE filtering
def search_tables_in_file(file_path, repo_url, repo_path):
    tables_info = []
    cte_aliases = set()
    
    # Extract CTE aliases and filter them out of results
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='latin-1') as file:
                lines = file.readlines()
        except UnicodeDecodeError:
            print(f"Skipping file due to encoding issue: {file_path}")
            return tables_info

    # Identify CTE aliases at the beginning of the file
    for line_content in lines:
        line_content_cleaned = remove_comments(line_content)
        cte_matches = cte_pattern.findall(line_content_cleaned)
        for alias in cte_matches:
            cte_aliases.add(alias.lower())  # Store CTE aliases in lowercase to ensure case-insensitive matching

    # Search for tables, excluding CTE aliases
    for line_number, line_content in enumerate(lines, start=1):
        line_content_cleaned = remove_comments(line_content)
        
        # Use cleaned content in is_false_positive and table extraction
        if is_false_positive(line_content_cleaned):
            continue

        # Find all SQL table references
        sql_tables = sql_table_pattern.findall(line_content_cleaned)
        for match in sql_tables:
            table_name = match[1].lower()  # Use lowercase for consistent CTE exclusion
            if table_name not in cte_aliases:  # Ignore CTE aliases
                relative_file_path = os.path.relpath(file_path, repo_path).replace(os.sep, '/')
                github_link = f"{repo_url.replace('.git', '')}/blob/main/{relative_file_path}#L{line_number}"
                tables_info.append({'table': table_name, 'filepath': github_link})
        
        # Find all PySpark table references
        pyspark_tables = pyspark_table_pattern.findall(line_content_cleaned)
        for match in pyspark_tables:
            table_name = match[1]
            github_link = f"{repo_url.replace('.git', '')}/blob/main/{relative_file_path}#L{line_number}"
            tables_info.append({'table': table_name, 'filepath': github_link})
    
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