import os
import shutil
import json

def check_and_move_files(source_folder, wrong_folder):
    if not os.path.exists(wrong_folder):
        os.makedirs(wrong_folder)

    file_pairs = {}
    inadequate_files = {}

    # First pass: gather all files and their base names
    for filename in os.listdir(source_folder):
        base_name, ext = os.path.splitext(filename)
        if ext.lower() in ['.txt', '.jpg', '.jpeg', '.png', '.gif']:
            if base_name not in file_pairs:
                file_pairs[base_name] = []
            file_pairs[base_name].append(filename)

    # Second pass: check for unpaired files and move them
    for base_name, files in file_pairs.items():
        if len(files) == 1:
            file_to_move = files[0]
            source_path = os.path.join(source_folder, file_to_move)
            dest_path = os.path.join(wrong_folder, file_to_move)
            shutil.move(source_path, dest_path)
            
            ext = os.path.splitext(file_to_move)[1].lower()
            file_type = 'text' if ext == '.txt' else 'image'
            
            if file_type not in inadequate_files:
                inadequate_files[file_type] = 0
            inadequate_files[file_type] += 1

    # Create JSON file with inadequate file information
    json_path = os.path.join(source_folder, 'inadequate_files.json')
    with open(json_path, 'w') as json_file:
        json.dump(inadequate_files, json_file, indent=4)

    print(f"Moved {sum(inadequate_files.values())} unpaired files to {wrong_folder}")
    print(f"Created {json_path} with information about inadequate files")

# Usage
source_folder = 'path/to/your/source/folder'
wrong_folder = 'path/to/your/wrong/folder'

check_and_move_files(source_folder, wrong_folder)