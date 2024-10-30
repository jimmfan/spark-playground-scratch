from sqlglot import Generator, IdentifierPolicy
import textwrap

class CustomGenerator(Generator):
    max_line_length = 80
    indent = "  "    # Customize indentation
    sep = "\n"       # Use newline as separator

    def __init__(self, **kwargs):
        # Use the custom identifier policy
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
            # Check if adding next_piece exceeds max_line_length
            if len(current_line) + len(next_piece) > self.max_line_length:
                # Add current line to lines and start a new line
                lines.append(current_line.rstrip())
                current_line = self.indent + next_piece.strip()
            else:
                current_line += next_piece
        lines.append(current_line.rstrip())
        return self.sep.join(lines)
