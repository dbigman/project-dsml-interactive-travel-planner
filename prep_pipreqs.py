import os
import chardet

def detect_encoding(file_path):
    """Detects the encoding of a file.

    This function opens a file in binary mode and uses the `chardet` library
    to analyze the contents of the file to determine its character encoding.
    It reads the entire file and returns the detected encoding type, which
    can be useful for correctly interpreting the file's contents.

    Args:
        file_path (str): The path to the file whose encoding is to be detected.

    Returns:
        str: The detected encoding of the file.
    """
    with open(file_path, "rb") as f:
        result = chardet.detect(f.read())
    return result["encoding"]

def convert_to_utf8(file_path):
    """Convert a file to UTF-8 encoding if it is not already in that format.

    This function detects the current encoding of the specified file. If the
    file's encoding is not UTF-8, it reads the content of the file and
    writes it back in UTF-8 encoding. This process ensures that the file is
    properly converted without data loss.

    Args:
        file_path (str): The path to the file that needs to be converted.
    """
    encoding = detect_encoding(file_path)
    if encoding and encoding.lower() != "utf-8":
        print(f"Converting {file_path} from {encoding} to UTF-8")
        try:
            with open(file_path, "r", encoding=encoding) as f:
                content = f.read()
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            print(f"Error converting {file_path}: {e}")

# Scan and convert all text files in the project
for root, _, files in os.walk("."):
    for file in files:
        if file.endswith((".py", ".txt", ".ipynb")):
            convert_to_utf8(os.path.join(root, file))
