# Dry Run
CUTOFF_DATE="2025-05-01"

git notes list | while read _note commit; do
  commit_date=$(git show -s --format=%ci "$commit" | cut -d' ' -f1)
  if [[ "$commit_date" > "$CUTOFF_DATE" ]]; then
    echo "Would delete note on commit $commit (date: $commit_date)"
  fi
done


# Actual code

CUTOFF_DATE="2025-05-01"

git notes list | while read _note commit; do
  commit_date=$(git show -s --format=%ci "$commit" | cut -d' ' -f1)
  if [[ "$commit_date" > "$CUTOFF_DATE" ]]; then
    echo "Deleting note on commit $commit (date: $commit_date)"
    git notes remove "$commit"
  fi
done

# Push the cleaned-up notes to GitHub
git push origin refs/notes/commits


# Delete based on text:

PATTERN="rc"

git notes list | while read _note commit; do
  note_content=$(git notes show "$commit" 2>/dev/null)
  if echo "$note_content" | grep -qi "$PATTERN"; then
    echo "Deleting note on commit $commit"
    git notes remove "$commit"
  fi
done

# Push updated notes to GitHub
git push origin refs/notes/commits
