from sqlglot import Generator, IdentifierPolicy
import textwrap

import sqlglot
from sqlglot import Generator, IdentifierPolicy

class CustomGenerator(Generator):
    max_line_length = 80
    indent = "  "
    sep = "\n"

    def __init__(self, **kwargs):
        kwargs['identifier_policy'] = IdentifierPolicy(
            quote_all=False,
            identify=False,
            normalize=False
        )
        super().__init__(**kwargs)

    def csv(self, expressions):
        lines = []
        current_line = ""
        for i, expression in enumerate(expressions):
            sql = self.sql(expression)
            prefix = ", " if i > 0 else ""
            next_piece = f"{prefix}{sql}"
            if len(current_line) + len(next_piece) > self.max_line_length:
                lines.append(current_line.rstrip())
                current_line = self.indent + next_piece.strip()
            else:
                current_line += next_piece
        lines.append(current_line.rstrip())
        return self.sep.join(lines)

    def where_sql(self, expression):
        conditions = self.sql(expression.this)
        wrapped_conditions = textwrap.fill(
            conditions,
            width=self.max_line_length,
            subsequent_indent=self.indent
        )
        return f"\nWHERE {wrapped_conditions}"

# Example usage
query = """
SELECT key1, key2, key3, key4, key5, key6
FROM database_name.table_name
WHERE key1 > 10 AND key2 < 20
"""

expression = sqlglot.parse_one(query, read='hive')
generator = CustomGenerator(dialect='hive')
custom_sql = generator.generate(expression)
print(custom_sql)
