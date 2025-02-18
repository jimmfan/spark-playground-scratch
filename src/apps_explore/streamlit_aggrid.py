import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode

# Sample DataFrame
df = pd.DataFrame({
    'ID': [1, 2, 3, 4],
    'Name': ['Alice', 'Bob', 'Charlie', 'David'],
    'Age': [25, 30, 35, 40]
})

st.title("Editable Table with Inline Row Deletion")

# JavaScript callback to handle row deletion
delete_row_js = JsCode("""
function(params) {
    var rowIndex = params.node.rowIndex;
    params.api.applyTransaction({ remove: [params.data] });
}
""")

# GridOptionsBuilder for AgGrid
gb = GridOptionsBuilder.from_dataframe(df)

# Make specific columns editable
gb.configure_columns(["Name", "Age"], editable=True)

# Add a delete button to each row
gb.configure_column(
    "Delete",
    cellRenderer=JsCode("""
    class DeleteButtonRenderer {
        init(params) {
            this.params = params;
            this.eGui = document.createElement('div');
            this.eGui.innerHTML = '<button style="color: red; cursor: pointer;">Delete</button>';
            this.eGui.querySelector('button').addEventListener('click', () => {
                params.api.applyTransaction({ remove: [params.data] });
            });
        }
        getGui() {
            return this.eGui;
        }
    }
    """),
    width=100
)

grid_options = gb.build()

# Display AgGrid with row editing and deletion enabled
grid_response = AgGrid(
    df,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.MODEL_CHANGED,
    allow_unsafe_jscode=True
)

# Capture updated DataFrame
updated_df = pd.DataFrame(grid_response['data'])

# Display updated DataFrame after edits/deletion
st.write("Updated DataFrame:", updated_df)