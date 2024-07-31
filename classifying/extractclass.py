import os
import glob

class AnnotationUpdater:
    def __init__(self, input_dir, output_dir, extraction_dir, class_mapping, class_names, target_classes):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.extraction_dir = extraction_dir
        self.class_mapping = class_mapping
        self.class_names = class_names
        self.error_log = []
        self.target_classes = target_classes

    def update_annotations(self):
        try:
            os.makedirs(self.output_dir, exist_ok=True)
            os.makedirs(self.extraction_dir, exist_ok=True)
        except PermissionError:
            self._log_error(f"Permission denied: Cannot create output or extraction directory")
            return

        annotation_files = glob.glob(os.path.join(self.input_dir, '*.txt'))
        
        if not annotation_files:
            self._log_error(f"No .txt files found in {self.input_dir}")
            return

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
        extracted_lines = []
        for line_num, line in enumerate(lines, 1):
            parts = line.strip().split()
            if not parts:
                continue

            try:
                old_class = parts[0].rstrip(':')  # Remove trailing colon if present
                old_class = int(old_class)
                if old_class in self.class_mapping:
                    new_class = self.class_mapping[old_class]
                    updated_line = f"{new_class} {' '.join(parts[1:])}\n"
                    updated_lines.append(updated_line)
                    if new_class in self.target_classes:
                        extracted_lines.append(updated_line)
                else:
                    self._log_error(f"Unexpected class {old_class} in file {file_path}, line {line_num}")
            except ValueError:
                self._log_error(f"Invalid class value in file {file_path}, line {line_num}")

        if updated_lines:
            output_file = os.path.join(self.output_dir, os.path.basename(file_path))
            try:
                with open(output_file, 'w') as file:
                    file.writelines(updated_lines)
            except IOError as e:
                self._log_error(f"Error writing to file {output_file}: {str(e)}")

        if extracted_lines:
            extraction_file = os.path.join(self.extraction_dir, os.path.basename(file_path))
            try:
                with open(extraction_file, 'w') as file:
                    file.writelines(extracted_lines)
            except IOError as e:
                self._log_error(f"Error writing to file {extraction_file}: {str(e)}")

    def _create_classes_file(self):
        classes_file_path = os.path.join(self.output_dir, 'classes.txt')
        try:
            with open(classes_file_path, 'w') as file:
                for class_name in self.class_names:
                    file.write(f"{class_name}\n")
            print(f"Created classes.txt file at {classes_file_path}")
        except IOError as e:
            self._log_error(f"Error creating classes.txt file: {str(e)}")

    def _log_error(self, message):
        self.error_log.append(message)
        print(f"Error: {message}")

    def _write_error_log(self):
        if self.error_log:
            log_file_path = os.path.join(self.output_dir, 'error_log.txt')
            try:
                with open(log_file_path, 'w') as file:
                    for error in self.error_log:
                        file.write(f"{error}\n")
                print(f"Error log written to {log_file_path}")
            except IOError as e:
                print(f"Error writing error log: {str(e)}")

if __name__ == "__main__":
    # Updated class mapping
    class_mapping = {
        0: 0,  # hard hat stays the same
        1: 3,  # glove moves to index 3
        2: 1,  # safety shoes stays the same
        3: 4   # welding mask moves to index 4
    }

    # Define class names in the new order
    class_names = [
        'hard hat',
        'safety shoes',
        'shoes',
        'gloves',
        'welding mask'
    ]
import os
import glob
import shutil

