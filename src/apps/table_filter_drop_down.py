import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode

# Define multiple static Pandas DataFrames (representing different tables)
tables = {
    "Customers": pd.DataFrame({
        'CustomerID': [101, 102, 103, 104],
        'Name': ['Alice', 'Bob', 'Charlie', 'David'],
        'Location': ['NY', 'CA', 'TX', 'FL']
    }),
    "Orders": pd.DataFrame({
        'OrderID': [5001, 5002, 5003, 5004],
        'CustomerID': [101, 102, 103, 104],
        'Product': ['Laptop', 'Phone', 'Tablet', 'Monitor']
    }),
    "Products": pd.DataFrame({
        'ProductID': [1, 2, 3, 4],
        'ProductName': ['Laptop', 'Phone', 'Tablet', 'Monitor'],
        'Price': [1000, 800, 600, 400]
    })
}

# Initialize session state for deleted rows and unioned rows
if "deleted_rows" not in st.session_state:
    st.session_state.deleted_rows = []

if "updated_df" not in st.session_state:
    st.session_state.updated_df = pd.DataFrame(columns=["ID", "Name", "Age"])

st.title("Editable Table with Row Deletion, Row Reordering & Data Union")

### AG-GRID: Editable Table with Delete Button ###
# JavaScript for delete button
delete_button_js = JsCode("""
class DeleteButtonRenderer {
    init(params) {
        this.params = params;
        this.eGui = document.createElement('div');
        this.eGui.innerHTML = '<button style="color: red; cursor: pointer;">❌ Delete</button>';
        this.eGui.querySelector('button').addEventListener('click', () => {
            window.deletedRow = params.data;  // Store deleted row in global JS variable
            params.api.applyTransaction({ remove: [params.data] });
        });
    }
    getGui() {
        return this.eGui;
    }
}
""")

# GridOptionsBuilder
gb = GridOptionsBuilder.from_dataframe(st.session_state.updated_df)

# Add delete button as the first column
gb.configure_column(
    "Delete",
    cellRenderer=delete_button_js,
    width=120,
    pinned='left'
)

# Enable row dragging
gb.configure_column("ID", rowDrag=True, width=60)

# Make specific columns editable
gb.configure_columns(["Name", "Age"], editable=True)

# Build grid options
grid_options = gb.build()

# Display AgGrid
grid_response = AgGrid(
    st.session_state.updated_df,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.MODEL_CHANGED,
    allow_unsafe_jscode=True
)

# Capture updated DataFrame
st.session_state.updated_df = pd.DataFrame(grid_response['data'])

# Display updated DataFrame
st.write("Updated DataFrame:", st.session_state.updated_df)

### FILTERING & UNIONING NEW DATA ###
st.subheader("Union Data from Other Tables")

# Dropdown for table selection
selected_table = st.selectbox("Select a Table", list(tables.keys()))

# Display selected table
df_selected = tables[selected_table]

# Dropdown for column selection (based on selected table)
selected_column = st.selectbox("Select a Column to Filter", df_selected.columns)

# Dropdown for values (based on selected column)
selected_values = st.multiselect("Select Values to Filter", df_selected[selected_column].unique())

# Button to add selected rows to updated_df
if st.button("Add Filtered Rows"):
    filtered_rows = df_selected[df_selected[selected_column].isin(selected_values)]
    
    # Append filtered rows to updated_df
    if not filtered_rows.empty:
        st.session_state.updated_df = pd.concat([st.session_state.updated_df, filtered_rows], ignore_index=True)
        st.write("Updated DataFrame After Adding Rows:", st.session_state.updated_df)
    else:
        st.warning("No matching rows found!")

### UNDO DELETE FUNCTION ###
if "deletedRow" in st.session_state and st.session_state.deletedRow:
    if st.button("Undo Last Deletion"):
        restored_row = st.session_state.deletedRow
        st.session_state.updated_df = pd.concat([pd.DataFrame([restored_row]), st.session_state.updated_df], ignore_index=True)
        st.session_state.deletedRow = None  # Clear the stored row
        st.write("Row restored!")

st.write("Undo functionality: Click 'Delete' on a row and use the 'Undo Last Deletion' button to restore it.")
