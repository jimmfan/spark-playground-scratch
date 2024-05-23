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

# Step 5: Remove large files from Bitbucket history
git filter-repo --path large_file.csv --invert-paths

# Step 6: Rebase GitHub commits onto Bitbucket history
git checkout main
git rebase bitbucket-history

# Step 7: Resolve conflicts if there are any
git rebase --continue

# Step 8: Push the updated history to GitHub
git push origin main --force
