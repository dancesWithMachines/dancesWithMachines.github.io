#!/bin/bash

POST_DIR="./all_collections/_posts"

# Check if path to post is provided
if [ -z "$1" ]; then
    echo "Usage: $0 path/to/post.md"
    exit 1
fi

original_post_path="$1"

# Extract current filename (without path)
original_filename=$(basename "$original_post_path")

# Check if file exists
if [ ! -f "$original_post_path" ]; then
    echo "Error: File '$original_post_path' does not exist."
    exit 1
fi

# Extract the current date and slug
date_prefix="${original_filename:0:10}"

filename_length=${#original_filename}
slug_length=$((filename_length - 11 - 3))
old_slug="${original_filename:11:$slug_length}"

# Ask for new title
read -p "Enter new title: " new_title

# Sanitize title to new slug
new_slug=$(echo "$new_title" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9_ ]//g' | tr ' ' '-')

# New paths
new_filename="${date_prefix}-${new_slug}.md"
new_post_path="${POST_DIR}/${new_filename}"

old_assets_dir="./assets/posts/${old_slug}/"
new_assets_dir="./assets/posts/${new_slug}/"

# Step 1: Rename the post file
echo "Updating post file name."
mv "$original_post_path" "$new_post_path" || {
    echo "Failed to rename post file."
    exit 1
}

# Step 2: Rename assets directory (if it exists)
echo "Updating assets directory name."
if [ -d "$old_assets_dir" ]; then
    mv "$old_assets_dir" "$new_assets_dir" || {
        echo "Failed to rename assets directory."
        exit 1
    }
fi

# Step 3: Update title inside post
echo "Applying new title."
sed -i '' "s/^title: .*/title: \"$new_title\"/" "$new_post_path"

# Step 4: Update references to old filename (in other posts)
# We'll search for mentions of the old filename (without path)
# echo "Updating references to '$original_filename' in other posts..."
# grep -rl "$old_slug" ./all_collections/_posts/ | grep -v "$new_post_path" | while read -r file; do
#     sed -i "s|$old_slug|$new_slug|g" "$file"
# done

echo "Post and assets renamed successfully."

