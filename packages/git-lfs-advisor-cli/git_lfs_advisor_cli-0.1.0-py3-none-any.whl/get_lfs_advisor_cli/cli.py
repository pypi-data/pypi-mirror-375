import os
import sys
import configparser
import pathlib

# --- Configuration ---
SIZE_LIMIT_MB = 25
# A set of common binary file extensions. Add more as needed for your project.
BINARY_EXTENSIONS = {
    # Images
    '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.svg',
    # Documents
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    # Archives
    '.zip', '.rar', '.7z', '.gz', '.tar',
    # Compiled code and libraries
    '.exe', '.dll', '.so', '.a', '.lib',
    # Media
    '.mp3', '.wav', '.ogg', '.mp4', '.mov', '.avi',
    # Databases
    '.db', '.sqlite', '.sqlite3',
    # Other
    '.jar', '.bin', '.dat',
}
# --- End Configuration ---


SIZE_LIMIT_BYTES = SIZE_LIMIT_MB * 1024 * 1024


def is_binary_file(filepath, chunk_size=1024):
    """
    Heuristically determines if a file is binary by checking for null bytes
    in the first chunk of the file.
    """
    try:
        with open(filepath, 'rb') as f:
            return b'\0' in f.read(chunk_size)
    except IOError:
        return False  # Could not read, assume not binary for safety.


def get_submodule_paths():
    """Parses .gitmodules and returns a set of submodule paths."""
    submodules = set()
    gitmodules_path = '.gitmodules'
    if not os.path.exists(gitmodules_path):
        return submodules

    print("Found .gitmodules, parsing for submodule paths...")
    config = configparser.ConfigParser()
    try:
        config.read(gitmodules_path)
        for section in config.sections():
            if config.has_option(section, 'path'):
                path_str = config.get(section, 'path')
                # Normalize path for the current OS (e.g., using '\' on Windows)
                normalized_path = str(pathlib.Path(path_str))
                submodules.add(normalized_path)
    except configparser.Error as e:
        print(f"Warning: Could not parse .gitmodules file: {e}", file=sys.stderr)

    if submodules:
        print("The following submodule paths will be ignored:")
        for path in sorted(list(submodules)):
            print(f"  - {path}")
    return submodules


def scan_repo_files(submodule_paths):
    """Walks the repo, yielding file paths to be analyzed."""
    for root, dirs, files in os.walk('.', topdown=True):
        if '.git' in dirs:
            dirs.remove('.git')

        for d in dirs[:]:
            dir_path = str(pathlib.Path(root) / d)
            if dir_path in submodule_paths:
                print(f"Ignoring submodule directory: '{dir_path}'")
                dirs.remove(d)

        for filename in files:
            yield os.path.join(root, filename)


def analyze_file(file_path):
    """Analyzes a single file and returns an LFS pattern if it matches criteria."""
    try:
        normalized_path = str(pathlib.Path(file_path).as_posix())
        file_size = os.path.getsize(file_path)
        is_large = file_size > SIZE_LIMIT_BYTES
        is_bin = False

        if not is_large:
            _, ext = os.path.splitext(file_path)
            if ext.lower() in BINARY_EXTENSIONS:
                is_bin = True
            else:
                is_bin = is_binary_file(file_path)

        if is_large or is_bin:
            if is_large:
                size_in_mb = file_size / (1024 * 1024)
                print(f"Found large file: '{normalized_path}' (Size: {size_in_mb:.2f}MB)")
            else:
                print(f"Found binary file: '{normalized_path}' (Reason: Binary content)")

            if '.' in os.path.basename(file_path):
                _, ext = os.path.splitext(file_path)
                return f"*{ext.lower()}"
            else:
                return normalized_path

    except FileNotFoundError:
        print(f"Warning: Could not access '{file_path}'. Skipping.", file=sys.stderr)

    return None


def print_lfs_suggestions(lfs_patterns):
    """Prints the suggested LFS commands based on found patterns."""
    if not lfs_patterns:
        print(f"No files found exceeding {SIZE_LIMIT_MB}MB or detected as binary.")
        return

    print("\n--- Suggested git lfs track commands (for .gitattributes) ---")
    print("# Run these commands to update your .gitattributes file.")
    sorted_patterns = sorted(list(lfs_patterns))
    for pattern in sorted_patterns:
        print(f'git lfs track "{pattern}"')

    print("\n--- Suggested git lfs migrate command (for rewriting history) ---")
    include_arg = ",".join(sorted_patterns)
    print("\n# WARNING: The following commands rewrite the history of your repository.")
    print("# It is STRONGLY RECOMMENDED to run this on a fresh clone or to backup your repository first.")
    print("\n# --- Option 1: Migrate ONLY the CURRENT branch (most common) ---")
    print(f'git lfs migrate import --include="{include_arg}"')
    print("\n# --- Option 2: Migrate a SPECIFIC branch (e.g., 'main') ---")
    print(f'# git lfs migrate import --include="{include_arg}" main')
    print("\n# --- Option 3: Migrate ALL local and remote branches ---")
    print(f'# git lfs migrate import --include="{include_arg}" --everything')


def main():
    """Finds large or binary files and generates .gitattributes LFS rules."""
    print(f"Scanning for files larger than {SIZE_LIMIT_MB}MB or binary files...")
    submodule_paths = get_submodule_paths()
    print("----------------------------------------")

    lfs_patterns = set()
    for file_path in scan_repo_files(submodule_paths):
        pattern = analyze_file(file_path)
        if pattern:
            lfs_patterns.add(pattern)

    print("----------------------------------------")
    print("Scan complete.")
    print_lfs_suggestions(lfs_patterns)


if __name__ == "__main__":
    main()
