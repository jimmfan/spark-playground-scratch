import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode

# JavaScript code for row drag and drop
onRowDragEnd = JsCode("""
function onRowDragEnd(e) {
    console.log('Row dragged', e);
}
""")

getRowNodeId = JsCode("""
function getRowNodeId(data) {
    return data.id;
}
""")

onGridReady = JsCode("""
function onGridReady() {
    gridOptions.api.forEachNode(function(node, index) {
        node.data.id = index;
    });
    gridOptions.api.setRowData(gridOptions.rowData);
}
""")

onRowDragMove = JsCode("""
function onRowDragMove(event) {
    var movingNode = event.node;
    var overNode = event.overNode;
    var rowNeedsToMove = movingNode !== overNode;

    if (rowNeedsToMove) {
        var movingData = movingNode.data;
        var overData = overNode.data;
        var fromIndex = gridOptions.rowData.indexOf(movingData);
        var toIndex = gridOptions.rowData.indexOf(overData);

        gridOptions.rowData.splice(fromIndex, 1);
        gridOptions.rowData.splice(toIndex, 0, movingData);

        gridOptions.api.setRowData(gridOptions.rowData);
        gridOptions.api.clearFocusedCell();
    }
}
""")

data = {
    'table1': {
        "id": {i: i + 1 for i in range(0, 5)},
        "process": {i: f"process name {i + 1}" for i in range(0, 5)},
        "owner": {i: f"owner name {i + 1}" for i in range(0, 5)},
    },
    'table2': {
        "id": {i: i + 1 for i in range(0, 5)},
        "process": {i: f"process name {i + 1}" for i in range(0, 5)},
        "owner": {i: f"owner name {i + 1}" for i in range(0, 5)},
    },
}


df = pd.DataFrame(data)

# Configure grid options
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_default_column(rowDrag=True, rowDragManaged=True)
gb.configure_grid_options(
    onRowDragEnd=onRowDragEnd,
    getRowNodeId=getRowNodeId,
    onGridReady=onGridReady,
    onRowDragMove=onRowDragMove,
    animateRows=True
)
gridOptions = gb.build()

# Display the grid
grid_response = AgGrid(
    df,
    gridOptions=gridOptions,
    update_mode=GridUpdateMode.MANUAL,
    allow_unsafe_jscode=True
)

# Updated DataFrame after reordering
updated_df = grid_response['data']
st.write(updated_df)


# Initialize session state for deleted rows
if "deleted_rows" not in st.session_state:
    st.session_state.deleted_rows = []

# Sample DataFrame
df = pd.DataFrame({
    'ID': [1, 2, 3, 4],
    'Name': ['Alice', 'Bob', 'Charlie', 'David'],
    'Age': [25, 30, 35, 40]
})

st.title("Editable Table with Undo Row Deletion & Row Reordering")

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

# JavaScript for reordering rows
row_drag_js = JsCode("""
function(params) {
    if (params.node.rowPinned) {
        return null;
    }
    return '<span style="cursor: grab;">⬍</span>';
}
""")

# GridOptionsBuilder
gb = GridOptionsBuilder.from_dataframe(df)

# Add delete button as the first column
gb.configure_column(
    "Delete",
    cellRenderer=delete_button_js,
    width=120,
    pinned='left'
)

# Enable row dragging for reordering
gb.configure_column("ID", rowDrag=True, width=60, cellRenderer=row_drag_js)

# Make specific columns editable
gb.configure_columns(["Name", "Age"], editable=True)

# Build grid options
grid_options = gb.build()

# Display AgGrid
grid_response = AgGrid(
    df,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.MODEL_CHANGED,
    allow_unsafe_jscode=True
)

# Capture updated DataFrame
updated_df = pd.DataFrame(grid_response['data'])

# Show updated DataFrame
st.write("Updated DataFrame:", updated_df)

# Undo Last Deleted Row
if "deletedRow" in st.session_state and st.session_state.deletedRow:
    if st.button("Undo Last Deletion"):
        restored_row = st.session_state.deletedRow
        updated_df = pd.concat([pd.DataFrame([restored_row]), updated_df], ignore_index=True)
        st.session_state.deletedRow = None  # Clear the stored row
        st.write("Row restored!")

st.write("Undo functionality: Click 'Delete' on a row and use the 'Undo Last Deletion' button to restore it.")