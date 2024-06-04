import requests
import json

# Configuration details
base_url = 'https://your-filenet-server/navigator'
username = 'your-username'
password = 'your-password'
object_id = 'your-object-id'  # Replace with the actual object ID

# Endpoint for search
search_url = f'{base_url}/jaxrs/search'

# Authentication
auth = (username, password)

# Search payload (example payload to search by document ID)
search_payload = {
    "query": {
        "q": f"id:{object_id}"
    }
}

# Headers for the request
headers = {
    'Content-Type': 'application/json'
}

# Perform the search request
response = requests.post(search_url, auth=auth, headers=headers, data=json.dumps(search_payload))
if response.status_code == 200:
    search_results = response.json()
    if search_results['num_results'] > 0:
        document = search_results['documents'][0]  # Assuming the first result is the required document
        doc_id = document['id']
        doc_name = document['name']

        # Endpoint to fetch document content
        content_url = f'{base_url}/jaxrs/objects/{doc_id}/content'

        # Fetch document content
        response = requests.get(content_url, auth=auth, stream=True)
        if response.status_code == 200:
            content_disposition = response.headers.get('content-disposition')
            if content_disposition:
                filename = content_disposition.split('filename=')[1].strip('\"')
            else:
                filename = f'document_{doc_id}'

            with open(filename, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print(f"Document content written to file: {filename}")
        else:
            print("Failed to fetch document content:", response.status_code, response.text)
    else:
        print("No documents found with the specified ID.")
else:
    print("Failed to perform search:", response.status_code, response.text)
