#!/bin/bash

fetch_categories() {
  find ./all_collections/_posts -name "*.md" | while read -r file; do
    # Extract the line before the second '---' in each file
    awk '
      BEGIN { dash_count = 0 }
      /^---/ {
        dash_count++
        if (dash_count == 2) {
          print prev_line
          exit
        }
      }
      { prev_line = $0 }
    ' "$file"
  done | \
  sed -E 's/^.*\[(.*)\].*$/\1/' | \
  tr ',' '\n' | \
  sed -E 's/^[[:space:]]*"([^"]+)"[[:space:]]*$/\1/' | \
  sort -u
}

# Check if the current directory path contains "scripts"
if [[ "$PWD" == *"/scripts"* ]]; then
    echo "This script must be executed at the root of the repository."
    exit 1
fi

# Prompt for post title
read -p "Enter post title: " title

# Process the title to create a sanitized filename
sanitized_title=$(echo "$title" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9_ ]//g' | tr ' ' '-')

# Get the current date and time
current_date=$(date +"%Y-%m-%d")
current_time=$(date +"%Y-%m-%d %H:%M")

# Create the filename
filename="./all_collections/_posts/${current_date}-${sanitized_title}.md"

echo "Available categories are:"
fetch_categories

# Prompt for categories
read -p "Enter categories (comma-separated, leave empty for none): " categories

# Format categories list
if [ -z "$categories" ]; then
  formatted_categories="[]"
else
  formatted_categories="[$(echo "$categories" | tr -d ' ' | sed 's/\([^,]*\)/"\1"/g; s/, /, /g')]"
fi

# Create the file and write the content
cat <<EOF > "$filename"
---
layout: post
title: "$title"
date: $current_time
categories: $formatted_categories
---
EOF

echo "Post template created: $filename"

# Run additional script
./scripts/create_dirs.sh
