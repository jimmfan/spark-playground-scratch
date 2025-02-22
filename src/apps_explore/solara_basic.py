import os
import io
import solara
import pandas as pd

# Reactive state variables
uploaded_file = solara.reactive(None)
mock_data = solara.reactive({})
table_name = solara.reactive("")
column_filter = solara.reactive("")
filtered_df = solara.reactive(pd.DataFrame())  # Ensure UI updates when changed
edited_df = solara.reactive(pd.DataFrame())


@solara.component
def FileUploader():
    """File uploader component"""
    def handle_upload(file):
        try:
            file_bytes = io.BytesIO(file["data"])
            file_name = file["name"]

            table_name, file_ext = os.path.splitext(file_name)

            if file_ext == ".xlsx":
                data = pd.read_excel(file_bytes, sheet_name=None)  # Multiple sheets
            elif file_ext == ".csv":
                df = pd.read_csv(file_bytes)  # Single table
                data = {table_name: df}

            uploaded_file.set(file_name)
            mock_data.set(data)
            table_name.set(list(data.keys())[0] if data else "")

        except Exception as e:
            solara.error(f"Error loading file: {e}")

    solara.FileDrop(on_file=handle_upload, label="Upload a CSV or Excel file")


@solara.component
def TableSelector():
    """Table selection dropdown"""
    if mock_data.value:
        solara.Select(
            label="Choose a table to query:",
            values=list(mock_data.value.keys()),
            value=table_name,
        )


@solara.component
def QueryInput():
    """Text input for filter condition"""
    solara.InputText("Filter condition (e.g., `age > 30` or `department == 'HR'`):", value=column_filter)


@solara.component
def RunQuery():
    """Run query and display results"""
    def execute_query():
        """Executes the query on the selected table and triggers UI update"""
        try:
            if table_name.value and table_name.value in mock_data.value:
                df = mock_data.value[table_name.value]
                if column_filter.value.strip():
                    filtered_df.set(df.query(column_filter.value))  # Set reactive variable
                else:
                    filtered_df.set(df)  # If no filter, use full table
        except Exception as e:
            solara.error(f"Error: {e}")

    solara.Button("Run Query", on_click=execute_query)

    # Auto-refresh UI when filtered_df changes
    @solara.use_effect(dependencies=[filtered_df])
    def update_ui():
        pass  # This will force Solara to refresh the component

    # Show results if available
    if not filtered_df.value.empty:
        solara.Info("Query executed successfully!")
        solara.Markdown(f"### Table: `{table_name.value}`")
        EditableTable()
        DownloadButton()


@solara.component
def EditableTable():
    """Editable DataFrame component"""
    if not filtered_df.value.empty:
        df = solara.DataFrame(filtered_df.value)
        solara.Info("Edit the filtered data below:")
        return df


@solara.component
def DownloadButton():
    """Download modified data"""
    if not edited_df.value.empty:
        csv_data = edited_df.value.to_csv(index=False).encode("utf-8")
        solara.DownloadButton(
            label="Download Edited Results as CSV",
            filename=f"{table_name.value}_edited.csv",
            data=csv_data,
        )


@solara.component
def Page():
    """Main Solara application layout"""
    solara.Title("Dynamic Query Runner with Editable Table")
    solara.Markdown("Upload an Excel or CSV file, query it, edit the results, and download the modified data.")

    FileUploader()
    if uploaded_file.value:
        solara.Success(f"Successfully loaded file: {uploaded_file.value}")
        TableSelector()
        QueryInput()
        RunQuery()
