import sqlglot

def extract_tables(sql):
    # Parse the SQL query
    parsed = sqlglot.parse_one(sql)
    
    # Extract table names
    tables = [table.name for table in parsed.find_all(sqlglot.exp.Table)]
    
    return tables


import sqlglot

def extract_tables_ignore_select(sql):
    try:
        # Parse the SQL query
        parsed = sqlglot.parse_one(sql)
        
        # Extract table names by looking specifically for FROM and JOIN clauses
        tables = []
        if parsed:
            for from_expression in parsed.find_all(sqlglot.exp.From):
                tables.extend([table.name for table in from_expression.find_all(sqlglot.exp.Table)])
            for join_expression in parsed.find_all(sqlglot.exp.Join):
                tables.extend([table.name for table in join_expression.find_all(sqlglot.exp.Table)])
                
    except sqlglot.errors.ParseError:
        # Handle parse errors, returning an empty list or alternative handling as needed
        tables = []
    
    return tables

# Example usage
sql_query = "SELECT name, age, MAX(order_date) FROM users JOIN orders ON users.id = orders.user_id WHERE order_date > '2024-01-01'"
print(extract_tables_ignore_select(sql_query))  # Output: ['users', 'orders']


# Example usage
sql_query = "SELECT name, age FROM users JOIN orders ON users.id = orders.user_id"
print(extract_tables(sql_query))  # Output: ['users', 'orders']
