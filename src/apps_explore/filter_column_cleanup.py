# Define filterable columns
filter_columns = {
    "source": "Filter by Source",
    "process": "Filter by Process",
    "owner": "Filter by Owner"
}

# Create columns dynamically based on the number of filters
filter_values = {}
cols = st.columns(len(filter_columns))

# Generate filter widgets dynamically
for (col_name, label), col in zip(filter_columns.items(), cols):
    unique_values = st.session_state.original_df[col_name].unique()
    filter_values[col_name] = col.multiselect(label, unique_values)

# Apply filters dynamically
df_filtered = st.session_state.original_df.copy()
for col_name, selected_values in filter_values.items():
    if selected_values:  # Apply filter only if a selection is made
        df_filtered = df_filtered[df_filtered[col_name].isin(selected_values)]