import sqlglot
from sqlglot import exp

def remove_redundant_aliases(expression):
    for table in expression.find_all(exp.Alias):
        if isinstance(table.this, exp.Table) and table.alias == table.this.name:
            table.replace(table.this)
    return expression

sql = """
WITH cte_table AS (
    SELECT cte_table.col1 AS col1
    FROM schema.table AS cte_table
)
SELECT * FROM cte_table
"""

# Parse and optimize
parsed = sqlglot.parse_one(sql)
optimized = sqlglot.optimizer.optimize(parsed)

# Apply alias cleanup
cleaned = remove_redundant_aliases(optimized)

# Print cleaned SQL
print(cleaned.sql())
