import os
import chardet

def detect_encoding(file_path):
    """Detects the encoding of a file."""
    with open(file_path, "rb") as f:
        result = chardet.detect(f.read())
    return result["encoding"]

def convert_to_utf8(file_path):
    """Converts a file to UTF-8 if it's not already."""
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
