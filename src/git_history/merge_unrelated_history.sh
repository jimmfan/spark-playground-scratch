#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Define repository URLs and branch names
GITHUB_REPO_URL="https://github.com/your_username/github_repo.git"
BITBUCKET_REPO_URL="https://bitbucket.org/your_username/bitbucket_repo.git"
NEW_BRANCH="bitbucket-merge"
LARGE_FILES_PATH="large_files.txt"

# Step 1: Clone the GitHub repository
echo "Cloning GitHub repository..."
git clone $GITHUB_REPO_URL github_repo
cd github_repo

# Step 2: Fetch the Bitbucket repository
echo "Fetching Bitbucket repository..."
git remote add bitbucket $BITBUCKET_REPO_URL
git fetch bitbucket

# Step 3: Identify the first commit from Bitbucket
echo "Identifying the first commit from Bitbucket..."
FIRST_COMMIT=$(git rev-list --max-parents=0 HEAD | tail -n 1)
echo "First commit from Bitbucket: $FIRST_COMMIT"

# Step 4: Create an orphan branch from the first commit
echo "Creating orphan branch bitbucket-base from the first commit..."
git checkout --orphan bitbucket-base $FIRST_COMMIT
git reset --hard

# Step 5: Add the original commit to the GitHub repository
echo "Adding the original commit to GitHub repository..."
echo "Original commit from Bitbucket repository" > README.md
git add README.md
git commit -m "Add original commit from Bitbucket repository"
git checkout main

# Step 6: Create a new branch from the original commit for Bitbucket history
echo "Creating branch bitbucket-history from bitbucket-base..."
git checkout -b bitbucket-history bitbucket-base
git merge bitbucket/main --allow-unrelated-histories -m "Merge Bitbucket history into bitbucket-base"

# Step 7: Identify and save large files from Bitbucket history
echo "Identifying large files..."
git rev-list --objects --all --filter=blob:limit=100M > $LARGE_FILES_PATH

echo "Large files identified and saved to $LARGE_FILES_PATH:"
cat $LARGE_FILES_PATH

# Step 8: Remove large files using git filter-repo
if [ -s $LARGE_FILES_PATH ]; then
  echo "Removing large files..."
  git filter-repo --invert-paths --paths-from-file $LARGE_FILES_PATH
else
  echo "No large files to remove."
fi

# Step 9: Clean up and repack the repository
echo "Cleaning up and repacking the repository..."
rm -rf .git/refs/original/
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Step 10: Restore bitbucket-history branch if necessary
echo "Restoring bitbucket-history branch..."
git branch -f bitbucket-history

# Step 11: Merge Bitbucket history into a new branch based off main
echo "Checking out main branch..."
git checkout main
echo "Creating new branch $NEW_BRANCH..."
git checkout -b $NEW_BRANCH

echo "Merging bitbucket-history into $NEW_BRANCH..."
git merge bitbucket-history

# Step 12: Resolve conflicts if there are any
# This step may need to be repeated if there are multiple conflicts
echo "Resolving conflicts if any..."
git mergetool || true
git commit -m "Merged Bitbucket history into $NEW_BRANCH branch" || true

# Step 13: Push the new branch to GitHub
echo "Pushing the new branch to GitHub..."
git remote set-url origin $GITHUB_REPO_URL
git push origin $NEW_BRANCH
