import streamlit as st
import pandas as pd
from io import BytesIO

# Set up Streamlit app
st.title("Dynamic Query Runner with File Upload and Download")
st.write("Upload an Excel file as your mock dataset, query it, and download the filtered results.")

# Step 1: File Uploader for Dataset
st.header("Upload Your Dataset")
uploaded_file = st.file_uploader(
    "Drag and drop a CSV or Excel file here:",
    type=["csv", "xlsx"]
)

# id,name,age,department
# 1,Alice,25,HR
# 2,Bob,35,Finance
# 3,Charlie,30,IT
# 4,Diana,28,HR
# 5,Eva,40,Finance


if uploaded_file:
    try:
        # Step 2: Determine file type and read data
        if uploaded_file.name.endswith(".xlsx"):
            # Read Excel file into a dictionary of DataFrames (one per sheet)
            mock_data = pd.read_excel(uploaded_file, sheet_name=None)
        elif uploaded_file.name.endswith(".csv"):
            # Read CSV file into a single DataFrame
            df = pd.read_csv(uploaded_file)
            mock_data = {"table": df}  # Create a single table dictionary

        # Step 3: Display available tables
        st.success(f"Successfully loaded file: {uploaded_file.name}")
        st.write("Available tables:", list(mock_data.keys()))  # List all tables (or sheets)

        # Step 4: Query Parameters
        st.header("Enter Query Parameters")

        # Dropdown for selecting a table
        table_name = st.selectbox(
            "Choose a table to query:",
            options=list(mock_data.keys())  # Options for all table names
        )

        # Text input for filter condition
        column_filter = st.text_input(
            "Filter condition (e.g., `age > 30` or `department == 'HR'`):",
            placeholder="Leave blank for no filter"
        )

        # Step 5: Query the Selected Table
        if st.button("Run Query"):
            try:
                # Fetch the selected table as a DataFrame
                df = mock_data[table_name]
                
                # Apply filter condition if provided
                if column_filter.strip():
                    filtered_df = df.query(column_filter)
                else:
                    filtered_df = df
                
                # Display results
                st.success("Query executed successfully!")
                st.write(f"Table: `{table_name}`")
                if not filtered_df.empty:
                    st.dataframe(filtered_df)
                    
                    # Step 6: Download Filtered Results as CSV
                    csv = filtered_df.to_csv(index=False)
                    st.download_button(
                        label="Download Filtered Results as CSV",
                        data=csv,
                        file_name=f"{table_name}_filtered.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("No results found for the given filter.")
            except Exception as e:
                st.error(f"Error: {e}")
    except Exception as e:
        st.error(f"Error loading file: {e}")
else:
    st.info("Please upload a CSV or Excel file to begin.")

