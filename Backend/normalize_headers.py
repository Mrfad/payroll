#!/usr/bin/env python3
"""
normalize_headers.py - Ensures every .py file has exactly one header:
    # Backend\relative\path\to\file.py
Removes any leading comment lines (e.g., duplicate headers) and blank lines.
"""

import os
import sys

def normalize_file(file_path, root_dir, dry_run=False):
    # Compute the relative path from root_dir and build the new header
    rel_path = os.path.relpath(file_path, root_dir)
    # On Windows, use backslashes; on other platforms, keep the native separator.
    # The user wants "# Backend\..." style, so we force backslashes on Windows.
    if os.name == 'nt':
        rel_path = rel_path.replace('/', '\\')
    new_header = f"# Backend\\{rel_path}"

    # Read the file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False

    # If the file is empty, just add the header.
    if not lines:
        if not dry_run:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_header + "\n")
        print(f"Added header to empty file: {rel_path}")
        return True

    # Check if the first non‑empty line is already the new header
    first_non_empty = next((line for line in lines if line.strip()), None)
    if first_non_empty and first_non_empty.strip() == new_header:
        # Already correct, skip
        return False

    # Find the first line that is NOT a comment (starts with '#') and NOT blank.
    # We will discard all leading comment lines and blank lines.
    start_index = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == "" or stripped.startswith('#'):
            continue
        else:
            start_index = i
            break
    else:
        # All lines were comments or blank – treat as empty file
        if not dry_run:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_header + "\n")
        print(f"Added header to file with only comments: {rel_path}")
        return True

    # Keep the content from start_index onward
    content = lines[start_index:]

    # Prepend the new header + newline
    new_content = new_header + "\n" + "".join(content)

    if dry_run:
        print(f"Would normalize: {rel_path}")
        return True
    else:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Normalized: {rel_path}")
        return True

def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Normalize .py file headers to '# Backend\\path\\to\\file.py'"
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
        help="Show what would be changed without writing files"
    )
    parser.add_argument(
        "--exclude-dirs",
        nargs="+",
        default=["__pycache__", ".git", ".venv", "venv"],
        help="Directories to skip"
    )
    args = parser.parse_args()

    root_dir = os.path.abspath(args.root)
    if not os.path.isdir(root_dir):
        print(f"Error: '{root_dir}' is not a valid directory.")
        sys.exit(1)

    modified_count = 0
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Prune excluded directories
        dirnames[:] = [d for d in dirnames if d not in args.exclude_dirs]

        for filename in filenames:
            if not filename.endswith(".py"):
                continue
            file_path = os.path.join(dirpath, filename)
            # Skip the script itself
            if os.path.abspath(__file__) == file_path:
                continue
            if normalize_file(file_path, root_dir, args.dry_run):
                modified_count += 1

    print(f"\n{'Dry run: ' if args.dry_run else ''}Total files modified: {modified_count}")

if __name__ == "__main__":
    main()