from io import BytesIO
import pandas as pd

from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext

site_url = "https://yourcompany.sharepoint.com/sites/yoursite"
username = "yourusername@yourcompany.com"
password = "yourpassword"

# Connect to SharePoint
ctx = ClientContext(site_url).with_credentials(UserCredential(username, password))
relative_url = "/sites/yoursite/Shared Documents/yourfolder"
folder = ctx.web.get_folder_by_server_relative_url(relative_url)

ctx.load(folder)
ctx.execute_query()

# Access and load files into memory
files = folder.files
ctx.load(files)
ctx.execute_query()

all_data = []

for file in files:
    if file.properties["Name"].endswith('.xlsx'):
        file_content = file.read()
        ctx.execute_query()
        # Load the file content into a BytesIO object
        excel_data = BytesIO(file_content.content)
        # Use pandas to read the Excel file
        df = pd.read_excel(excel_data)
        all_data.append(df)

import pandas as pd

# Concatenate all data into one DataFrame
# `ignore_index=True` will reindex the new DataFrame
# `sort=False` will keep the original column order, putting NaN where data is missing
aggregated_df = pd.concat(all_data, ignore_index=True, sort=False)

print(aggregated_df.head())

output_file_path = "aggregated_data.xlsx"
aggregated_df.to_excel(output_file_path, index=False)
