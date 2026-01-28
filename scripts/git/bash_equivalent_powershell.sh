#!/bin/bash

# Define repository URLs
BITBUCKET_REPO_PATH="/path/to/your/local/bitbucket/repo"
GITHUB_REPO_URL="https://github.com/your_username/github_repo.git"

# Step 1: Initialize a new Git repository
echo "Initializing new repository..."
git init new_repo
cd new_repo

# Step 2: Create an initial dummy commit
echo "Creating initial dummy commit..."
git commit --allow-empty -m "Initial dummy commit"

# Step 3: Add a remote for the local Bitbucket repo and fetch its content
echo "Adding and fetching Bitbucket repo..."
git remote add origin $BITBUCKET_REPO_PATH
git fetch origin

if (Test-Path $LARGE_FILES_PATH -PathType Leaf) {
    $file = Get-Item $LARGE_FILES_PATH
    if ($file.Length -gt 0) {
        Write-Output "Removing large files..."
        git filter-repo --invert-paths --paths-from-file $LARGE_FILES_PATH
    } else {
        Write-Output "No large files to remove."
    }
} else {
    Write-Output "No large files to remove."
}

# Step 4: Merge origin/master into the current branch
echo "Merging origin/master into the current branch..."
git merge origin/master --allow-unrelated-histories -m "Merge Bitbucket repo into new repository"

# Step 5: Move origin files into a subdirectory
echo "Moving origin files into a subdirectory..."
mkdir origin_files
for file in $(ls -A | grep -v origin_files); do
  git mv "$file" origin_files/
done

# Step 6: Commit the move
echo "Committing the move of origin files..."
git commit -m "Move Bitbucket repo files into subdir"

# Step 7: Add a remote for GitHub repo and fetch its content
echo "Adding and fetching GitHub repo..."
git remote add github $GITHUB_REPO_URL
git fetch github

# Step 8: Merge github/master into the current branch
echo "Merging github/master into the current branch..."
git merge github/master --allow-unrelated-histories -m "Merge GitHub repo into new repository"

# Step 9: Move GitHub repo files into a subdirectory
echo "Moving GitHub repo files into a subdirectory..."
mkdir github_files
for file in $(ls -A | grep -v origin_files | grep -v github_files); do
  git mv "$file" github_files/
done

# Step 10: Commit the move
echo "Committing the move of GitHub repo files..."
git commit -m "Move GitHub repo files into subdir"

echo "Process completed successfully."
