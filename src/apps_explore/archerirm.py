import requests

# Archer API details
ARCHER_BASE_URL = "https://your-archer-instance.com"
TOKEN_ENDPOINT = "/api/core/security/login"
SEARCH_ENDPOINT = "/api/core/content/12345"  # Replace with actual App ID for "plans"

# User Credentials
USERNAME = "your_username"
PASSWORD = "your_password"
INSTANCE = "your_instance_name"

# Authenticate to get session token
auth_payload = {
    "Username": USERNAME,
    "Password": PASSWORD,
    "InstanceName": INSTANCE
}

session = requests.Session()

try:
    auth_response = session.post(f"{ARCHER_BASE_URL}{TOKEN_ENDPOINT}", json=auth_payload)
    auth_response.raise_for_status()  # Raise error for bad response

    session_token = auth_response.headers.get("Authorization")  # Extract token

    if session_token:
        print("Authentication successful. Token received.")

        # Headers with authentication token
        headers = {
            "Authorization": session_token,
            "Content-Type": "application/json"
        }

        # Define the search filter for "plans"
        search_payload = {
            "Fields": [1234, 5678],  # Replace with actual field IDs for Plan Name, etc.
            "Filter": {
                "Operator": "And",
                "Filters": [
                    {
                        "FieldId": 1234,  # Replace with the field ID for Plan Name
                        "Operator": "Contains",
                        "Value": "Your Plan Name"
                    }
                ]
            }
        }

        # Make the request
        search_response = session.post(f"{ARCHER_BASE_URL}{SEARCH_ENDPOINT}", headers=headers, json=search_payload)

        if search_response.status_code == 200:
            print("Search successful. Plans found:", search_response.json())
        else:
            print(f"Search failed. Status Code: {search_response.status_code}, Response: {search_response.text}")

    else:
        print("Failed to retrieve authentication token.")

except requests.exceptions.RequestException as e:
    print(f"Error: {e}")