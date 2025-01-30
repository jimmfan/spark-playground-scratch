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
