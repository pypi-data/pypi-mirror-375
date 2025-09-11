"""
Filehandls - a library to handle files
"""

def read(path: str) -> str | None:
    """
    read(path) -> str | None
    Reads a file and returns it's contents as a string.
    Returns None if the file does not exist.
    """
    try:
        with open(path, "r") as f: 
            return f.read()
    except FileNotFoundError:
        return None


def write(path: str, contents, overwrite: bool = True) -> int | None:
    """
    write(path, contents, overwrite=True) -> int | None
    Writes contents to a file.
    - If overwrite=True, existing files will be replaced.
    - If overwrite=False and file exists, returns None.
    - Returns 0 on success.
    """
    mode = "w" if overwrite else "x"
    try:
        with open(path, mode) as f:
            f.write(str(contents))  # ensure it writes
        return 0
    except FileExistsError:
        return None

def append(path: str, contents) -> None | int:
    """append()
    Appends content to an file using the path
    If the file exists, appends content
    If the file does NOT exists, return 1
    """
    try:
        with open(path, "a") as f:
            f.write(contents)
    except FileNotFoundError:
        return 1
    
import os

def delete(path: str) -> int:
    """
    delete(path) -> int
    Deletes a file.
    Returns 0 if deleted successfully.
    Returns 1 if the file does not exist.
    """
    try:
        os.remove(path)
        return 0
    except FileNotFoundError:
        return 1


def exists(path: str) -> bool:
    """
    exists(path) -> bool
    Check if a file exists.
    Returns True if the file exists, False otherwise.
    """
    return os.path.exists(path)
