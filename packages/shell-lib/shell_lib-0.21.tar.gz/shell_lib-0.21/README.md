### shell-lib

`shell-lib` is a Python module designed to simplify the process of writing Shell-like scripts. With this library, you can replace complex and error-prone Shell syntax with clean, powerful Python code, while leveraging Python's robust exception handling for easy error management.

This module is lightweight and uses only the Python standard library. It was co-created with Google Gemini.

### Why shell-lib?

- **Clean Syntax**: Write your scripts in highly readable Python, leaving behind complex Shell command combinations and syntax.
- **Reliable Error Handling**: Utilize Python's built-in exception mechanism to handle errors, eliminating the need for tedious `$?` or `set -e` checks. When a command fails, it raises a `subprocess.CalledProcessError`, which you can handle like any other Python exception.
- **Unified File System Operations**: Encapsulates common file system operations from various standard library modules (like `os`, `shutil`, and `pathlib`), providing a consistent API with useful parameters like `overwrite`.

### Usage

```python
#!/usr/bin/python3
from shell_lib import sh

# `with sh:` context:
# This is a top-level context manager for handling unhandled exceptions.
# If an exception occurs within the `with` block, the program will automatically exit
# with a non-zero status code.
# Specifically, if `sh()` or `sh.safe_run()` fails, it returns the error exit code from the command.
#
# If you want to handle exceptions yourself and prevent the program from exiting, do not use this context manager.
FILE = "hello.txt"
with sh:
    # `sh.path()` returns a pathlib.Path object for easy cross-platform path manipulation.
    project_path = sh.path("my_project")
    sh.create_dir(project_path)

    # `with sh.cd():` is a directory change context manager.
    # It automatically changes to the specified directory and returns to the previous directory upon exiting,
    # regardless of whether an exception occurred.
    with sh.cd(project_path):
        # Use sh() to run commands that require shell features like pipes or redirection.
        sh(f"echo 'Hello, World!' > {FILE}")
        print(f"File size: {sh.get_file_info(FILE).size} bytes")

    sh.remove_dir(project_path)
```

### API Reference


File and Directory Operations. Path parameters can be a `str` or a `pathlib.Path` object.

```
sh.home_dir() -> Path: Gets the current user's home directory.
sh.path(path) -> Path: Converts a string to a pathlib.Path object.

sh.create_dir(path, *, exist_ok=False): Creates a directory.
sh.remove_file(path, *, ignore_missing=False): Removes a file.
sh.remove_dir(path, *, ignore_missing=False): Recursively removes a directory.
sh.copy_file(src, dst, *, overwrite=False): Copies a file.
sh.copy_dir(src, dst, *, overwrite=False): Copies a directory.
sh.move_file(src, dst, *, overwrite=False): Moves a file.
sh.move_dir(src, dst, *, overwrite=False): Moves a directory.
sh.rename_file(src, dst): Renames a file.
sh.rename_dir(src, dst): Renames a directory.

sh.get_file_info(path) -> FileSystemEntryInfo: Retrieves detailed information about a file or directory.

sh.list_dir(path) -> List[str]: Lists all entry names within a directory.
sh.walk_dir(top_dir) -> Generator[Tuple[str, str]]: A generator that traverses a directory tree.
sh.cd(path: Union[str, Path, None]): Changing the working directory. Can be used as a context manager.

sh.exists(path) -> bool: Checks if a path exists.
sh.is_file(path) -> bool: Checks if a path is a file.
sh.is_dir(path) -> bool: Checks if a path is a directory.

sh.split_path(path) -> Tuple[str, str]: Splits a path into its directory name and file name.
sh.join_path(*parts) -> str: Safely joins path components.
```

Shell Command Execution

```
Executes a command with shell=True. Use this for commands that require shell features like pipes (|) or redirection (>).
sh(command: str, *,
   print_output=True,
   text=True,
   input=None,
   timeout=None,
   fail_on_error=True) -> subprocess.CompletedProcess

Securely executes a command with shell=False. It accepts a list of strings to prevent Shell injection.
sh.safe_run(command: List[str], *,
            print_output=True,
            text=True,
            input=None,
            timeout=None,
            fail_on_error=True) -> subprocess.CompletedProcess
```

Script Control

```
sh.pause(msg=None): Prompts the user to press any key to continue.
sh.choice(title, *choices): Displays a menu and gets a 1-based index from the user's choice.
sh.exit(exit_code=0): Exits the script with a specified exit code.
sh.get_username() -> str: Get the current username.
sh.is_elevated() -> bool: If the script is running with elevated (admin/root) privileges.
sh.get_preferred_encoding(): Get the preferred encoding for the current locale.
sh.get_filesystem_encoding(): Get the encoding used by the operating system for filenames.
```