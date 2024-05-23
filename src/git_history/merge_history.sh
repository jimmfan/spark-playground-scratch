#!/bin/bash

# Step 1: Clone both repositories
git clone https://github.com/your_username/github_repo.git
git clone https://bitbucket.org/your_username/bitbucket_repo.git

# Step 2: Add a remote for the Bitbucket repository
cd github_repo
git remote add bitbucket ../bitbucket_repo

# Step 3: Fetch all branches from Bitbucket
git fetch bitbucket

# Step 4: Create a new branch for Bitbucket history
git checkout -b bitbucket-history bitbucket/main

# Step 5: Identify and remove large files from Bitbucket history
# Find CSV files larger than 100 MB
large_files=$(git rev-list --objects --all | grep '\.csv' | while read -r hash name; do
  size=$(git cat-file -s "$hash")
  if [ $size -gt $((100 * 1024 * 1024)) ]; then
    echo "$name"
  fi
done)

# Remove large files using git filter-repo
for file in $large_files; do
  git filter-repo --path "$file" --invert-paths
done

# Step 6: Rebase GitHub commits onto Bitbucket history
git checkout main
git rebase bitbucket-history

# Step 7: Resolve conflicts if there are any
git rebase --continue

# Step 8: Push the updated history to GitHub
git push origin main --force
