import sqlglot
from sqlglot import parse_one, exp

def clean_redundant_aliases(expr):
    alias_mapping = {}

    # Step 1: Remove table aliases where alias == table name
    for table_alias in expr.find_all(exp.TableAlias):
        table_expr = table_alias.this
        alias_expr = table_alias.args.get("alias")

        if isinstance(table_expr, exp.Table) and alias_expr:
            table_name = table_expr.name
            alias_name = alias_expr.name
            if table_name == alias_name:
                alias_mapping[alias_name] = True
                table_alias.replace(table_expr)

    # Step 2: Remove table prefixes in columns where alias was removed
    for col in expr.find_all(exp.Column):
        if col.args.get("table") in alias_mapping:
            col.set("table", None)

    # Step 3: Remove redundant column aliases (e.g., col1 AS col1)
    for alias in list(expr.find_all(exp.Alias)):
        this_expr = alias.this
        alias_name = alias.alias
        if isinstance(this_expr, exp.Column):
            col_name = this_expr.name
            if col_name == alias_name:
                alias.replace(this_expr)

    return expr
