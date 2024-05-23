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
# Find CSV files larger than 100 MB and remove them
git rev-list --objects --all | grep '\.csv' | while read -r hash name; do
  size=$(git cat-file -s "$hash")
  if [ $size -gt $((100 * 1024 * 1024)) ]; then
    echo "Removing $name ($size bytes)"
    git filter-branch --force --index-filter "git rm --cached --ignore-unmatch $name" --prune-empty --tag-name-filter cat -- --all
  fi
done

# Step 6: Clean up and repack the repository
rm -rf .git/refs/original/
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Step 7: Rebase GitHub commits onto Bitbucket history
git checkout main
git rebase bitbucket-history

# Step 8: Resolve conflicts if there are any
git rebase --continue

# Step 9: Push the updated history to GitHub
git push origin main --force
