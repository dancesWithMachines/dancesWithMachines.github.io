#!/usr/bin/env python3
"""blog.py — helper CLI for managing posts in this Jekyll blog.

Single entry point that replaces the old shell scripts. Run `blog.py --help`
or `blog.py <command> --help` for usage. Commands fall back to interactive
prompts when arguments are omitted.
"""

import argparse
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

POSTS_DIR = Path("all_collections/_posts")
ASSETS_DIR = Path("assets/posts")

# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def find_repo_root() -> Path:
    """Walk up from CWD until we find the posts directory, so the tool can be
    run from anywhere in the repo."""
    for d in [Path.cwd(), *Path.cwd().parents]:
        if (d / POSTS_DIR).is_dir():
            return d
    sys.exit("Error: could not locate the blog repo root (no all_collections/_posts found).")


def slugify(title: str) -> str:
    """Lowercase, strip anything but [a-z0-9_ ], spaces -> hyphens.

    Matches the behaviour of the old shell scripts."""
    s = title.lower()
    s = re.sub(r"[^a-z0-9_ ]", "", s)
    s = s.replace(" ", "-")
    return s


def post_slug(filename: str) -> str:
    """Strip the leading `YYYY-MM-DD-` date and the `.md` suffix from a post
    filename to get its slug."""
    name = Path(filename).name
    name = re.sub(r"^\d{4}-\d{1,2}-\d{1,2}-", "", name)
    return re.sub(r"\.md$", "", name)


def parse_categories_line(text: str):
    """Return the list of categories from a post's frontmatter, or []."""
    m = re.search(r"^categories:\s*\[(.*)\]\s*$", text, re.MULTILINE)
    if not m:
        return []
    return re.findall(r'"([^"]+)"', m.group(1))


def format_categories(cats) -> str:
    if not cats:
        return "[]"
    return "[" + ",".join(f'"{c}"' for c in cats) + "]"


def list_categories(root: Path):
    """Collect the unique set of categories used across all posts."""
    cats = set()
    for f in sorted((root / POSTS_DIR).glob("*.md")):
        cats.update(parse_categories_line(f.read_text(encoding="utf-8")))
    return sorted(cats)


def ensure_assets_dirs(root: Path) -> None:
    """Ensure every post has a matching assets/posts/<slug>/ directory.

    Not a user-facing command; run automatically when creating a new post."""
    for f in sorted((root / POSTS_DIR).glob("*.md")):
        target = root / ASSETS_DIR / post_slug(f.name)
        if not target.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            print(f"Created assets directory: {target.relative_to(root)}")


def prompt(text: str, default: str = "") -> str:
    try:
        ans = input(text).strip()
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit("Aborted.")
    return ans or default


# --------------------------------------------------------------------------- #
# Commands
# --------------------------------------------------------------------------- #


def cmd_new(root: Path, args) -> None:
    """Create a new post from a frontmatter template, then sync asset dirs."""
    title = args.title or prompt("Enter post title: ")
    if not title:
        sys.exit("Error: a title is required.")

    slug = slugify(title)
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%Y-%m-%d %H:%M")
    post_path = root / POSTS_DIR / f"{date}-{slug}.md"

    if post_path.exists():
        sys.exit(f"Error: post already exists: {post_path.relative_to(root)}")

    # Categories
    if args.cat is not None:
        cats = [c.strip() for c in args.cat.split(",") if c.strip()]
    else:
        print("Available categories are:")
        for c in list_categories(root):
            print(f"  {c}")
        raw = prompt("Enter categories (comma-separated, leave empty for none): ")
        cats = [c.strip() for c in raw.split(",") if c.strip()]

    post_path.write_text(
        "---\n"
        "layout: post\n"
        f'title: "{title}"\n'
        f"date: {time}\n"
        f"categories: {format_categories(cats)}\n"
        "---\n",
        encoding="utf-8",
    )
    print(f"Post template created: {post_path.relative_to(root)}")
    ensure_assets_dirs(root)


def cmd_rename(root: Path, args) -> None:
    """Rename a post file + its assets dir and rewrite its title."""
    src = Path(args.post)
    if not src.is_absolute():
        # Accept paths relative to either CWD or repo root.
        src = src if src.exists() else root / args.post
    if not src.is_file():
        sys.exit(f"Error: file '{args.post}' does not exist.")

    filename = src.name
    m = re.match(r"^(\d{4}-\d{1,2}-\d{1,2})-(.+)\.md$", filename)
    if not m:
        sys.exit(f"Error: '{filename}' is not a dated post (YYYY-MM-DD-slug.md).")
    date_prefix, old_slug = m.group(1), m.group(2)

    new_title = args.title or prompt("Enter new title: ")
    if not new_title:
        sys.exit("Error: a new title is required.")
    new_slug = slugify(new_title)

    new_post = root / POSTS_DIR / f"{date_prefix}-{new_slug}.md"
    old_assets = root / ASSETS_DIR / old_slug
    new_assets = root / ASSETS_DIR / new_slug

    print("Updating post file name.")
    shutil.move(str(src), str(new_post))

    print("Updating assets directory name.")
    if old_assets.is_dir():
        shutil.move(str(old_assets), str(new_assets))

    print("Applying new title.")
    text = new_post.read_text(encoding="utf-8")
    text = re.sub(r'^title:.*$', f'title: "{new_title}"', text, count=1, flags=re.MULTILINE)
    new_post.write_text(text, encoding="utf-8")

    print("Post and assets renamed successfully.")


