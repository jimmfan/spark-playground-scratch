import sqlglot
import re

def align_aliases(sql, fixed_column=60):
    # Parse the SQL query into an AST using the Hive dialect
    parsed = sqlglot.parse_one(sql, read='hive')

    # Generate the formatted SQL with pretty printing
    formatted_sql = parsed.sql(pretty=True)

    # Split the formatted SQL into lines
    lines = formatted_sql.split('\n')

    # Variables to track the state
    in_select = False
    select_start_index = 0

    # Process each line to identify SELECT statements and align aliases
    for i, line in enumerate(lines):
        stripped_line = line.strip().upper()

        # Check if the line is the start of a SELECT statement
        if stripped_line == 'SELECT':
            in_select = True
            select_start_index = i + 1  # Index where select expressions start
            continue

        # Check if we've reached the end of the SELECT statement
        if in_select and (stripped_line.startswith('FROM') or stripped_line == ''):
            in_select = False
            # Process the SELECT expressions
            select_end_index = i
            select_lines = lines[select_start_index:select_end_index]

            # Align the aliases in the SELECT expressions
            select_lines_aligned = align_select_expressions(select_lines, fixed_column)
            # Replace the original lines with the aligned lines
            lines[select_start_index:select_end_index] = select_lines_aligned

        # Handle the last SELECT in the query
        if in_select and i == len(lines) - 1:
            select_end_index = i + 1
            select_lines = lines[select_start_index:select_end_index]
            select_lines_aligned = align_select_expressions(select_lines, fixed_column)
            lines[select_start_index:select_end_index] = select_lines_aligned

    # Join the lines back into a single string
    aligned_sql = '\n'.join(lines)
    return aligned_sql

def align_select_expressions(select_lines, fixed_column):
    expressions = []
    max_expr_length = 0

    # Regular expression to split expressions and aliases
    # Match only when 'AS' is not inside parentheses (e.g., not inside functions)
    alias_regex = re.compile(r'^(.*?)(\s+AS\s+)([^\(\)]+)$', re.IGNORECASE)

    # Extract expressions and aliases, calculate maximum expression length
    for line in select_lines:
        # Capture leading whitespace to maintain indentation
        leading_whitespace_match = re.match(r'^(\s*)', line)
        leading_whitespace = leading_whitespace_match.group(1) if leading_whitespace_match else ''
        line_stripped = line.strip()
        
        # Check if line contains 'AS' used for aliasing
        match = alias_regex.match(line_stripped)
        if match:
            expr_part = match.group(1).rstrip()
            alias_part = match.group(3).strip()
            # Ensure 'AS' is not inside parentheses
            if '(' not in expr_part or expr_part.rfind('(') < expr_part.rfind(')'):
                is_alias = True
            else:
                is_alias = False
        else:
            expr_part = line_stripped
            alias_part = ''
            is_alias = False

        expr_no_spaces = ' '.join(expr_part.split())
        expr_length = len(expr_no_spaces)
        max_expr_length = max(max_expr_length, expr_length)
        expressions.append((leading_whitespace, expr_part, alias_part, expr_length, is_alias))

    # Decide the column to align to
    padding = 1  # You can adjust this padding as needed
    align_column = max(fixed_column, max_expr_length + padding)

    # Align the aliases based on the align_column
    aligned_lines = []
    for leading_whitespace, expr_part, alias_part, expr_length, is_alias in expressions:
        if is_alias:
            spaces_needed = max(1, align_column - expr_length)
            spaces = ' ' * spaces_needed
            aligned_line = f"{expr_part}{spaces}AS {alias_part}"
        else:
            aligned_line = expr_part
        aligned_lines.append(f"{leading_whitespace}{aligned_line}")
    return aligned_lines

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
  (
    SELECT
      MAX(value)
    FROM
      table3
    WHERE
      id = cte1.id
  ) AS max_value,
  CASE
    WHEN cte1.column2 > 0 THEN 'positive'
    ELSE 'non-positive'
  END AS column_case,
  CAST(some_col AS date) AS date_col,
  CAST(other_col AS STRING) AS string_col
FROM cte1
JOIN cte2 ON cte1.column2 = cte2.column4
'''

formatted_sql = align_aliases(sql, fixed_column=60)
print(formatted_sql)
