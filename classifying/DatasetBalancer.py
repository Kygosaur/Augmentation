import os
import shutil
import json
from collections import defaultdict
import random

class DatasetBalancer:
    """
    A class to balance a YOLOv7 dataset by ensuring each class has exactly 300 annotations.
    It reads from an input folder and a secondary folder, copying or moving files as needed to reach the target.
    """

    def __init__(self, input_folder, secondary_folder, output_folder, extra_folder, target_count=300):
        """
        Initialize the DatasetBalancer with input, secondary, output, and extra folders.

        :param input_folder: Path to the main input folder containing initial dataset
        :param secondary_folder: Path to the secondary folder with additional data
        :param output_folder: Path to the output folder where balanced dataset will be created
        :param extra_folder: Path to the extra folder where excess annotations will be moved
        :param target_count: Target number of annotations per class (default: 300)
        """
        self.input_folder = input_folder
        self.secondary_folder = secondary_folder
        self.output_folder = output_folder
        self.extra_folder = extra_folder
        self.target_count = target_count
        self.data = {
            "class_counts": defaultdict(int),
            "processed_files": set(),
            "class_files": defaultdict(list)
        }
        self.json_path = os.path.join(output_folder, "dataset_balance_state.json")

    def balance_dataset(self):
        """
        Main method to balance the dataset.
        """
        print("Starting dataset balancing process...")
        
        # Step 1: Count existing annotations in the input folder
        self._count_annotations(self.input_folder)
        self._save_state()
        self._print_class_counts("Initial counts from input folder:")
        
        # Step 2: Copy all files from input folder to output folder
        self._copy_folder_contents(self.input_folder, self.output_folder)
        
        # Step 3: Add annotations from secondary folder to reach target count
        self._add_annotations_from_secondary()
        self._save_state()
        self._print_class_counts("Counts after adding from secondary folder:")

        # Step 4: Remove excess annotations
        self._remove_excess_annotations()
        self._save_state()

        # Step 5: Print final class counts
        self._print_class_counts("Final class counts:")

        print("Dataset balancing completed.")

    def _count_annotations(self, folder):
        """
        Count annotations for each class in the given folder.

        :param folder: Folder to count annotations in
        """
        for filename in os.listdir(folder):
            if filename.endswith('.txt') and not filename.startswith('classes'):
                filepath = os.path.join(folder, filename)
                self._process_annotation_file(filepath, filename)

    def _process_annotation_file(self, filepath, filename):
        """
        Process a single annotation file and update class counts.

        :param filepath: Path to the annotation file
        :param filename: Name of the annotation file
        """
        with open(filepath, 'r') as file:
            for line in file:
                class_id = int(line.split()[0])
                self.data["class_counts"][class_id] += 1
                if filename not in self.data["class_files"][class_id]:
                    self.data["class_files"][class_id].append(filename)

    def _copy_folder_contents(self, src_folder, dst_folder):
        """
        Copy all contents from source folder to destination folder.

        :param src_folder: Source folder path
        :param dst_folder: Destination folder path
        """
        if not os.path.exists(dst_folder):
            os.makedirs(dst_folder)

        for item in os.listdir(src_folder):
            s = os.path.join(src_folder, item)
            d = os.path.join(dst_folder, item)
            if os.path.isfile(s):
                shutil.copy2(s, d)
                self.data["processed_files"].add(item)

    def _add_annotations_from_secondary(self):
        """
        Add annotations from the secondary folder to reach the target count for each class.
        """
        for filename in os.listdir(self.secondary_folder):
            if filename.endswith('.txt') and not filename.startswith('classes'):
                filepath = os.path.join(self.secondary_folder, filename)
                self._process_secondary_file(filepath, filename)

    def _process_secondary_file(self, filepath, filename):
        """
        Process a single file from the secondary folder and copy if needed.

        :param filepath: Path to the annotation file
        :param filename: Name of the file
        """
        with open(filepath, 'r') as file:
            for line in file:
                class_id = int(line.split()[0])
                if self.data["class_counts"][class_id] < self.target_count and filename not in self.data["processed_files"]:
                    self._copy_file_pair(self.secondary_folder, self.output_folder, filename)
                    self.data["class_counts"][class_id] += 1
                    if filename not in self.data["class_files"][class_id]:
                        self.data["class_files"][class_id].append(filename)
                    break  # Only copy once per file

    def _copy_file_pair(self, src_folder, dst_folder, filename):
        """
        Copy both the annotation file and its corresponding image file.

        :param src_folder: Source folder path
        :param dst_folder: Destination folder path
        :param filename: Name of the annotation file
        """
        base_name = os.path.splitext(filename)[0]
        for ext in ['.txt', '.jpg', '.png', '.jpeg']:
            src_path = os.path.join(src_folder, base_name + ext)
            if os.path.exists(src_path):
                dst_path = os.path.join(dst_folder, base_name + ext)
                shutil.copy2(src_path, dst_path)
        self.data["processed_files"].add(filename)

    def _remove_excess_annotations(self):
        """
        Remove excess annotations and move them to the extra folder.
        """
        if not os.path.exists(self.extra_folder):
            os.makedirs(self.extra_folder)

        for class_id, count in self.data["class_counts"].items():
            if count > self.target_count:
                excess_count = count - self.target_count
                excess_files = random.sample(self.data["class_files"][class_id], excess_count)
                
                for filename in excess_files:
                    self._move_file_pair(self.output_folder, self.extra_folder, filename)
                    self.data["class_files"][class_id].remove(filename)
                    self.data["class_counts"][class_id] -= 1
                    print(f"Moved excess file {filename} for class {class_id}")

    def _move_file_pair(self, src_folder, dst_folder, filename):
        """
        Move both the annotation file and its corresponding image file.

        :param src_folder: Source folder path
        :param dst_folder: Destination folder path
        :param filename: Name of the annotation file
        """
        base_name = os.path.splitext(filename)[0]
        for ext in ['.txt', '.jpg', '.png', '.jpeg']:
            src_path = os.path.join(src_folder, base_name + ext)
            if os.path.exists(src_path):
                dst_path = os.path.join(dst_folder, base_name + ext)
                shutil.move(src_path, dst_path)

    def _print_class_counts(self, message="Current class counts:"):
        """
        Print the current count of annotations for each class.

        :param message: Message to display before the counts
        """
        print(message)
        for class_id, count in sorted(self.data["class_counts"].items()):
            print(f"Class {class_id}: {count}")
        print()  # Add a blank line for readability

    def _save_state(self):
        """
        Save the current state of the balancing process to a JSON file.
        """
        state = {
            "class_counts": dict(self.data["class_counts"]),
            "processed_files": list(self.data["processed_files"]),
            "class_files": {k: v for k, v in self.data["class_files"].items()}
        }
        with open(self.json_path, 'w') as f:
            json.dump(state, f, indent=4)
        print(f"Saved current state to {self.json_path}")

    def _load_state(self):
        """
        Load the state of the balancing process from a JSON file.
        """
        if os.path.exists(self.json_path):
            with open(self.json_path, 'r') as f:
                state = json.load(f)
            self.data["class_counts"] = defaultdict(int, state["class_counts"])
            self.data["processed_files"] = set(state["processed_files"])
            self.data["class_files"] = defaultdict(list, state["class_files"])
            print(f"Loaded state from {self.json_path}")
        else:
            print("No saved state found. Starting fresh.")

# Usage example
if __name__ == "__main__":
    input_folder = "/path/to/input/folder"
    secondary_folder = "/path/to/secondary/folder"
    output_folder = "/path/to/output/folder"
    extra_folder = "/path/to/extra/folder"

    balancer = DatasetBalancer(input_folder, secondary_folder, output_folder, extra_folder)
    balancer._load_state()  # Try to load previous state
    balancer.balance_dataset()