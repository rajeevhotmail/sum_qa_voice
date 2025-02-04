from tree_sitter import Language
import os

# Path to the compiled shared library (.so)
LIBRARY_PATH = os.path.expanduser("~/.tree-sitter/tree-sitter-python.so")

# Load the Python parser
python_language = Language(LIBRARY_PATH, "python")

print("Python parser loaded successfully!")