def cmd_signal_img(root: Path, args) -> None:
    """Copy the newest ~/Downloads/signal* file into the newest post dir."""
    downloads = Path.home() / "Downloads"
    signal_files = sorted(
        downloads.glob("signal*"), key=lambda p: p.stat().st_mtime, reverse=True
    )
    if not signal_files:
        sys.exit(f"No Signal pics found in {downloads}.")
    src = signal_files[0]

    post_dirs = sorted(
        (p for p in (root / ASSETS_DIR).iterdir() if p.is_dir()),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not post_dirs:
        sys.exit(f"No post directories found in {ASSETS_DIR}.")
    dest_dir = post_dirs[0]

    new_name = args.name or prompt("Enter a new filename (leave blank to keep original): ")
    if new_name:
        new_name = f"{new_name}{src.suffix}"
    else:
        new_name = src.name

    dest = dest_dir / new_name
    shutil.copy2(src, dest)

    rel = dest.relative_to(root)
    stem = Path(new_name).stem
    print(f"File copied to {rel} successfully.")
    print(f"Add file to post with -> ![{stem}](../../{rel})")


# Bare YouTube iframe -> responsive wrapper, used by `verify`.
_IFRAME_RE = re.compile(
    r'<iframe[^>]*src="https://www\.youtube\.com/embed/([^"?&]+)[^"]*"[^>]*></iframe>',
    re.IGNORECASE,
)
_IFRAME_TEMPLATE = (
    '\n<div style="width:100%">\n'
    '  <iframe\n'
    '    src="https://www.youtube.com/embed/{vid}"\n'
    '    title="YouTube video player"\n'
    '    allow="accelerometer; autoplay; clipboard-write; encrypted-media; '
    'gyroscope; picture-in-picture; web-share"\n'
    '    referrerpolicy="strict-origin-when-cross-origin"\n'
    '    allowfullscreen\n'
    '    style="width:100%; aspect-ratio:16/9; border:0;"\n'
    '  ></iframe>\n'
    '</div>\n'
)


def _fix_iframes(content: str):
    """Return (new_content, n_fixed) wrapping bare YouTube iframes responsively."""
    fixed = 0

    def repl(match):
        nonlocal fixed
        start, end = match.span()
        surrounding = content[max(0, start - 50):min(len(content), end + 50)]
        # Skip if already responsive or wrapped in a width:100% div.
        if "width:100%" in match.group(0) or "width:100%" in surrounding:
            return match.group(0)
        fixed += 1
        return _IFRAME_TEMPLATE.format(vid=match.group(1))

    return _IFRAME_RE.sub(repl, content), fixed


def cmd_verify(root: Path, args) -> None:
    """Check all posts and apply fixes, reporting only the posts changed.

    Currently fixes bare YouTube iframes to be responsive."""
    any_changed = False
    for f in sorted((root / POSTS_DIR).glob("*.md")):
        content = f.read_text(encoding="utf-8")
        new_content, fixed = _fix_iframes(content)
        if fixed:
            f.write_text(new_content, encoding="utf-8")
            print(f"[+] {f.name}: fixed {fixed} iframe(s)")
            any_changed = True
    if not any_changed:
        print("All posts OK, nothing to fix.")


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="blog.py", description="Helper CLI for managing this Jekyll blog."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_new = sub.add_parser("new", help="Create a new post (also creates its assets dir).")
    p_new.add_argument("title", nargs="?", help="Post title (prompted if omitted).")
    p_new.add_argument("--cat", help="Comma-separated categories (prompted if omitted).")
    p_new.set_defaults(func=cmd_new)

    p_rename = sub.add_parser("rename", help="Rename a post + its assets dir.")
    p_rename.add_argument("post", help="Path to the post .md file.")
    p_rename.add_argument("title", nargs="?", help="New title (prompted if omitted).")
    p_rename.set_defaults(func=cmd_rename)

    p_img = sub.add_parser(
        "signal-img", help="Copy newest ~/Downloads/signal* into newest post dir."
    )
    p_img.add_argument("--name", help="New filename without extension (prompted if omitted).")
    p_img.set_defaults(func=cmd_signal_img)

    p_verify = sub.add_parser(
        "verify", help="Scan all posts and apply fixes (responsive iframes)."
    )
    p_verify.set_defaults(func=cmd_verify)

    args = parser.parse_args()
    root = find_repo_root()
    args.func(root, args)


if __name__ == "__main__":
    main()