class AnnotationUpdater:
    def __init__(self, input_dir, output_dir, class_mapping, class_names, target_classes):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.class_mapping = class_mapping
        self.class_names = class_names
        self.error_log = []
        self.target_classes = target_classes

    def update_annotations(self):
        try:
            os.makedirs(self.output_dir, exist_ok=True)
        except PermissionError:
            self._log_error(f"Permission denied: Cannot create output directory")
            return

        annotation_files = glob.glob(os.path.join(self.input_dir, '*.txt'))
        
        if not annotation_files:
            self._log_error(f"No .txt files found in {self.input_dir}")
            return

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

        contains_target_class = False
        updated_lines = []
        for line_num, line in enumerate(lines, 1):
            parts = line.strip().split()
            if not parts:
                continue

            try:
                old_class = parts[0].rstrip(':')  # Remove trailing colon if present
                old_class = int(old_class)
                if old_class in self.class_mapping:
                    new_class = self.class_mapping[old_class]
                    updated_line = f"{new_class} {' '.join(parts[1:])}\n"
                    updated_lines.append(updated_line)
                    if new_class in self.target_classes:
                        contains_target_class = True
                else:
                    self._log_error(f"Unexpected class {old_class} in file {file_path}, line {line_num}")
            except ValueError:
                self._log_error(f"Invalid class value in file {file_path}, line {line_num}")

        if contains_target_class:
            self._copy_files_to_output(file_path, updated_lines)

    def _copy_files_to_output(self, txt_file_path, updated_lines):
        # Copy and update the .txt file
        output_txt_file = os.path.join(self.output_dir, os.path.basename(txt_file_path))
        try:
            with open(output_txt_file, 'w') as file:
                file.writelines(updated_lines)
        except IOError as e:
            self._log_error(f"Error writing to file {output_txt_file}: {str(e)}")

        # Copy the corresponding image file
        image_file_path = os.path.splitext(txt_file_path)[0] + '.jpg'  # Assuming .jpg extension
        if os.path.exists(image_file_path):
            output_image_file = os.path.join(self.output_dir, os.path.basename(image_file_path))
            try:
                shutil.copy2(image_file_path, output_image_file)
            except IOError as e:
                self._log_error(f"Error copying image file {image_file_path}: {str(e)}")
        else:
            self._log_error(f"Corresponding image file not found for {txt_file_path}")

    def _create_classes_file(self):
        classes_file_path = os.path.join(self.output_dir, 'classes.txt')
        try:
            with open(classes_file_path, 'w') as file:
                for class_name in self.class_names:
                    file.write(f"{class_name}\n")
            print(f"Created classes.txt file at {classes_file_path}")
        except IOError as e:
            self._log_error(f"Error creating classes.txt file: {str(e)}")

    def _log_error(self, message):
        self.error_log.append(message)
        print(f"Error: {message}")

    def _write_error_log(self):
        if self.error_log:
            log_file_path = os.path.join(self.output_dir, 'error_log.txt')
            try:
                with open(log_file_path, 'w') as file:
                    for error in self.error_log:
                        file.write(f"{error}\n")
                print(f"Error log written to {log_file_path}")
            except IOError as e:
                print(f"Error writing error log: {str(e)}")

if __name__ == "__main__":
    # Updated class mapping
    class_mapping = {
        0: 0,  # hard hat stays the same
        1: 3,  # glove moves to index 3
        2: 1,  # safety shoes stays the same
        3: 4   # welding mask moves to index 4
    }

    # Define class names in the new order
    class_names = [
        'hard hat',
        'safety shoes',
        'shoes',
        'gloves',
        'welding mask'
    ]

    # Define the target classes for extraction (gloves and welding mask)
    target_classes = {3, 4}

    input_directory = r"c:\Users\jack\Desktop\images"
    output_directory = r"c:\Users\jack\Desktop\output"

    updater = AnnotationUpdater(input_directory, output_directory, class_mapping, class_names, target_classes)
    updater.update_annotations()

    print(f"Annotation update complete. Files with gloves and welding mask are in {output_directory}")
    # Define the target classes for extraction
    target_classes = {3, 4}

    input_directory = r"c:\Users\jack\Desktop\train"
    output_directory = r"c:\\Users\\jack\\Desktop\\renamed"
    extraction_directory = r"c:\\Users\\jack\\Desktop\\extraction"

    updater = AnnotationUpdater(input_directory, output_directory, extraction_directory, class_mapping, class_names, target_classes)
    updater.update_annotations()

    print(f"Annotation update complete. Updated files are in {output_directory}")
    print(f"Extracted files are in {extraction_directory}")
