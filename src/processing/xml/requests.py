import requests
from xml.etree import ElementTree

# Send PROPFIND request to WebDAV server
url = "http://your-webdav-server.com/webdav/documents/"
response = requests.request('PROPFIND', url, auth=('username', 'password'))

# Parse the XML response
tree = ElementTree.fromstring(response.content)

# Iterate through each response element
for item in tree.findall('{DAV:}response'):
    href = item.find('{DAV:}href').text
    # Extract metadata such as last modified and content length
    last_modified = item.find('.//{DAV:}getlastmodified').text
    content_length = item.find('.//{DAV:}getcontentlength').text
    print(f"File: {href}, Last Modified: {last_modified}, Size: {content_length} bytes")
