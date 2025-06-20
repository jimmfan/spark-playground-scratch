git for-each-ref --sort=creatordate --format '%(creatordate:iso) %(refname:strip=2)' refs/tags \
  | awk '$1 >= "2024-06-01"'
