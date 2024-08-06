import os
import glob
import shutil

class AnnotationUpdater:
    def __init__(self, input_dir, output_dir, class_mapping, class_names, target_classes):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.class_mapping = class_mapping
        self.class_names = class_names
        self.target_classes = set(target_classes)  # Convert to set for faster lookups
        self.error_log = []

    def update_annotations(self):
        os.makedirs(self.output_dir, exist_ok=True)
        annotation_files = glob.glob(os.path.join(self.input_dir, '*.txt'))
        for file_path in annotation_files:
            self._process_file(file_path)
        self._create_classes_file()
        self._write_error_log()

    def _process_file(self, file_path):
        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()
        except IOError as e:
            self._log_error(f"Error reading file {file_path}: {str(e)}")
            return

        updated_lines = []
        contains_target_class = False
        for line in lines:
            parts = line.strip().split()
            if not parts:
                continue

            try:
                old_class = int(parts[0])
                if old_class in self.class_mapping:
                    new_class = self.class_mapping[old_class]
                    # Only include annotations for target classes
                    if new_class in self.target_classes:
                        updated_line = f"{new_class} {' '.join(parts[1:])}\n"
                        updated_lines.append(updated_line)
                        contains_target_class = True
                else:
                    self._log_error(f"Unexpected class {old_class} in file {file_path}")
            except ValueError:
                self._log_error(f"Invalid class value in file {file_path}")

        # Only copy files if they contain annotations for target classes
        if contains_target_class:
            self._copy_files_to_output(file_path, updated_lines)

    def _copy_files_to_output(self, txt_file_path, updated_lines):
        output_txt_file = os.path.join(self.output_dir, os.path.basename(txt_file_path))
        with open(output_txt_file, 'w') as file:
            file.writelines(updated_lines)

        # Copy corresponding image file
        image_file_path = os.path.splitext(txt_file_path)[0] + '.jpg'
        if os.path.exists(image_file_path):
            shutil.copy2(image_file_path, self.output_dir)
        else:
            self._log_error(f"Image file not found for {txt_file_path}")

    def _create_classes_file(self):
        classes_file_path = os.path.join(self.output_dir, 'classes.txt')
        with open(classes_file_path, 'w') as file:
            for i, class_name in enumerate(self.class_names):
                if i in self.target_classes:
                    file.write(f"{i}: {class_name}\n")

    def _log_error(self, message):
        self.error_log.append(message)
        print(f"Error: {message}")

    def _write_error_log(self):
        if self.error_log:
            log_file_path = os.path.join(self.output_dir, 'error_log.txt')
            with open(log_file_path, 'w') as file:
                for error in self.error_log:
                    file.write(f"{error}\n")

if __name__ == "__main__":
    # Configuration to remap which goes where and so on,but make sure you dont skip a reg example 0,1,3 (dont do this)
    class_mapping = {
        0: 0,  # hard hat
        1: 3,  # gloves
        2: 1,  # safety shoes
        3: 4   # welding mask
    }

    class_names = [
        'hard hat',
        'safety shoes',
        'shoes',
        'gloves',
        'welding mask'
    ]

    # IMPORTANT: Specify the classes you want to extract here
    # The numbers should correspond to the NEW class indices after remapping
    # Examples:
    # 1. To extract only welding masks:
    # target_classes = [4]
    
    # 2. To extract hard hats and gloves:
    # target_classes = [0, 3]
    
    # 3. To extract safety shoes, gloves, and welding masks:
    # target_classes = [1, 3, 4]
    
    # 4. To extract all classes:
    # target_classes = [0, 1, 2, 3, 4]

    # Set your desired target classes here:
    target_classes = [3, 4]  # Example: extract only hard hat and welding mask

    # Set input and output directories
    input_directory = r"c:\Users\jack\Desktop\awa"
    output_directory = r"c:\Users\jack\Desktop\images-extract"

    # Create and run the updater
    updater = AnnotationUpdater(input_directory, output_directory, class_mapping, class_names, target_classes)
    updater.update_annotations()

    print(f"Annotation update complete. Extracted files are in {output_directory}")