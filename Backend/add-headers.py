# Backend\add-headers.py
"""
add_headers.py - Adds a header comment with the file's relative path
to every .py file that doesn't already have one.
"""

import os
import sys
import argparse

def add_header_to_file(file_path, root_dir, dry_run=False):
    """
    Add a header comment with the relative path of file_path from root_dir.
    Skips if the file already starts with a comment containing that relative path.
    """
    rel_path = os.path.relpath(file_path, root_dir)
    header = f"# {rel_path}"

    # Read the file content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False

    # Check if the first line already contains the header
    lines = content.splitlines()
    if lines and lines[0].strip() == header:
        # Already has the exact header
        return False

    # Also skip if the first non-empty line is the header (in case of blank lines at start)
    first_non_empty = next((line.strip() for line in lines if line.strip()), None)
    if first_non_empty == header:
        return False

    # If we reach here, we need to add the header
    new_content = header + "\n" + content
    if dry_run:
        print(f"Would add header to: {rel_path}")
        return True
    else:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Added header to: {rel_path}")
            return True
        except Exception as e:
            print(f"Error writing to {file_path}: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(
        description="Add a header comment with the file's relative path to every .py file."
    )
    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="Root directory to scan (default: current directory)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only show what would be changed, do not write files"
    )
    parser.add_argument(
        "--exclude-dirs",
        nargs="+",
        default=["__pycache__", ".git", ".venv", "venv"],
        help="Directories to skip (default: __pycache__ .git .venv venv)"
    )
    args = parser.parse_args()

    root_dir = os.path.abspath(args.root)
    if not os.path.isdir(root_dir):
        print(f"Error: '{root_dir}' is not a valid directory.")
        sys.exit(1)

    # Exclude the script itself
    script_path = os.path.abspath(__file__)

    modified_count = 0
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Prune excluded directories in-place to avoid walking into them
        dirnames[:] = [d for d in dirnames if d not in args.exclude_dirs]

        for filename in filenames:
            if not filename.endswith(".py"):
                continue
            file_path = os.path.join(dirpath, filename)
            if file_path == script_path:
                continue  # skip the script itself

            if add_header_to_file(file_path, root_dir, args.dry_run):
                modified_count += 1

    print(f"\n{'Dry run: ' if args.dry_run else ''}Total files modified: {modified_count}")

if __name__ == "__main__":
    main()