import requests

# Archer IRM API details
ARCHER_BASE_URL = "https://your-archer-instance.com"
AUTH_ENDPOINT = "/api/core/security/login"
PING_ENDPOINT = "/api/core/system/info"

# API credentials
USERNAME = "your_username"
PASSWORD = "your_password"
INSTANCE = "your_instance_name"

# Headers for authentication
auth_payload = {
    "Username": USERNAME,
    "Password": PASSWORD,
    "InstanceName": INSTANCE
}

# Start a session
session = requests.Session()

# Authenticate with Archer
auth_response = session.post(f"{ARCHER_BASE_URL}{AUTH_ENDPOINT}", json=auth_payload)

if auth_response.status_code == 200:
    print("Authentication successful.")
    
    # Now ping the system info endpoint
    ping_response = session.get(f"{ARCHER_BASE_URL}{PING_ENDPOINT}")

    if ping_response.status_code == 200:
        print("Ping successful. System Info:", ping_response.json())
    else:
        print(f"Ping failed. Status Code: {ping_response.status_code}, Response: {ping_response.text}")

else:
    print(f"Authentication failed. Status Code: {auth_response.status_code}, Response: {auth_response.text}")