import sqlglot
from sqlglot import exp, parse_one
from collections import defaultdict

def remove_redundant_aliases(expr):
    table_aliases = {}
    table_counts = defaultdict(int)

    # Step 1: Find all table aliases
    for table in expr.find_all(exp.TableAlias):
        table_expr = table.this
        alias = table.alias_or_name
        if isinstance(table_expr, exp.Table):
            table_counts[table_expr.name] += 1
            if alias == table_expr.name:
                # Safe to remove redundant alias
                table.replace(table_expr)
                table_aliases[alias] = None
            else:
                table_aliases[alias] = table_expr.name

    # Step 2: Remove redundant prefixes from column references
    for col in expr.find_all(exp.Column):
        table_part = col.table
        column_name = col.name

        if table_part and table_aliases.get(table_part) is None:
            # Strip the table prefix
            col.replace(exp.to_identifier(column_name))

    return expr