import solara
import pandas as pd
from io import BytesIO

# Application state
uploaded_file = solara.reactive(None)
mock_data = solara.reactive({})
table_name = solara.reactive("")
column_filter = solara.reactive("")
filtered_df = solara.reactive(pd.DataFrame())
edited_df = solara.reactive(pd.DataFrame())


@solara.component
def FileUploader():
    """File uploader component"""
    def handle_upload(file):
        try:
            file_bytes = file["content"]
            file_name = file["name"]

            if file_name.endswith(".xlsx"):
                data = pd.read_excel(BytesIO(file_bytes), sheet_name=None)  # Multiple sheets
            elif file_name.endswith(".csv"):
                df = pd.read_csv(BytesIO(file_bytes))  # Single table
                data = {"table": df}

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
    if solara.Button("Run Query", on_click=lambda: execute_query()):
        if not filtered_df.value.empty:
            solara.Info("Query executed successfully!")
            solara.Markdown(f"### Table: `{table_name.value}`")
            EditableTable()
            DownloadButton()


def execute_query():
    """Executes the query on the selected table"""
    try:
        if table_name.value and table_name.value in mock_data.value:
            df = mock_data.value[table_name.value]
            if column_filter.value.strip():
                filtered_df.set(df.query(column_filter.value))
            else:
                filtered_df.set(df)
    except Exception as e:
        solara.error(f"Error: {e}")


@solara.component
def EditableTable():
    """Editable table using Solara's DataTable component"""
    if not filtered_df.value.empty:
        # Convert DataFrame to a list of dictionaries for editing
        data_records = solara.reactive(filtered_df.value.to_dict(orient="records"))

        def update_data(updated_records):
            """Update DataFrame when table is edited"""
            try:
                updated_df = pd.DataFrame(updated_records)
                edited_df.set(updated_df)  # Save the modified DataFrame
            except Exception as e:
                solara.error(f"Error updating table: {e}")

        solara.Info("Edit the filtered data below:")
        solara.DataTable(items=data_records.value, on_change=update_data)


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
def App():
    """Main Solara application layout"""
    solara.Title("Dynamic Query Runner with Editable Table")
    solara.Markdown("Upload an Excel or CSV file, query it, edit the results, and download the modified data.")

    FileUploader()
    if uploaded_file.value:
        solara.Success(f"Successfully loaded file: {uploaded_file.value}")
        TableSelector()
        QueryInput()
        RunQuery()


# Run the app
App()