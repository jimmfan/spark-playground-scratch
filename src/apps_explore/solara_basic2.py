import solara
import pandas as pd
import io
import base64

# Reactive state for uploaded file, filter text, and table data
uploaded_file = solara.reactive(None)
column_filter = solara.reactive("")
edited_df = solara.reactive(pd.DataFrame())

def load_file():
    """Loads the uploaded file into a DataFrame."""
    if uploaded_file.value:
        file_ext = uploaded_file.value.name.split(".")[-1].lower()
        if file_ext == "csv":
            df = pd.read_csv(uploaded_file.value)
        elif file_ext in ["xls", "xlsx"]:
            df = pd.read_excel(uploaded_file.value)
        else:
            solara.warning("Unsupported file format. Please upload a CSV or Excel file.")
            return
        edited_df.set(df)

def filter_data():
    """Filters the DataFrame based on the user input."""
    if column_filter.value and not edited_df.value.empty:
        filtered_df = edited_df.value[edited_df.value.apply(lambda row: row.astype(str).str.contains(column_filter.value, case=False, na=False).any(), axis=1)]
        edited_df.set(filtered_df)

def get_csv_download_link():
    """Generates a downloadable CSV file link for the filtered DataFrame."""
    csv_buffer = io.StringIO()
    edited_df.value.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    csv_encoded = base64.b64encode(csv_buffer.getvalue().encode()).decode()
    href = f'data:text/csv;base64,{csv_encoded}'
    return href

@solara.component
def EditableTableComponent():
    """Solara component for uploading, filtering, and editing a DataFrame."""
    solara.FileDropzone(label="Upload CSV or Excel file", on_file=uploaded_file.set)
    solara.Button("Load File", on_click=load_file)
    
    if not edited_df.value.empty:
        solara.InputText("Filter text", value=column_filter)
        solara.Button("Apply Filter", on_click=filter_data)
        
        solara.Markdown("### Editable Table")
        solara.DataFrame(edited_df.value, editable=True)
        
        solara.Button("Download CSV", on_click=lambda: solara.download(get_csv_download_link(), "filtered_data.csv"))

@solara.page("/")
def page():
    """Main page to run the Solara app."""
    solara.Title("Editable Data Table")
    EditableTableComponent()