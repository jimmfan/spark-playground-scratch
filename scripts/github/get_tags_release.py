import requests

# Replace 'your_token' with your GitHub Personal Access Token
headers = {
    'Authorization': 'token your_token',
    'Accept': 'application/vnd.github.v3+json',
}

# List of your repositories in the format 'owner/repo'
repositories = [
    'owner/repo1',
    'owner/repo2',
    # Add more as needed
]

def get_latest_release(repo):
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()['tag_name']  # or ['name'] for the release name
    else:
        return "No release found or access denied"

for repo in repositories:
    latest_release = get_latest_release(repo)
    print(f"{repo}: {latest_release}")
