import sqlglot

def extract_tables(sql):
    # Parse the SQL query
    parsed = sqlglot.parse_one(sql)
    
    # Extract table names
    tables = [table.name for table in parsed.find_all(sqlglot.exp.Table)]
    
    return tables


def extract_tables2(sql):
    # Parse the SQL query with error handling set to ignore
    parsed = sqlglot.parse(sql)
    
    # Extract table names if parsing succeeds
    tables = []
    for tree in parsed:
        tables.extend([table.name for table in tree.find_all(sqlglot.exp.Table)])
    
    return tables

# Example usage
sql_query = "SELECT name, age FROM users JOIN orders ON users.id = orders.user_id"
print(extract_tables(sql_query))  # Output: ['users', 'orders']
