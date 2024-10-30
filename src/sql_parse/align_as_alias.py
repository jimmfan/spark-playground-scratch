import sqlparse

def align_sql_aliases(query):
    # Parse and reformat query
    parsed = sqlparse.parse(query)[0]
    lines = []
    max_length = max([len(token.value) for token in parsed.tokens if token.ttype is None])

    for token in parsed.tokens:
        if token.ttype is None:  # Ignore keywords and other tokens
            token_value = token.value.strip()
            if " AS " in token_value:
                col, alias = token_value.split(" AS ")
                aligned_line = f"{col:<{max_length}} AS {alias.strip()}"
                lines.append(aligned_line)
            else:
                lines.append(token_value)
        else:
            lines.append(token.value.strip())

    return "\n".join(lines)

query = """SELECT first_name AS firstName, last_name AS lastName, birth_date AS birthDate, address AS userAddress FROM users;"""
print(align_sql_aliases(query))
