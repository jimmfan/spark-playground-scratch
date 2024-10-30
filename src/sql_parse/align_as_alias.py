import sqlglot
from sqlglot import expressions as exp

def align_aliases(sql, fixed_column=60):
    # Parse the SQL query into an AST
    parsed = sqlglot.parse_one(sql, read='hive')

    def traverse(node):
        if isinstance(node, exp.Select):
            # Collect all select expressions
            expressions = []
            for select_expression in node.expressions:
                if isinstance(select_expression, exp.Alias):
                    expr_sql = select_expression.this.sql()
                    alias = select_expression.alias
                else:
                    expr_sql = select_expression.sql()
                    alias = None
                # Remove line breaks and excess whitespace for length calculation
                expr_sql_no_breaks = ' '.join(expr_sql.split())
                expr_length = len(expr_sql_no_breaks)
                expressions.append((expr_sql, alias, expr_length))
            # Set the fixed column where 'AS' should align
            # Reconstruct select expressions with aligned aliases
            new_expressions = []
            for expr_sql, alias, expr_length in expressions:
                # Calculate spaces based on the fixed column alignment
                spaces_needed = max(1, fixed_column - expr_length)
                spaces = ' ' * spaces_needed
                if alias:
                    # Remove line breaks for alignment but keep original formatting
                    expr_sql_no_breaks = ' '.join(expr_sql.split())
                    new_expr_sql = expr_sql_no_breaks + spaces + 'AS ' + alias
                else:
                    new_expr_sql = expr_sql
                # Parse the new expression
                new_expression = sqlglot.parse_one(new_expr_sql)
                new_expressions.append(new_expression)
            # Replace the expressions in the select node
            node.set("expressions", new_expressions)
        # Recursively traverse child nodes
        for child in node.args.values():
            if isinstance(child, list):
                for item in child:
                    if isinstance(item, exp.Expression):
                        traverse(item)
            elif isinstance(child, exp.Expression):
                traverse(child)

    # Start traversal from the root of the AST
    traverse(parsed)

    # Return the formatted SQL with aligned aliases
    return parsed.sql(pretty=True)

# Example usage
sql = '''
WITH cte1 AS (
    SELECT column1, column2
    FROM table1
),
cte2 AS (
    SELECT column3, column4
    FROM table2
)
SELECT
    cte1.column1 AS col1_alias,
    cte2.column3 AS col3_alias,
    (SELECT
        MAX(value)
     FROM
        table3
     WHERE
        id = cte1.id
    ) AS max_value
FROM cte1
JOIN cte2 ON cte1.column2 = cte2.column4
'''

formatted_sql = align_aliases(sql)
print(formatted_sql)
