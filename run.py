import sys
from src.tsu_analyzer.db.Saver import Saver

# Check if a file path is provided as a command-line argument
if len(sys.argv) < 2:
    print("Usage: pdm run python run.py <path_to_json_file>")
    sys.exit(1)

# The first argument is always the script name, so the second argument (index 1) is the file path
file_path = sys.argv[1]

saver = Saver(file_path)
saver.run()
