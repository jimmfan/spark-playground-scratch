from cmislib import CmisClient
import os

# Replace with your FileNet CMIS repository URL
cmis_url = 'https://<filenet_cmis_url>/cmis/repositories'

# Replace with your credentials
username = 'your_username'
password = 'your_password'

# Create a CMIS client
client = CmisClient(cmis_url, username, password)

# Get the default repository
repo = client.defaultRepository

# Print repository info
print(f'Repository Name: {repo.name}')
print(f'Repository ID: {repo.id}')
print(f'Repository Description: {repo.description}')

# Function to list folder contents and retrieve files
def list_and_retrieve_files(folder, download_path):
    # Create download directory if it doesn't exist
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    # List the contents of the folder
    for obj in folder.getChildren():
        print(f'Name: {obj.name}, Type: {obj.properties["cmis:objectTypeId"]}')
        if obj.properties['cmis:objectTypeId'] == 'cmis:document':
            # Retrieve file content
            content_stream = obj.getContentStream()
            file_path = os.path.join(download_path, obj.name)
            with open(file_path, 'wb') as f:
                f.write(content_stream.read())
            print(f'Downloaded file: {file_path}')
        elif obj.properties['cmis:objectTypeId'] == 'cmis:folder':
            # Recursively list and retrieve files in subfolders
            subfolder = obj
            subfolder_path = os.path.join(download_path, obj.name)
            list_and_retrieve_files(subfolder, subfolder_path)

# Get the root folder
root_folder = repo.rootFolder

# Set the download path where files will be saved
download_path = './downloaded_files'

# List the contents of the root folder and retrieve files
list_and_retrieve_files(root_folder, download_path)
