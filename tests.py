import unittest
import argparse
import os
import tempfile
import stat
from main import analyze_directory


class TestFileSystemAnalyzer(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory with subdirectories for testing
        self.test_dir = tempfile.TemporaryDirectory()
        self.sub_dir = os.path.join(self.test_dir.name, "subdir")
        os.mkdir(self.sub_dir)

        # Create test files
        self.create_file("test.txt", "This is a text file")
        self.create_file(
            "image.png", b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR", is_binary=True
        )
        self.create_file(
            "script.sh", "#!/bin/bash\necho Hello World", is_executable=True
        )
        self.create_file("large_file.dat", "0" * 2000000)  # Large file
        self.create_file("world_writable.txt", "Some content", world_writable=True)

        # Add files with various access permissions
        self.create_file("readable_by_others.txt", "Readable by others")
        os.chmod(
            os.path.join(self.test_dir.name, "readable_by_others.txt"), stat.S_IROTH
        )

        self.create_file(
            "executable_by_others.sh", "#!/bin/bash\necho Hello", is_executable=True
        )
        os.chmod(
            os.path.join(self.test_dir.name, "executable_by_others.sh"), stat.S_IXOTH
        )

        # Add a file with an unknown extension
        self.create_file("unknown_file.xyz", "Unknown file content")

        # Create a file in the subdirectory
        self.create_file(
            os.path.join(self.sub_dir, "subfile.txt"), "Subdirectory text file"
        )

        # Create a temporary directory for testing inaccessible directories
        self.inaccessible_dir = tempfile.TemporaryDirectory()
        self.inaccessible_dir.cleanup()  # Remove the directory to make it inaccessible

    def tearDown(self):
        # Clean up the temporary directory after tests
        self.test_dir.cleanup()

    def create_file(
        self,
        filename,
        content,
        is_binary=False,
        is_executable=False,
        world_writable=False,
    ):
        # Create a file with the specified name and content
        file_path = os.path.join(self.test_dir.name, filename)
        mode = "wb" if is_binary else "w"
        with open(file_path, mode) as f:
            f.write(content)

        # Set executable permissions
        if is_executable:
            os.chmod(file_path, os.stat(file_path).st_mode | stat.S_IEXEC)

        # Set world-writable permissions
        if world_writable:
            os.chmod(file_path, os.stat(file_path).st_mode | stat.S_IWOTH)

    def test_directory_traversal(self):
        # Test recursive directory traversal
        categories, _, _ = analyze_directory(self.test_dir.name, 1000000)
        self.assertIn(
            "text", categories
        )  # Check that files in subdirectories are analyzed

    def test_file_categorization(self):
        # Test proper file categorization
        categories, _, _ = analyze_directory(self.test_dir.name, 1000000)
        self.assertIn("text", categories)
        self.assertIn("image", categories)
        self.assertIn("unknown", categories)

    def test_size_analysis(self):
        # Test summing up file sizes by categories
        categories, _, _ = analyze_directory(self.test_dir.name, 1000000)
        self.assertGreater(categories.get("text", 0), 0)
        self.assertGreater(categories.get("image", 0), 0)

    def test_large_files_detection(self):
        # Test large file detection
        _, large_files, _ = analyze_directory(self.test_dir.name, 1000000)
        self.assertEqual(len(large_files), 1)
        self.assertIn("large_file.dat", large_files[0][0])

    def test_unusual_permissions(self):
        # Test files with unusual permissions (world-writable, readable/executable by others)
        _, _, permissions = analyze_directory(self.test_dir.name, 1000000)
        permissioned_files = [
            os.path.basename(file_path) for file_path, _ in permissions
        ]
        self.assertIn("world_writable.txt", permissioned_files)
        self.assertIn("readable_by_others.txt", permissioned_files)
        self.assertIn("executable_by_others.sh", permissioned_files)

    def test_inaccessible_directory(self):
        # Test handling of inaccessible directories
        with self.assertRaises(OSError):
            analyze_directory(self.inaccessible_dir.name, 1000000)

    def test_command_line_arguments(self):
        # Test proper handling of command-line arguments
        parser = argparse.ArgumentParser()
        parser.add_argument("directory")
        parser.add_argument("--size-threshold", type=int, default=1000000)
        args = parser.parse_args([self.test_dir.name, "--size-threshold=2000000"])
        self.assertEqual(args.directory, self.test_dir.name)
        self.assertEqual(args.size_threshold, 2000000)


if __name__ == "__main__":
    unittest.main()
