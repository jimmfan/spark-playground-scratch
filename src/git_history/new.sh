#!/bin/bash

# Define variables
BITBUCKET_REPO_URL="your_bitbucket_repo_url"
GITHUB_REPO_URL="your_github_repo_url"
BITBUCKET_CLONE_DIR="original-repo.git"
GITHUB_CLONE_DIR="new-repo"

# Clone the original Bitbucket repository as a mirror
git clone --mirror $BITBUCKET_REPO_URL $BITBUCKET_CLONE_DIR

# Navigate to the cloned Bitbucket repository directory
cd $BITBUCKET_CLONE_DIR

# Filter out large files (>100MB)
git filter-repo --path-glob '**/*' --strip-blobs-bigger-than 100M

# Navigate back to the parent directory
cd ..

# Clone the new GitHub repository
git clone $GITHUB_REPO_URL $GITHUB_CLONE_DIR

# Navigate to the cloned GitHub repository directory
cd $GITHUB_CLONE_DIR

# Add the filtered Bitbucket repository as a remote
git remote add bitbucket ../$BITBUCKET_CLONE_DIR

# Fetch the history from the original repository
git fetch bitbucket

# Merge the histories
git merge bitbucket/master --allow-unrelated-histories

# Prompt the user to resolve any conflicts manually
echo "If there are any merge conflicts, please resolve them manually, stage the files, and commit the changes."

# Push the merged history to the GitHub repository
git push origin master

echo "Merge process completed and pushed to GitHub repository."
