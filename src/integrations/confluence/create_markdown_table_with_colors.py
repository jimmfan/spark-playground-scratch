import pandas as pd

def generate_html_table_with_colors(headers, rows, num_placeholders=3):
    """
    Generates an HTML table with specified placeholder empty rows and color-coded cells.

    :param headers: List of column headers.
    :param rows: List of lists containing table rows.
    :param num_placeholders: Number of empty placeholder rows to add.
    :return: String containing the HTML table.
    """
    # Create DataFrame from existing rows
    df = pd.DataFrame(rows, columns=headers)
    
    # Create placeholder rows
    placeholders = pd.DataFrame([["" for _ in headers] for _ in range(num_placeholders)], columns=headers)
    
    # Append placeholder rows to the DataFrame
    df = pd.concat([df, placeholders], ignore_index=True)
    
    # Define a function to apply styles
    def highlight_occupation(val):
        color = ""
        if val == "Engineer":
            color = "background-color: #d1e7dd;"  # Light green
        elif val == "Designer":
            color = "background-color: #cff4fc;"  # Light blue
        elif val == "Artist":
            color = "background-color: #f8d7da;"  # Light red
        elif val == "":
            color = "background-color: #f8f9fa;"  # Light gray for placeholders
        return color

    # Apply styles to the 'Occupation' column
    styled_df = df.style.applymap(highlight_occupation, subset=["Occupation"])

    # Convert the styled DataFrame to HTML
    html_table = styled_df.hide_index().render()

    return html_table

# Example data
headers = ["Name", "Age", "Occupation"]
rows = [
    ["Alice", 24, "Engineer"],
    ["Bob", 30, "Designer"],
    ["Charlie", 22, "Artist"]
]

# Generate HTML table with color-coded 'Occupation' column and placeholders
html_table = generate_html_table_with_colors(headers, rows, num_placeholders=3)

# Output the HTML table
print(html_table)
