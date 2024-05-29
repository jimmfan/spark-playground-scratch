for file in $(find . -type f | grep -v bitbucket); do
    git mv "$file" bitbucket/
done

for file in $(find . -type f -not -path "./origin/*" -not -path "./bitbucket/*"); do
    git mv "$file" bitbucket/
done