#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Define repository URLs and branch names
GITHUB_REPO_URL="https://github.com/your_username/github_repo.git"
BITBUCKET_REPO_URL="https://bitbucket.org/your_username/bitbucket_repo.git"
NEW_BRANCH="bitbucket-merge"
LARGE_FILES_PATH="large_files.txt"

# Step 1: Clone both repositories
git clone $GITHUB_REPO_URL github_repo
git clone $BITBUCKET_REPO_URL bitbucket_repo

# Step 2: Add a remote for the Bitbucket repository in the GitHub repo
cd github_repo
git remote add bitbucket ../bitbucket_repo

# Step 3: Fetch all branches from Bitbucket
git fetch bitbucket

# Step 4: Create a new branch for Bitbucket history
git checkout -b bitbucket-history bitbucket/main

# Verify the bitbucket-history branch
echo "Verifying bitbucket-history branch..."
git branch --list bitbucket-history
git log --oneline -5

# Step 5: Identify and save large files from Bitbucket history
git rev-list --objects --all | while read -r hash name; do
  size=$(git cat-file -s "$hash")
  if [ $size -gt $((100 * 1024 * 1024)) ]; then
    echo "$name"
  fi
done > $LARGE_FILES_PATH

echo "Large files identified and saved to $LARGE_FILES_PATH:"
cat $LARGE_FILES_PATH

# Step 6: Remove large files using git filter-repo
if [ -s $LARGE_FILES_PATH ]; then
  echo "Removing large files..."
  git filter-repo --invert-paths --paths-from-file $LARGE_FILES_PATH
else
  echo "No large files to remove."
fi

# Step 7: Clean up and repack the repository
rm -rf .git/refs/original/
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Step 8: Merge Bitbucket history into a new branch based off main
git checkout main
git checkout -b $NEW_BRANCH

# Verify the bitbucket-history branch before merging
echo "Verifying bitbucket-history branch before merging..."
git branch --list bitbucket-history
git log bitbucket-history --oneline -5

git merge bitbucket-history

# Step 9: Resolve conflicts if there are any
# This step may need to be repeated if there are multiple conflicts
git mergetool
git commit -m "Merged Bitbucket history into $NEW_BRANCH branch"

# Step 10: Push the new branch to GitHub
git remote set-url origin $GITHUB_REPO_URL
git push origin $NEW_BRANCH
