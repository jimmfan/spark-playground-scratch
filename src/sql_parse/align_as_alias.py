import sqlglot
from sqlglot import expressions as exp

def align_aliases(sql):
    # Parse the SQL query into an AST
    parsed = sqlglot.parse_one(sql)

    def traverse(node):
        if isinstance(node, exp.Select):
            # Collect all select expressions
            expressions = []
            max_length = 0
            for select_expression in node.expressions:
                expr_sql = select_expression.this.sql()
                alias = select_expression.alias
                expressions.append((expr_sql, alias))
                max_length = max(max_length, len(expr_sql))
            # Reconstruct select expressions with aligned aliases
            new_expressions = []
            for expr_sql, alias in expressions:
                spaces = ' ' * (max_length - len(expr_sql) + 1)
                if alias:
                    new_expr_sql = expr_sql + spaces + 'AS ' + alias
                else:
                    new_expr_sql = expr_sql
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
SELECT cte1.column1 AS col1_alias, cte2.column3 AS col3_alias
FROM cte1
JOIN cte2 ON cte1.column2 = cte2.column4
'''

formatted_sql = align_aliases(sql)
print(formatted_sql)
