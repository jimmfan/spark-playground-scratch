import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode

# Example dataset
tables = [
    {"source": "team pikachu", "process": f"process name {i}", "owner": owner}
    for i, owner in enumerate(["Ash", "Misty", "Brock"] * 3 + ["James", "Meowth", "Jesse"] * 2)
]

st.set_page_config(page_title="Streamlit Dashboard", layout="wide")
st.title("Streamlit Dashboard")

# Initialize session state with original data if not already set
if "original_df" not in st.session_state:
    st.session_state.original_df = pd.DataFrame(tables)

if "final_df" not in st.session_state:
    st.session_state.final_df = pd.DataFrame()

if "filter_values" not in st.session_state:
    st.session_state.filter_values = {col: [] for col in ["source", "process", "owner"]}

# Define filterable columns
filter_columns = {
    "source": "Filter by Source",
    "process": "Filter by Process",
    "owner": "Filter by Owner"
}

# Clear all filters and reset df_filtered
if st.button("Clear All Filters"):
    st.session_state.filter_values = {col: [] for col in filter_columns.keys()}  # Reset filters
    st.session_state.df_filtered = st.session_state.original_df.copy()  # Reset data

# Create columns dynamically based on the number of filters
filter_values = {}
cols = st.columns(len(filter_columns))

# Generate filter widgets dynamically
for (col_name, label), col in zip(filter_columns.items(), cols):
    unique_values = st.session_state.original_df[col_name].unique()
    filter_values[col_name] = col.multiselect(
        label, unique_values, default=st.session_state.filter_values[col_name]
    )

# Save selections in session state
st.session_state.filter_values = filter_values

# Apply filters dynamically unless filters are cleared
if not any(st.session_state.filter_values.values()):
    st.session_state.df_filtered = st.session_state.original_df.copy()
else:
    df_filtered = st.session_state.original_df.copy()
    for col_name, selected_values in filter_values.items():
        if selected_values:  # Apply filter only if a selection is made
            df_filtered = df_filtered[df_filtered[col_name].isin(selected_values)]
    st.session_state.df_filtered = df_filtered

# Display filtered or unfiltered data
df_filtered = st.session_state.df_filtered
st.write(df_filtered)