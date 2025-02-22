import os
import io
import solara
import pandas as pd
import tkinter as tk
from tkinter import filedialog

# Reactive state variables
uploaded_file = solara.reactive(None)
mock_data = solara.reactive({})
table_name = solara.reactive("")
column_filter = solara.reactive("")
filtered_df = solara.reactive(pd.DataFrame())  # Ensure UI updates when changed
edited_df = solara.reactive(pd.DataFrame())

def open_file_dialog():
    """Opens the native file explorer"""
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    file_path = filedialog.askopenfilename(
        filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("All files", "*.*")]
    )
    if file_path:
        handle_select(file_path)

def handle_select(file_path):
    """Handles file selection"""
    try:
        file_name = os.path.basename(file_path)
        table_name_value, file_ext = os.path.splitext(file_name)

        if file_ext == ".xlsx":
            data = pd.read_excel(file_path, sheet_name=None)  # Multiple sheets
        elif file_ext == ".csv":
            df = pd.read_csv(file_path)  # Single table
            data = {table_name_value: df}

        uploaded_file.set(file_name)
        mock_data.set(data)
        table_name.set(list(data.keys())[0] if data else "")

    except Exception as e:
        solara.error(f"Error loading file: {e}")

@solara.component
def FileUploader():
    """File uploader component supporting both drag-and-drop and file browser"""

    def handle_upload(file):
        """Handles file upload from drag-and-drop"""
        try:
            file_bytes = io.BytesIO(file["data"])
            file_name = file["name"]

            table_name_value, file_ext = os.path.splitext(file_name)

            if file_ext == ".xlsx":
                data = pd.read_excel(file_bytes, sheet_name=None)  # Multiple sheets
            elif file_ext == ".csv":
                df = pd.read_csv(file_bytes)  # Single table
                data = {table_name_value: df}

            uploaded_file.set(file_name)
            mock_data.set(data)
            table_name.set(list(data.keys())[0] if data else "")

        except Exception as e:
            solara.error(f"Error loading file: {e}")

    # UI Components
    solara.Markdown("### Upload a file using either method:")
    
    # Drag-and-Drop Upload
    solara.FileDrop(
        on_file=handle_upload, 
        label="Drag and drop a CSV or Excel file here, or click to select one"
    )

    # Open Native File Dialog
    solara.Button("Browse Files", on_click=open_file_dialog)


@solara.component
def QueryInput():
    """Text input for filter condition with Enter key support"""
    user_input = solara.reactive("")  # Store user input separately

    def handle_change(new_value):
        """Handles text input changes"""
        user_input.set(new_value)  # Update reactive state

    solara.InputText(
        "Filter condition (e.g., `age > 30` or `department == 'HR'`):",
        value=user_input,
        on_value=handle_change,  # Detect text changes
    )

    # Detect when Enter is pressed
    @solara.use_effect(dependencies=[user_input])
    def detect_enter():
        if user_input.value.endswith("\n"):  # If Enter is detected
            column_filter.set(user_input.value.strip())  # Update main filter
            run_query()  # Run the query


@solara.component
def RunQuery():
    """Run query and display results"""
    
    def run_query():
        """Executes the query on the selected table and updates UI"""
        try:
            if table_name.value and table_name.value in mock_data.value:
                df = mock_data.value[table_name.value]
                if column_filter.value.strip():
                    filtered_df.set(df.query(column_filter.value))  # Set reactive variable
                else:
                    filtered_df.set(df)  # If no filter, use full table
        except Exception as e:
            solara.error(f"Error: {e}")

    # Include QueryInput so it can listen for Enter key
    QueryInput()

    # Button for manual query execution
    solara.Button("Run Query", on_click=run_query)

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
