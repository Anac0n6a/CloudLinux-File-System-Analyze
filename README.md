# File System Analyzer Documentation

## Table of Contents
1. [Overview](#1-overview)
2. [Features](#2-features)
3. [Dependencies](#3-dependencies)
4. [How to Run](#4-how-to-run)
    - [Prerequisites](#41-prerequisites)
    - [Command to Run](#42-command-to-run)
    - [Arguments](#43-arguments)
5. [Output](#5-output)
6. [Error Handling](#6-error-handling)
7. [Example Output](#7-example-output)
8. [Running the Tests](#8-running-the-tests)
    - [To Run Tests](#81-to-run-tests)
    - [Test Example Output](#82-test-example-output)
9. [Contact information](#9-contact-information)

---

## 1. Overview 

The **File System Analyzer** is a Python tool designed to scan directories, categorize files by type, identify large files, and detect unusual file permissions. The tool is efficient, supporting parallel processing for handling large directories and includes robust error handling for inaccessible directories and files.

---

## 2. Features

- **File Categorization**: Automatically categorizes files based on extensions or MIME types.
- **Large File Detection**: Identifies files larger than a user-defined size threshold.
- **Permission Analysis**: Detects files with unusual permissions (writable, readable, or executable by others).
- **Parallel Processing**: Supports multi-threading for faster analysis of large directories.

---

## 3. Dependencies

The tool only uses Python standard libraries, so no external packages are needed. Here’s a list of modules used:

- **os**: For directory and file operations.
- **mimetypes**: For guessing file MIME types.
- **argparse**: For command-line argument parsing.
- **stat**: For analyzing file permissions.
- **collections**: For managing file categories.
- **concurrent.futures**: For parallel processing with ThreadPoolExecutor.

---

## 4. How to Run

### 4.1 Prerequisites

- **Python 3.6 or higher** is required to run the tool.

### 4.2 Command to Run

1. Open a terminal or command prompt.
2. Navigate to the directory containing the script.
3. Run the following command to analyze a directory:

```bash
python main.py /path/to/directory --size-threshold 1000000
```

### 4.3 Arguments

- **directory**: The directory to analyze.
- **--size-threshold**: (Optional) Set the size threshold for detecting large files (in bytes). The default is 1 MB (1,000,000 bytes).

Example:

```bash
python main.py /home/user/docs --size-threshold 2000000
```

---

## 5. Output

The tool will display a report with the following sections:
- **File Categories and Their Total Size**: A summary of file types (e.g., text, image) and the total size for each category.
- **Large Files**: A list of files that exceed the specified size threshold.
- **Files with Unusual Permissions**: A list of files with potentially insecure permissions.

---

## 6. Error Handling

The tool gracefully handles common issues such as:
- **Inaccessible directories**: It reports directories that cannot be accessed.
- **Missing files**: It skips missing files with appropriate warnings.

---

## 7. Example Output

Here’s an example of the tool’s output:

```
File Categories and Their Total Size:
Document: 5,421,232 bytes
Image: 1,232,000 bytes
Text: 643,123 bytes

Large Files:
- /path/to/largefile1.txt: 10,232,312 bytes
- /path/to/largefile2.pdf: 8,432,000 bytes

Files with Unusual Permissions:
- /path/to/file.sh: Writable by others
- /path/to/anotherfile.txt: Executable by others
```

---

## 8. Running the Tests

Unit tests are provided in the `tests.py` file to ensure all functionality works as expected.

### 8.1 To Run Tests

Use Python's `unittest` module to execute the tests:

```bash
python -m unittest tests.py
```

### 8.2 Test Example Output

Here’s an example of the test output:

```
test_directory_traversal (tests.TestFileSystemAnalyzer) ... ok
test_file_categorization (tests.TestFileSystemAnalyzer) ... ok
test_size_analysis (tests.TestFileSystemAnalyzer) ... ok
test_large_files_detection (tests.TestFileSystemAnalyzer) ... ok
test_unusual_permissions (tests.TestFileSystemAnalyzer) ... ok
test_inaccessible_directory (tests.TestFileSystemAnalyzer) ... ok
test_command_line_arguments (tests.TestFileSystemAnalyzer) ... ok

----------------------------------------------------------------------
Ran 7 tests in 0.045s

OK
```

---

## 9. Contact information 
Completed by Timofey Shmakov  
Contacts for communication:
- email: timofei.schmackov@yandex.ru
- telegram: https://t.me/tim31560
