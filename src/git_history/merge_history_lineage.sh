#!/bin/bash

# Define variables
BITBUCKET_REPO_URL="your_bitbucket_repo_url"
GITHUB_REPO_URL="your_github_repo_url"
BITBUCKET_CLONE_DIR="original-repo.git"
FILTERED_BITBUCKET_DIR="filtered-bitbucket-repo"
GITHUB_CLONE_DIR="new-repo"
NEW_BRANCH_NAME="merge-bitbucket-history"

# Clone the original Bitbucket repository as a mirror
git clone --mirror $BITBUCKET_REPO_URL $BITBUCKET_CLONE_DIR

# Navigate to the cloned Bitbucket repository directory
cd $BITBUCKET_CLONE_DIR

# Filter out large files (>100MB)
git filter-repo --path-glob '**/*' --strip-blobs-bigger-than 100M

# Create a non-bare clone of the filtered Bitbucket repository
cd ..
git clone $BITBUCKET_CLONE_DIR $FILTERED_BITBUCKET_DIR

# Clone the new GitHub repository
git clone $GITHUB_REPO_URL $GITHUB_CLONE_DIR

# Navigate to the cloned GitHub repository directory
cd $GITHUB_CLONE_DIR

# Find the initial commit and rebase to remove it
INITIAL_COMMIT=$(git rev-list --max-parents=0 HEAD)
git rebase --onto $INITIAL_COMMIT^ $INITIAL_COMMIT

# Create a new branch for the merge
git checkout -b $NEW_BRANCH_NAME

# Add the filtered Bitbucket repository as a remote
git remote add bitbucket ../$FILTERED_BITBUCKET_DIR

# Fetch the history from the original repository
git fetch bitbucket

# Merge the histories
git merge bitbucket/master --allow-unrelated-histories

# Prompt the user to resolve any conflicts manually
echo "If there are any merge conflicts, please resolve them manually, stage the files, and commit the changes."

# Push the merged history to the new branch on GitHub
git push origin $NEW_BRANCH_NAME

echo "Merge process completed and pushed to GitHub repository on branch $NEW_BRANCH_NAME."
