import sqlglot
from sqlglot.generator import Generator
import textwrap

class CustomGenerator(Generator):
    max_line_length = 80
    indent = "  "
    sep = "\n"

    def __init__(self, **kwargs):
        kwargs.setdefault('identify', False)  # Do not quote identifiers
        kwargs.setdefault('normalize', False) # Preserve original case
        super().__init__(**kwargs)

    def select_sql(self, expression):
        # Use existing functionality to get SELECT expressions
        expressions = expression.expressions

        # Calculate the maximum length of expressions before 'AS'
        max_expr_length = 0
        expr_info = []
        for expr in expressions:
            if isinstance(expr, sqlglot.expressions.Alias):
                expr_str = self.sql(expr.this)
                alias_str = self.sql(expr.alias)
                expr_info.append((expr_str, alias_str))
            else:
                expr_str = self.sql(expr)
                expr_info.append((expr_str, None))

            # Update maximum length
            expr_length = len(expr_str)
            if expr_length > max_expr_length:
                max_expr_length = expr_length

        # Generate SQL lines with padded expressions
        lines = []
        current_line = ""
        for i, (expr_str, alias_str) in enumerate(expr_info):
            # Prepare the prefix (comma at the beginning if not first expression)
            prefix = ', ' if i > 0 else ''
            
            # Pad the expression to the max length
            padding = ' ' * (max_expr_length - len(expr_str))
            padded_expr_str = expr_str + padding

            # Construct the line with or without alias
            if alias_str:
                line_piece = f"{prefix}{padded_expr_str} AS {alias_str}"
            else:
                line_piece = f"{prefix}{padded_expr_str}"

            # Check if adding the next piece exceeds the max line length
            if len(current_line) + len(line_piece) > self.max_line_length:
                # Start a new line
                if current_line:
                    lines.append(current_line.rstrip())
                current_line = self.indent + line_piece.strip()
            else:
                current_line += line_piece

        # Append any remaining line
        if current_line:
            lines.append(current_line.rstrip())

        # Combine lines
        select_clause = self.sep.join(lines)

        # Return the SELECT clause
        return f"SELECT{self.sep}{select_clause}"

    # Optionally override other methods if needed
    # For example, to handle WHERE clause formatting
    def where_sql(self, expression):
        conditions = self.sql(expression.this)
        wrapped_conditions = textwrap.fill(
            conditions,
            width=self.max_line_length,
            subsequent_indent=self.indent
        )
        return f"\nWHERE {wrapped_conditions}"

    # You can also override other methods like group_by_sql, order_by_sql, etc.

# Example usage
query = """
SELECT col1 AS alias1, col2_long AS alias2, col3 AS alias3
FROM table_name
WHERE col1 > 10 AND col2_long < 20
"""

# Parse the query
expression = sqlglot.parse_one(query)

# Use the custom generator
generator = CustomGenerator()
custom_sql = generator.generate(expression)

print(custom_sql)
