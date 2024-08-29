
# SEARCH PATTERN SCRIPT
import os
import fnmatch

def search_files(base_dir, pattern):
    for root, dirs, files in os.walk(base_dir):
        for filename in fnmatch.filter(files, pattern):
            print(os.path.join(root, filename))

# Utilisation
base_directory = 'C:\\Users\\bapoh\\PycharmProjects\\Polarion_copilot'
search_pattern = '*certif*'
search_files(base_directory, search_pattern)