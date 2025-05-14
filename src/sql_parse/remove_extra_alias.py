import sqlglot
from sqlglot import parse_one, exp

def clean_redundant_aliases(expr):
    alias_mapping = {}

    # Step 1: Remove redundant table aliases
    for table_alias in expr.find_all(exp.TableAlias):
        table_expr = table_alias.this
        alias_expr = table_alias.alias

        if isinstance(table_expr, exp.Table) and alias_expr:
            table_name = table_expr.name
            alias_name = alias_expr.name

            if table_name == alias_name:
                alias_mapping[alias_name] = True
                table_alias.replace(table_expr)

    # Step 2: Remove table prefixes from column references
    for col in expr.find_all(exp.Column):
        if col.table in alias_mapping:
            col.set("table", None)

    # Step 3: Remove column aliases where name == column name
    for col_alias in expr.find_all(exp.Alias):
        if isinstance(col_alias.this, exp.Column):
            column = col_alias.this
            if col_alias.name == column.name:
                col_alias.replace(column)

    return expr
