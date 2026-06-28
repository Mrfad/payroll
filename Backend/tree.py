# Backend\tree.py
import os
import sys

def print_tree(root_dir, prefix=""):
    """
    Recursively walk through root_dir and print:
    - all directories
    - all .py files
    skipping __pycache__ and .pyc files.
    """
    try:
        items = sorted(os.listdir(root_dir))
    except PermissionError:
        return

    # Filter items: we only keep directories and .py files
    filtered = []
    for item in items:
        full_path = os.path.join(root_dir, item)
        if os.path.isdir(full_path):
            if item == "__pycache__":
                continue
            filtered.append((item, True))  # directory
        else:
            if item.endswith(".py"):
                filtered.append((item, False))  # file

    # Print each item with appropriate indentation
    for i, (name, is_dir) in enumerate(filtered):
        # Determine connector characters
        if i == len(filtered) - 1:
            connector = "└── "
            next_prefix = prefix + "    "
        else:
            connector = "├── "
            next_prefix = prefix + "│   "

        print(f"{prefix}{connector}{name}")

        # If it's a directory, recurse into it
        if is_dir:
            print_tree(os.path.join(root_dir, name), next_prefix)

if __name__ == "__main__":
    # Use the provided argument or the current working directory
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    print(f"Project tree for: {os.path.abspath(root)}\n")
    print_tree(root)