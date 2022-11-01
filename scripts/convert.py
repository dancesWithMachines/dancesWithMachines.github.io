import glob, os
import subprocess
import shutil

# This script uses "markdown-to-html-github-style" to generate website from github markdown.
# Link: https://github.com/KrauseFx/markdown-to-html-github-style
#
# Markdown-to-html looks for README.md file, thus every file must be renamed and occurrences must be replaced within those files.
# I know this is a bit cursed, but I don't feel like messing with javascript, and I can license this however I want.

markdown_to_html_path="/Users/timax/Development/3rd_party_repos/markdown-to-html-github-style/convert.js"

os.chdir("./markdown")
for file in glob.glob("*.md"):
    name=file.removesuffix(".md")
    shutil.copy(file, "README.md")
    convert=subprocess.run(["node", markdown_to_html_path, name])
    with open("README.html") as f:
        content=f.read().replace("../", "./") \
                        .replace(".md","html")
    with open("README.html", "w") as f:
        f.write(content)
    shutil.move("README.html", "../" + name + ".html")
    os.remove("README.md")