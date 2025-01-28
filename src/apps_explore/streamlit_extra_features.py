import streamlit as st
import pandas as pd
from io import BytesIO

# Set up Streamlit app
st.title("Dynamic Query Runner with File Upload and Download")
st.write("Upload an Excel file as your mock dataset, query it, and download the filtered results.")

# Step 1: File Uploader for Mock Dataset
st.header("Upload Your Dataset")
uploaded_file = st.file_uploader(
    "Drag and drop an Excel file here to use it as your mock dataset.",
    type=["xlsx"]
)

if uploaded_file:
    try:
        # Read Excel file into a dictionary of DataFrames
        mock_data = pd.read_excel(uploaded_file, sheet_name=None)  # Load all sheets as tables
        st.success(f"Successfully loaded {len(mock_data)} tables from {uploaded_file.name}!")
        
        # Display available tables
        st.write("Available tables:", list(mock_data.keys()))

        # Step 2: User Input for Query Parameters
        st.header("Enter Query Parameters")

        # Dropdown for selecting a table
        table_name = st.selectbox(
            "Choose a table to query:",
            options=list(mock_data.keys())  # Get table names from the uploaded file
        )

        # Text input for a filter condition
        column_filter = st.text_input(
            "Filter condition (e.g., `age > 30` or `department == 'HR'`):",
            placeholder="Leave blank for no filter"
        )

        # Step 3: Query the Selected Table
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
                    
                    # Step 4: Download Filtered Results as CSV
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
    st.info("Please upload an Excel file to begin.")
