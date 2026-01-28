import streamlit as st
import pandas as pd

# Set up Streamlit app
st.title("Mock SQL Table Query Runner")
st.write("This app demonstrates querying a mock SQL table and displaying results in a table.")

# Step 1: Create a Mock SQL Table
mock_data = {
    "employees": pd.DataFrame({
        "id": [1, 2, 3, 4],
        "name": ["Alice", "Bob", "Charlie", "Diana"],
        "age": [25, 35, 30, 28],
        "department": ["HR", "Finance", "IT", "HR"]
    }),
    "departments": pd.DataFrame({
        "dept_id": [1, 2, 3],
        "department_name": ["HR", "Finance", "IT"],
        "manager": ["Alice", "Bob", "Charlie"]
    }),
    "projects": pd.DataFrame({
        "project_id": [101, 102, 103],
        "project_name": ["Project A", "Project B", "Project C"],
        "department": ["HR", "Finance", "IT"]
    })
}

# Step 2: User Input
st.header("Enter Query Parameters")

# Dropdown for selecting a table
table_name = st.selectbox(
    "Choose a table to query:",
    options=list(mock_data.keys())  # Get table names from the mock data
)

# Text input for a filter condition
column_filter = st.text_input(
    "Filter condition (e.g., `age > 30` or `department == 'HR'`):",
    placeholder="Leave blank for no filter"
)

# Step 3: Query the Mock Table
if st.button("Run Query"):
    try:
        # Fetch the selected table as a DataFrame
        df = mock_data[table_name]
        
        # Apply the filter condition if provided
        if column_filter.strip():
            filtered_df = df.query(column_filter)
        else:
            filtered_df = df
        
        # Display results
        st.success("Query executed successfully!")
        st.write(f"Table: `{table_name}`")
        if not filtered_df.empty:
            st.dataframe(filtered_df)
        else:
            st.warning("No results found for the given filter.")
    except Exception as e:
        st.error(f"Error: {e}")
