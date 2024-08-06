import os
import shutil
import json
from collections import defaultdict

class DatasetBalancer:
    def __init__(self, input_folder, secondary_folder, output_folder, extra_folder, target_count=300):
        self.input_folder = input_folder
        self.secondary_folder = secondary_folder
        self.output_folder = output_folder
        self.extra_folder = extra_folder
        self.target_count = target_count
        self.data = {
            "class_counts": defaultdict(int),
            "file_annotations": defaultdict(lambda: defaultdict(lambda: defaultdict(int))),
            "processed_files": set()
        }
        self.json_path = os.path.join(output_folder, "dataset_balance_state.json")
        self.class_names = []
        
        for folder in [output_folder, extra_folder]:
            os.makedirs(folder, exist_ok=True)

    def empty_folders(self):
        print("Emptying output and extra folders...")
        for folder in [self.output_folder, self.extra_folder]:
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f'Failed to delete {file_path}. Reason: {e}')
        print("Folders emptied.")

    def balance_dataset(self):
        print("Starting dataset balancing process...")
        self.empty_folders()  # Empty the folders before starting
        self._load_state()
        self._load_class_names()
        self._count_annotations(self.input_folder)
        self._count_annotations(self.secondary_folder)
        self._print_class_counts("Initial counts in input folder:")
        
        self._remove_excess_from_input()
        self._copy_remaining_input_to_output()
        self._add_files_from_secondary()
        
        self._print_class_counts("Counts before rebalancing:")
        self._rebalance_dataset()
        
        self._save_state()
        self._print_final_counts()

    def _load_class_names(self):
        classes_file = os.path.join(self.input_folder, "classes.txt")
        if os.path.exists(classes_file):
            with open(classes_file, 'r') as f:
                self.class_names = [line.strip().split(': ')[-1] for line in f.readlines()]
            print(f"Loaded class names: {self.class_names}")
        else:
            print("Warning: classes.txt not found. Class names will be unknown.")

    def _count_annotations(self, folder):
        print(f"Counting annotations in folder: {folder}")
        for filename in os.listdir(folder):
            if filename.endswith(".txt") and filename != "classes.txt":
                filepath = os.path.join(folder, filename)
                self._process_annotation_file(filepath, filename, folder)

    def _process_annotation_file(self, filepath, filename, folder):
        with open(filepath, 'r') as file:
            for line in file:
                try:
                    parts = line.split()
                    if len(parts) < 5:  # YOLO format should have at least 5 parts
                        raise ValueError("Not enough parts in the annotation line")
                    class_id = int(parts[0])
                    self.data["file_annotations"][folder][filename][class_id] += 1
                    if folder == self.output_folder:
                        self.data["class_counts"][class_id] += 1
                except (ValueError, IndexError) as e:
                    print(f"Skipping line in file {filename} due to invalid format: {line.strip()} (Error: {str(e)})")

    def _remove_excess_from_input(self):
        print("Removing excess files from input folder...")
        input_counts = defaultdict(int)
        for filename, annotations in self.data["file_annotations"][self.input_folder].items():
            for class_id, count in annotations.items():
                input_counts[class_id] += count

        files_to_remove = []
        for class_id, count in input_counts.items():
            if count > self.target_count:
                excess = count - self.target_count
                for filename, annotations in self.data["file_annotations"][self.input_folder].items():
                    if class_id in annotations:
                        files_to_remove.append(filename)
                        excess -= annotations[class_id]
                        if excess <= 0:
                            break

        for filename in files_to_remove:
            self._move_file_to_extra(self.input_folder, filename)

    def _copy_remaining_input_to_output(self):
        print("Copying remaining files from input to output...")
        for filename in os.listdir(self.input_folder):
            if filename.endswith(".txt") and filename != "classes.txt":
                self._move_file_to_output(self.input_folder, filename)

    def _add_files_from_secondary(self):
        print("Adding files from secondary folder to reach target count...")
        for class_id in range(len(self.class_names)):
            needed = self.target_count - self.data["class_counts"][class_id]
            if needed > 0:
                self._add_files_for_class(class_id, needed)

    def _add_files_for_class(self, class_id, needed):
        added = 0
        for filename, annotations in self.data["file_annotations"][self.secondary_folder].items():
            if class_id in annotations and filename not in self.data["processed_files"]:
                self._move_file_to_output(self.secondary_folder, filename)
                added += annotations[class_id]
                if added >= needed:
                    break
        
        if added < needed:
            print(f"Warning: Unable to find enough files for class {class_id} ({self.class_names[class_id] if class_id < len(self.class_names) else 'Unknown'}). Added {added} out of {needed} needed.")

    def _move_file_to_output(self, source_folder, filename):
        src_path = os.path.join(source_folder, filename)
        dest_path = os.path.join(self.output_folder, filename)
        shutil.copy2(src_path, dest_path)
        self._copy_corresponding_image(source_folder, self.output_folder, filename)
        self.data["processed_files"].add(filename)
        
        annotations = self.data["file_annotations"][source_folder][filename]
        self.data["file_annotations"][self.output_folder][filename] = annotations
        
        for class_id, count in annotations.items():
            self.data["class_counts"][class_id] += count

    def _move_file_to_extra(self, source_folder, filename):
        src_path = os.path.join(source_folder, filename)
        dest_path = os.path.join(self.extra_folder, filename)
        if os.path.exists(src_path):
            shutil.move(src_path, dest_path)
            self._move_corresponding_image(source_folder, self.extra_folder, filename)
        else:
            print(f"Warning: File {filename} not found in {source_folder}")
        
        if source_folder in self.data["file_annotations"] and filename in self.data["file_annotations"][source_folder]:
            del self.data["file_annotations"][source_folder][filename]

    def _copy_corresponding_image(self, source_folder, dest_folder, annotation_filename):
        base_name = os.path.splitext(annotation_filename)[0]
        for ext in ['.jpg', '.jpeg', '.png']:
            img_filename = base_name + ext
            src_path = os.path.join(source_folder, img_filename)
            dest_path = os.path.join(dest_folder, img_filename)
            if os.path.exists(src_path):
                shutil.copy2(src_path, dest_path)
                break

    def _move_corresponding_image(self, source_folder, dest_folder, annotation_filename):
        base_name = os.path.splitext(annotation_filename)[0]
        for ext in ['.jpg', '.jpeg', '.png']:
            img_filename = base_name + ext
            src_path = os.path.join(source_folder, img_filename)
            dest_path = os.path.join(dest_folder, img_filename)
            if os.path.exists(src_path):
                shutil.move(src_path, dest_path)
                break

    def _print_class_counts(self, message):
        print(message)
        if not self.data["class_counts"]:
            print("No annotations found.")
        else:
            for class_id, count in sorted(self.data["class_counts"].items()):
                class_name = self.class_names[class_id] if class_id < len(self.class_names) else "Unknown"
                print(f"Class {class_id} ({class_name}): {count}")
        print()

    def _save_state(self):
        state = {
            "class_counts": dict(self.data["class_counts"]),
            "file_annotations": {folder: {file: dict(annots) for file, annots in folder_data.items()} 
                                 for folder, folder_data in self.data["file_annotations"].items()},
            "processed_files": list(self.data["processed_files"]),
            "target_count": self.target_count
        }
        with open(self.json_path, 'w') as f:
            json.dump(state, f, indent=4)
        print(f"Saved current state to {self.json_path}")

    def _load_state(self):
        if os.path.exists(self.json_path):
            with open(self.json_path, 'r') as f:
                state = json.load(f)
            self.data["class_counts"] = defaultdict(int, state["class_counts"])
            self.data["file_annotations"] = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
            for folder, folder_data in state["file_annotations"].items():
                for file, annots in folder_data.items():
                    self.data["file_annotations"][folder][file] = defaultdict(int, annots)
            self.data["processed_files"] = set(state["processed_files"])
            self.target_count = state.get("target_count", self.target_count)
            print(f"Loaded state from {self.json_path}")
        else:
            print("No saved state found. Starting fresh.")

    def _rebalance_dataset(self):
        iteration = 0
        max_iterations = 100  # Prevent infinite loops
        while iteration < max_iterations:
            iteration += 1
            print(f"\nRebalancing iteration {iteration}")
            changes_made = False
            
            for class_id, count in self.data["class_counts"].items():
                if count > self.target_count:
                    print(f"Class {class_id} is over target ({count} > {self.target_count})")
                    removed = self._remove_excess_for_class(class_id, count - self.target_count)
                    if removed > 0:
                        changes_made = True
                        print(f"Removed {removed} annotations for class {class_id}")
                elif count < self.target_count:
                    print(f"Class {class_id} is under target ({count} < {self.target_count})")
                    added = self._add_files_for_class(class_id, self.target_count - count)
                    if added > 0:
                        changes_made = True
                        print(f"Added {added} annotations for class {class_id}")
            
            self._print_class_counts(f"Counts after rebalancing iteration {iteration}:")
            
            if all(count == self.target_count for count in self.data["class_counts"].values()):
                print("All classes have exactly the target count. Rebalancing complete.")
                break
            
            if not changes_made:
                print("No changes made in this iteration. Rebalancing complete.")
                break
        
        if iteration == max_iterations:
            print("Warning: Reached maximum number of iterations. Rebalancing may be incomplete.")

    def _remove_excess_for_class(self, class_id, excess):
        removed = 0
        files_to_process = list(self.data["file_annotations"][self.output_folder].items())
        for filename, annotations in files_to_process:
            if class_id in annotations:
                annotations_in_file = annotations[class_id]
                annotations_to_remove = min(annotations_in_file, excess - removed)
                self._remove_annotations_from_file(filename, class_id, annotations_to_remove)
                removed += annotations_to_remove
                if removed >= excess:
                    break
        return removed

    def _remove_annotations_from_file(self, filename, class_id, count_to_remove):
        filepath = os.path.join(self.output_folder, filename)
        extra_filepath = os.path.join(self.extra_folder, filename)
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        new_lines = []
        extra_lines = []
        removed = 0
        for line in lines:
            if int(line.split()[0]) == class_id and removed < count_to_remove:
                extra_lines.append(line)
                removed += 1
            else:
                new_lines.append(line)
        
        with open(filepath, 'w') as f:
            f.writelines(new_lines)
        
        with open(extra_filepath, 'a') as f:
            f.writelines(extra_lines)
        
        self.data["file_annotations"][self.output_folder][filename][class_id] -= removed
        self.data["class_counts"][class_id] -= removed

    def _print_final_counts(self):
        print("\nFinal true annotations per class:")
        total_annotations = 0
        for class_id, count in sorted(self.data["class_counts"].items()):
            class_name = self.class_names[class_id] if class_id < len(self.class_names) else "Unknown"
            print(f"Class {class_id} ({class_name}): {count}")
            total_annotations += count
        print(f"\nTotal annotations: {total_annotations}")
        print(f"Average annotations per class: {total_annotations / len(self.data['class_counts']):.2f}")

if __name__ == "__main__":
    input_folder = r"c:\Users\jack\Desktop\test"
    secondary_folder = r"c:\Users\jack\Desktop\aspect-640"
    output_folder = r"c:\Users\jack\Desktop\true_val"
    extra_folder = r"c:\Users\jack\Desktop\extra"
    
    target_annotations = 400

    balancer = DatasetBalancer(input_folder, secondary_folder, output_folder, extra_folder, target_count=target_annotations)
    balancer.balance_dataset()