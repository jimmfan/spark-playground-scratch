# Define variables
INITIAL_COMMIT_HASH="your_initial_commit_hash"
BRANCH_NAME="main"

# Check out the main branch
git checkout $BRANCH_NAME

# Start an interactive rebase
# Use GIT_SEQUENCE_EDITOR to automate the rebase editing
export GIT_SEQUENCE_EDITOR="sed -i '/$INITIAL_COMMIT_HASH/d'"

# Rebase all commits after the initial commit
git rebase -i $INITIAL_COMMIT_HASH^

# Force push the changes to the remote repository
git push origin $BRANCH_NAME --force

echo "Initial commit removed and changes pushed to GitHub repository on branch $BRANCH_NAME."
