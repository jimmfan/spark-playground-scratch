#!/bin/bash

# List your repository directories here
repos=(
    /path/to/repo1
    /path/to/repo2
    # Add more as needed
)

for repo in "${repos[@]}"; do
    echo "Checking latest tag in $repo..."
    cd "$repo"
    # Fetch tags from remote
    git fetch --tags
    # Get the latest tag name
    latestTag=$(git describe --tags `git rev-list --tags --max-count=1`)
    echo "Latest tag: $latestTag"
done
