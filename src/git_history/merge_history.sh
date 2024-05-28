#!/bin/bash

# Define repository URLs
GITHUB_REPO_URL="https://github.com/your_username/github_repo.git"
BITBUCKET_REPO_URL="https://bitbucket.org/your_username/bitbucket_repo.git"

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

# Step 5: Identify and remove large files from Bitbucket history using git filter-repo
large_files=$(git rev-list --objects --all | grep '\.csv' | while read -r hash name; do
  size=$(git cat-file -s "$hash")
  if [ $size -gt $((100 * 1024 * 1024)) ]; then
    echo "$name"
  fi
done)

# Step 5b for powershell
$largeFiles = git rev-list --objects --all | ForEach-Object {
    $entry = $_ -split " "
    $hash = $entry[0]
    $name = $entry[1]
    $size = git cat-file -s $hash
    if ($size -gt (100 * 1024 * 1024)) {
        $name
    }
}

# Remove large files using git filter-repo
for file in $large_files; do
  python git-filter-repo --path "$file" --invert-paths
done

# Step 6: Merge Bitbucket history into the main branch
git checkout main
git merge bitbucket-history

# Step 7: Resolve conflicts if there are any
# This step may need to be repeated if there are multiple conflicts
git mergetool
git commit -m "Merged Bitbucket history into main branch"

# Step 8: Push the updated history to GitHub
git remote set-url origin $GITHUB_REPO_URL
git push origin main --force

# Clean up
cd ..
rm -rf github_repo bitbucket_repo
