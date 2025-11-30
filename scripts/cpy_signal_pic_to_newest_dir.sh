#!/bin/bash

# Check if the current directory path contains "scripts"
if [[ "$PWD" == *"/scripts"* ]]; then
    echo "This script must be executed at the root of the repository."
    exit 1
fi

# Get the newest file starting with "signal" in the Downloads directory
newest_signal_file=$(ls -t "$HOME"/Downloads/signal* 2>/dev/null | head -n 1)

# Check if any "signal" file exists
if [[ -z "$newest_signal_file" ]]; then
    echo "No Signal pics found in $HOME/Downloads."
    exit 1
fi

# Get the newest directory in ./assets/posts/
newest_post_dir=$(ls -td ./assets/posts/* 2>/dev/null | head -n 1)

# Prompt the user for a new filename
read -p "Enter a new filename (leave blank to keep original): " new_filename

# Extract the file extension
file_extension="${newest_signal_file##*.}"

# If the user didn't provide a new filename, use the original filename
if [[ -z "$new_filename" ]]; then
    new_filename=$(basename "$newest_signal_file")
else
    # Add the file extension to the new filename
    new_filename="${new_filename}.${file_extension}"
fi

# Copy the file to the newest directory in ./assets/posts/
cp "$newest_signal_file" "$newest_post_dir/$new_filename"

echo "File copied to $newest_post_dir/$new_filename successfully."
echo "Add file to post with -> ![${new_filename%%.*}](../.$newest_post_dir/$new_filename)"
