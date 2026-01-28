import requests

# Configuration details
base_url = 'https://your-filenet-server/navigator'
username = 'your-username'
password = 'your-password'
object_id = 'your-object-id'  # Replace with the actual object ID

# Endpoint to fetch document details
details_url = f'{base_url}/jaxrs/objects/{object_id}'

# Endpoint to fetch document content
content_url = f'{base_url}/jaxrs/objects/{object_id}/content'

# Authentication
auth = (username, password)

# Fetch document details
response = requests.get(details_url, auth=auth)
if response.status_code == 200:
    document_details = response.json()
    print("Document Details:", document_details)
else:
    print("Failed to fetch document details:", response.status_code, response.text)

# Fetch document content
response = requests.get(content_url, auth=auth, stream=True)
if response.status_code == 200:
    content_disposition = response.headers.get('content-disposition')
    if content_disposition:
        filename = content_disposition.split('filename=')[1].strip('\"')
    else:
        filename = f'document_{object_id}'

    with open(filename, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
    print(f"Document content written to file: {filename}")
else:
    print("Failed to fetch document content:", response.status_code, response.text)
