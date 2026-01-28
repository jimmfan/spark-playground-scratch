import os
import re
import subprocess
from git import Repo

# Refined regex patterns for SQL and PySpark tables
sql_table_pattern = re.compile(r'\b(from|join)\s+([a-zA-Z0-9_.]+)\b', re.IGNORECASE)
pyspark_table_pattern = re.compile(r'(spark\.table\(["\'])([a-zA-Z0-9_.]+)(["\'])')

# Function to remove comments from lines
def remove_comments_from_lines(lines):
    cleaned_lines = []
    in_multiline_comment = False
    for line in lines:
        original_line = line
        if not in_multiline_comment:
            # Check for start of multi-line comment
            while True:
                start_comment = line.find('/*')
                single_line_comment_pos = min(
                    [pos for pos in [line.find('--'), line.find('#')] if pos != -1] + [len(line)]
                )
                if start_comment != -1 and start_comment < single_line_comment_pos:
                    end_comment = line.find('*/', start_comment + 2)
                    if end_comment != -1:
                        # Remove the multi-line comment from the line
                        line = line[:start_comment] + line[end_comment + 2:]
                    else:
                        # Multi-line comment starts but doesn't end on this line
                        line = line[:start_comment]
                        in_multiline_comment = True
                        break
                else:
                    break
            # Remove single-line comments
            line = re.sub(r'--.*', '', line)
            line = re.sub(r'#.*', '', line)
            cleaned_lines.append(line.rstrip('\n'))
        else:
            # We are inside a multi-line comment
            end_comment = line.find('*/')
            if end_comment != -1:
                # Multi-line comment ends on this line
                line = line[end_comment + 2:]
                in_multiline_comment = False
                # Check if another multi-line comment starts on the same line
                line = remove_comments_from_lines([line])[0]
                cleaned_lines.append(line.rstrip('\n'))
            else:
                # Entire line is within a multi-line comment
                cleaned_lines.append('')
    return cleaned_lines

# Function to extract CTE aliases from the content
def extract_cte_aliases(content):
    cte_aliases = set()
    # Regex pattern to find CTE aliases
    cte_alias_pattern = re.compile(r'(?:(?:with|,)\s*)([a-zA-Z0-9_]+)\s+as\s*\(', re.IGNORECASE)
    matches = cte_alias_pattern.findall(content)
    cte_aliases.update(matches)
    return cte_aliases

# Function to check for Python import statements and SQL functions using 'from'
def is_false_positive(line_content):
    if re.match(r'^\s*from\s+[a-zA-Z0-9_]+\s+import\s', line_content):
        return True
    if re.search(r'\bextract\s*\(.+?\bfrom\b', line_content, re.IGNORECASE):
        return True
    return False

# Function to get files modified in the last 12 months, checking only the main branch
def get_recent_files(repo_path, since="12 months ago"):
    command = ["git", "-C", repo_path, "log", f"--since={since}", "--name-only", "--pretty=format:", "main"]
    result = subprocess.run(command, capture_output=True, text=True)
    # Filter for .sql and .py files only and remove duplicates
    files = set(line.strip() for line in result.stdout.splitlines() if line.endswith(('.sql', '.py')))
    return sorted(files)

# Function to search for tables in the recently modified files in the main branch
def search_tables_in_file(file_path, repo_url, repo_path):
    tables_info = []
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

    # Remove comments from lines
    cleaned_lines = remove_comments_from_lines(lines)

    # Extract CTE aliases from the cleaned content
    cleaned_content = ''.join(cleaned_lines)
    cte_aliases = extract_cte_aliases(cleaned_content)

    for line_number, line_content in enumerate(cleaned_lines, start=1):
        if is_false_positive(line_content):
            continue

        # Find all SQL table references
        sql_tables = sql_table_pattern.findall(line_content)
        for match in sql_tables:
            table_name = match[1]
            # Ignore if table_name is a CTE alias
            if table_name.lower() in (alias.lower() for alias in cte_aliases):
                continue
            relative_file_path = os.path.relpath(file_path, repo_path).replace(os.sep, '/')
            github_link = f"{repo_url.replace('.git', '')}/blob/main/{relative_file_path}#L{line_number}"
            tables_info.append({'table': table_name, 'filepath': github_link})

        # Find all PySpark table references
        pyspark_tables = pyspark_table_pattern.findall(line_content)
        for match in pyspark_tables:
            table_name = match[1]
            relative_file_path = os.path.relpath(file_path, repo_path).replace(os.sep, '/')
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
