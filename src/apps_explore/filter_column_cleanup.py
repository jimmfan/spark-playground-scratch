import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode

preselect_js = JsCode("""
function onFirstDataRendered(params) {
    params.api.forEachNode(node => node.setSelected(true));
}
""")

# Example dataset
tables = [
    {"source": "team pikachu", "process": f"process name {i}", "owner": owner}
    for i, owner in enumerate(["Ash", "Misty", "Brock"] * 3 + ["James", "Meowth", "Jesse"] * 2)
]

st.set_page_config(page_title="Streamlit Dashboard", layout="wide")
st.title("Streamlit Dashboard")

# Initialize session state with original data
if "original_df" not in st.session_state:
    st.session_state.original_df = pd.DataFrame(tables)

if "final_df" not in st.session_state:
    st.session_state.final_df = pd.DataFrame()

if "filter_values" not in st.session_state:
    st.session_state.filter_values = {col: [] for col in ["source", "process", "owner"]}

if "df_filtered" not in st.session_state:
    st.session_state.df_filtered = st.session_state.original_df.copy()

# Define filterable columns
filter_columns = {
    "source": "Filter by Source",
    "process": "Filter by Process",
    "owner": "Filter by Owner"
}

# Create columns dynamically for filters
filter_values = {}
cols = st.columns(len(filter_columns))

for (col_name, label), col in zip(filter_columns.items(), cols):
    unique_values = st.session_state.original_df[col_name].unique()
    filter_values[col_name] = col.multiselect(
        label, unique_values, default=st.session_state.filter_values[col_name]
    )

# Store selections in session state
st.session_state.filter_values = filter_values

# Buttons: Apply Filters & Clear All Filters
col1, col2 = st.columns(2)

with col1:
    if st.button("Apply Filters"):
        df_filtered = st.session_state.original_df.copy()
        for col_name, selected_values in filter_values.items():
            if selected_values:
                df_filtered = df_filtered[df_filtered[col_name].isin(selected_values)]
        st.session_state.df_filtered = df_filtered  # Save filtered data
        st.session_state.refresh_grid = True  # Trigger AgGrid refresh

with col2:
    if st.button("Clear All Filters"):
        st.session_state.filter_values = {col: [] for col in filter_columns.keys()}
        st.session_state.df_filtered = st.session_state.original_df.copy()
        st.session_state.refresh_grid = True  # Trigger AgGrid refresh

# Display AgGrid with `preselect_js`
df_filtered = st.session_state.df_filtered
if not df_filtered.empty:
    gb = GridOptionsBuilder.from_dataframe(df_filtered)

    gb.configure_selection(
        selection_mode="multiple", use_checkbox=True, header_checkbox=True
    )

    gb.configure_grid_options(
        domLayout="autoHeight",
        animateRows=True,
        enableSorting=True,
        enableFilter=True,
        pagination=True,
        paginationPageSize=50,
        onFirstDataRendered=preselect_js if "refresh_grid" in st.session_state else None,
    )

    gridOptions = gb.build()

    grid_response = AgGrid(
        df_filtered,
        gridOptions=gridOptions,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        allow_unsafe_jscode=True,
        key=str(st.session_state.refresh_grid),  # Force grid refresh
    )

    selected_rows = grid_response["selected_rows"]

    if any(selected_rows):
        st.write("Selected Rows:", selected_rows)

# Reset refresh state after rendering
st.session_state.refresh_grid = False