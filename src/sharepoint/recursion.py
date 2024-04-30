import requests
from requests_ntlm import HttpNtlmAuth
from urllib.parse import quote
from io import BytesIO
import pandas as pd

# Configuration
site_url = "https://yourcompany.sharepoint.com/sites/yoursite"
base_folder_url = "/sites/yoursite/Shared Documents/Reports 2024"
site_encoded_url = quote(base_folder_url)
base_api_url = f"{site_url}/_api/web/GetFolderByServerRelativeUrl"

# Authentication setup
session = requests.Session()
session.auth = HttpNtlmAuth('yourusername@yourcompany.com', 'yourpassword')

# List to store data frames
all_data = []

def fetch_files_in_folder(folder_url):
    """ Recursively fetch files from folder and subfolders """
    encoded_folder_url = quote(folder_url)
    api_url = f"{base_api_url}('{encoded_folder_url}')"
    response = session.get(api_url + "/Files", headers={'Accept': 'application/json;odata=verbose'})
    data = response.json()

    for file_info in data['d']['results']:
        file_name = file_info['Name']
        if file_name.endswith('.xlsx'):
            file_url = file_info['__metadata']['uri'] + "/$value"

            # Download the Excel file
            response = session.get(file_url, stream=True)
            if response.ok:
                excel_data = BytesIO(response.content)
                df = pd.read_excel(excel_data)
                all_data.append(df)
            else:
                print(f"Failed to download {file_name}")
    
    # Check for subfolders and recurse into them
    response = session.get(api_url + "/Folders", headers={'Accept': 'application/json;odata=verbose'})
    subfolders = response.json()
    for folder in subfolders['d']['results']:
        subfolder_url = folder['ServerRelativeUrl']
        fetch_files_in_folder(subfolder_url)

# Start the recursion from the base folder
fetch_files_in_folder(base_folder_url)

# all_data now contains all data frames from Excel files in the folder and its subfolders
