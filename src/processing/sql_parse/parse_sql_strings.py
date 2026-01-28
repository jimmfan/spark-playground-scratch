import re
from pyspark.sql import SparkSession

def strip_comments(query: str) -> str:
    """
    Strip comments from SQL query.
    
    Parameters:
    - query (str): The SQL query with potential comments.
    
    Returns:
    - str: The SQL query without comments.
    """
    # Remove multiline comments
    query = re.sub(r"/\*.*?\*/", "", query, flags=re.DOTALL)
    # Remove single line comments
    query = re.sub(r"--.*", "", query)
    return query.strip()

def remove_outer_parentheses_and_alias(query: str) -> str:
    """
    Remove the outermost parentheses and alias from the SQL query.
    
    Parameters:
    - query (str): The SQL query to be normalized.
    
    Returns:
    - str: The SQL query without the outermost parentheses and alias.
    """
    query = strip_comments(query)
    
    # Regular expression to match outermost parentheses with alias
    # pattern = re.compile(r'^\s*\(\s*(.*?)\s*\)\s+as\s+\w+\s*$', re.IGNORECASE | re.DOTALL)
    pattern = re.compile(r'^\s*\((.*)\)\s*(as\s+\w+|\w+)?\s*$', re.IGNORECASE | re.DOTALL)
    
    # Remove the outermost parentheses and alias
    match = pattern.match(query)
    if match:
        return match.group(1).strip()
    return query

def normalize_sql_query(query: str, for_format: bool = False) -> str:
    """
    Normalize the SQL query format for both spark.read.jdbc() and spark.read.format("jdbc").
    
    Parameters:
    - query (str): The SQL query to be normalized.
    - for_format (bool): If True, format for spark.read.format("jdbc"). If False, format for spark.read.jdbc().
    
    Returns:
    - str: The normalized SQL query.
    """
    query = strip_comments(query)
    query, alias = extract_alias(query)
    
    if for_format:
        # Remove outer parentheses if present for spark.read.format("jdbc")
        if query.startswith('(') and query.endswith(')'):
            query = query[1:-1].strip()
    else:
        # Add outer parentheses if not present for spark.read.jdbc()
        if not (query.startswith('(') and query.endswith(')')):
            query = f"({query.strip()})"
    
    return f"{query} {alias}".strip()

