import sqlglot

def extract_tables(sql):
    # Parse the SQL query
    parsed = sqlglot.parse_one(sql)
    
    # Extract table names
    tables = [table.name for table in parsed.find_all(sqlglot.exp.Table)]
    
    return tables

import re
import sqlglot

def replace_iif_with_case(sql):
    # Convert IIF(condition, true_value, false_value) to CASE WHEN condition THEN true_value ELSE false_value END
    pattern = re.compile(r"IIF\(([^,]+),\s*([^,]+),\s*([^)]+)\)", re.IGNORECASE)
    return pattern.sub(r"CASE WHEN \1 THEN \2 ELSE \3 END", sql)

def extract_tables(sql):
    # Preprocess the SQL to replace IIF
    sql = replace_iif_with_case(sql)
    
    try:
        # Parse the preprocessed SQL query
        parsed = sqlglot.parse_one(sql)
        
        # Extract table names if parsing succeeded
        tables = [table.name for table in parsed.find_all(sqlglot.exp.Table)] if parsed else []
    except sqlglot.errors.ParseError:
        # Return an empty list if parsing fails
        tables = []
    
    return tables

# Example usage
sql_query = "SELECT iif(table.`column name` IS NULL, 'value1', 'value2') AS column_alias FROM table"
print(extract_tables(sql_query))  # Expected Output: ['table']


# Example usage
sql_query = "SELECT name, age FROM users JOIN orders ON users.id = orders.user_id"
print(extract_tables(sql_query))  # Output: ['users', 'orders']
