import os
import glob
import shutil

class AnnotationUpdater:
    """
    A class to update annotation files for object detection datasets.
    It remaps class IDs and handles error logging.
    """

    def __init__(self, input_dir, output_dir, class_mapping, class_names):
        """
        Initialize the AnnotationUpdater with input and output directories,
        class mapping, and new class names.

        :param input_dir: Directory containing original annotation files
        :param output_dir: Directory to save updated annotation files
        :param class_mapping: Dictionary mapping old class IDs to new class IDs
        :param class_names: List of new class names for the updated dataset
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.class_mapping = class_mapping
        self.class_names = class_names
        self.error_log = []

    def update_annotations(self):
        """
        Main method to process all annotation files in the input directory.
        It creates the output directory, processes each file, copies images,
        creates a classes file, and writes an error log if necessary.
        """
        try:
            os.makedirs(self.output_dir, exist_ok=True)
        except PermissionError:
            self._log_error(f"Permission denied: Cannot create output directory {self.output_dir}")
            return

        # Find all annotation and image files
        annotation_files = glob.glob(os.path.join(self.input_dir, '*.txt'))
        image_files = glob.glob(os.path.join(self.input_dir, '*.jpg')) + glob.glob(os.path.join(self.input_dir, '*.png'))
        
        if not annotation_files:
            self._log_error(f"No .txt files found in {self.input_dir}")
        
        # Process each annotation file
        for file_path in annotation_files:
            self._process_file(file_path)
        
        # Copy each image file
        for image_path in image_files:
            self._copy_image(image_path)
        
        # Create classes.txt file and write error log if any errors occurred
        self._create_classes_file()
        self._write_error_log()

    def _process_file(self, file_path):
        """
        Process a single annotation file.
        It reads the file, updates class IDs, and writes the updated annotations.

        :param file_path: Path to the annotation file to process
        """
        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()
        except IOError as e:
            self._log_error(f"Error reading file {file_path}: {str(e)}")
            return

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
                else:
                    self._log_error(f"Unexpected class {old_class} in file {file_path}, line {line_num}")
                    updated_lines.append(line)
            except ValueError:
                self._log_error(f"Invalid class format '{parts[0]}' in file {file_path}, line {line_num}")
                updated_lines.append(line)

        output_file = os.path.join(self.output_dir, os.path.basename(file_path))
        try:
            with open(output_file, 'w') as file:
                file.writelines(updated_lines)
        except IOError as e:
            self._log_error(f"Error writing to file {output_file}: {str(e)}")

    def _copy_image(self, image_path):
        """
        Copy an image file to the output directory.

        :param image_path: Path to the image file to copy
        """
        output_image_path = os.path.join(self.output_dir, os.path.basename(image_path))
        try:
            shutil.copy2(image_path, output_image_path)
        except IOError as e:
            self._log_error(f"Error copying image {image_path} to {output_image_path}: {str(e)}")

    def _create_classes_file(self):
        """
        Create a classes.txt file in the output directory
        containing the new class names.
        """
        classes_file_path = os.path.join(self.output_dir, 'classes.txt')
        try:
            with open(classes_file_path, 'w') as file:
                for class_name in self.class_names:
                    file.write(f"{class_name}\n")
            print(f"Created classes.txt file at {classes_file_path}")
        except IOError as e:
            self._log_error(f"Error creating classes.txt file: {str(e)}")

    def _log_error(self, message):
        """
        Log an error message to the error_log list and print it.

        :param message: Error message to log
        """
        self.error_log.append(message)
        print(f"Error: {message}")

    def _write_error_log(self):
        """
        Write all logged errors to an error_log.txt file in the output directory.
        """
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
    """
    Main execution block to demonstrate usage of the AnnotationUpdater class.
    """
    # Define the class mapping from old to new class IDs
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

    # Set input and output directories
    input_directory = r"c:\Users\jack\Desktop\labels"
    output_directory = r"c:\Users\jack\Desktop\val"

    # Create an instance of AnnotationUpdater and run the update process
    updater = AnnotationUpdater(input_directory, output_directory, class_mapping, class_names)
    updater.update_annotations()

    print(f"Annotation update complete. Updated files are in {output_directory}")