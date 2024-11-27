#!/bin/bash

# Define source and target directories
POSTS_DIR="./all_collections/_posts"
ASSETS_DIR="./assets/posts"

# Initialize a flag to check if changes were made
changes_made=false

# Check if the current directory path contains "scripts"
if [[ "$PWD" == *"/scripts"* ]]; then
    echo "This script must be executed at the root of the repository."
    exit 1
fi

# Loop through all markdown files in the posts directory
for file in "$POSTS_DIR"/*.md; do
    # Extract the base name of the file (e.g., 2024-11-1-hello-world.md)
    base_name=$(basename "$file")

    # Remove the date and extension to get the desired directory name
    dir_name=$(echo "$base_name" | sed -E 's/^[0-9-]+-//; s/\.md$//')

    # Full path of the new directory
    target_dir="$ASSETS_DIR/$dir_name"

    # Check if the directory already exists
    if [[ ! -d "$target_dir" ]]; then
        # Create the directory
        mkdir -p "$target_dir"
        echo "Created directory: $target_dir"
        changes_made=true
    fi
done

# If no changes were made, print "No changes"
if [[ "$changes_made" == false ]]; then
    echo "No changes"
fi
