import os  # Working with the file system
import mimetypes  # Determining file MIME types
import argparse  # Parsing command-line arguments
import stat  # Getting file permission information
from collections import defaultdict  # Convenient structure for counting file categories
from concurrent.futures import ThreadPoolExecutor, as_completed  # Parallel task execution

# Dictionary for determining file categories based on extensions
EXTENSION_CATEGORIES = {
    "text": ["txt", "md", "csv", "log"],
    "image": ["jpg", "jpeg", "png", "gif"],
    "executable": ["exe", "bin", "sh"],
    "archive": ["zip", "tar", "gz", "bz2"],
    "audio": ["mp3", "wav"],
    "video": ["mp4", "avi"],
    "document": ["pdf", "doc", "docx"],
}


def get_category(file_path):
    """
    Determines the category of a file based on its MIME type or extension.

    Arguments:
    file_path (str): The file path.

    Returns:
    str: The file category (e.g., "text", "image", or "unknown").
    """
    # Determine the MIME type of the file
    mime_type, _ = mimetypes.guess_type(file_path)

    if mime_type:
        # Extract the category from the MIME type (e.g., "text/plain" -> "text")
        category = mime_type.split("/")[0]
        if category in EXTENSION_CATEGORIES:
            return category

    # If MIME type is not recognized, determine the category by extension
    _, ext = os.path.splitext(file_path)
    ext = ext.lower().lstrip(".")
    for category, extensions in EXTENSION_CATEGORIES.items():
        if ext in extensions:
            return category

    # If no category is found, return "unknown"
    return "unknown"


def analyze_file(file_path, size_threshold):
    """
    Analyzes a single file, gathering information about its category, size, and permissions.

    Arguments:
    file_path (str): The file path.
    size_threshold (int): The threshold for determining large files (in bytes).

    Returns:
    tuple: The file path and a dictionary with file information.
    """
    file_info = {
        "category": "unknown",
        "size": 0,
        "permissions": "normal",
    }  # Initializing file information

    try:
        # Get the file size
        file_size = os.path.getsize(file_path)
        file_info["size"] = file_size

        # Determine the file category
        file_info["category"] = get_category(file_path)

        # Check if the file size exceeds the threshold
        if file_size > size_threshold:
            file_info["size"] = file_size

        # Get permission information
        file_stat = os.stat(file_path)
        permissions = {
            "writable_by_others": bool(file_stat.st_mode & stat.S_IWOTH),
            "readable_by_others": bool(file_stat.st_mode & stat.S_IROTH),
            "executable_by_others": bool(file_stat.st_mode & stat.S_IXOTH),
        }

        # Check for unusual permissions
        if permissions["writable_by_others"]:
            file_info["permissions"] = "Writable by others"
        elif permissions["readable_by_others"]:
            file_info["permissions"] = "Readable by others"
        elif permissions["executable_by_others"]:
            file_info["permissions"] = "Executable by others"

    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
    except PermissionError:
        print(f"Error: No permission to access file {file_path}.")
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")

    return file_path, file_info


def analyze_directory(directory, size_threshold):
    """
    Analyzes a directory, gathering information about files, including categories, large files, and permissions.

    Arguments:
    directory (str): The path to the directory.
    size_threshold (int): The threshold for large files (in bytes).

    Returns:
    tuple: Dictionary of file categories, list of large files, and list of files with unusual permissions.
    """
    file_categories = defaultdict(int)  # Stores file categories and their total size
    large_files = []  # List of large files
    unusual_permissions = []  # List of files with unusual permissions

    # Check if the directory exists
    if not os.path.isdir(directory):
        raise OSError(f"Directory {directory} does not exist or is inaccessible.")

    # Parallel execution for file analysis
    futures = []
    with ThreadPoolExecutor() as executor:
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                futures.append(executor.submit(analyze_file, file_path, size_threshold))

        # Process the results
        for future in as_completed(futures):
            file_path, file_info = future.result()

            # Increment total size for the file category
            if file_info["category"]:
                file_categories[file_info["category"]] += file_info["size"]

            # Add large files to the list
            if file_info["size"] > size_threshold:
                large_files.append((file_path, file_info["size"]))

            # Add files with unusual permissions to the list
            if file_info["permissions"] in [
                "Writable by others",
                "Readable by others",
                "Executable by others",
            ]:
                unusual_permissions.append((file_path, file_info["permissions"]))

    return file_categories, large_files, unusual_permissions


def print_report(categories, large_files, permissions):
    """
    Prints a report based on the file system analysis results.

    Arguments:
    categories (dict): File categories and their total size.
    large_files (list): List of large files.
    permissions (list): List of files with unusual permissions.
    """
    # Print file categories and their total size
    if categories:
        print("\nFile Categories and Their Total Size:")
        for category, total_size in sorted(categories.items()):
            print(f"{category.capitalize()}: {total_size:,} bytes")
    else:
        print("No file categories found.")

    # Print large files
    if large_files:
        print("\nLarge Files:")
        for file_path, size in sorted(large_files, key=lambda x: x[1], reverse=True):
            print(f"{file_path}: {size:,} bytes")
    else:
        print("No large files found.")

    # Print files with unusual permissions
    if permissions:
        print("\nFiles with Unusual Permissions:")
        for file_path, permission_type in sorted(permissions):
            print(f"{file_path}: {permission_type}")
    else:
        print("No files with unusual permissions found.")


def main():
    """
    Main function that parses command-line arguments, runs directory analysis, and prints a report.
    """
    parser = argparse.ArgumentParser(description="File System Analyzer")
    parser.add_argument("directory", help="Directory to analyze")
    parser.add_argument(
        "--size-threshold",
        type=int,
        default=1000000,  # Default threshold for large files (1MB)
        help="Size threshold for large files (in bytes)",
    )
    args = parser.parse_args()

    try:
        # Start directory analysis
        categories, large_files, permissions = analyze_directory(
            args.directory, args.size_threshold
        )
        print_report(categories, large_files, permissions)
    except OSError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()