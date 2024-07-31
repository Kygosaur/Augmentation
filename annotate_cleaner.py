import os
import glob
import shutil

class AnnotationCleaner:
    def __init__(self, input_dir, output_dir, keep_classes, new_class_names):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.keep_classes = keep_classes
        self.new_class_names = new_class_names

    def clean_annotations(self):
        os.makedirs(self.output_dir, exist_ok=True)
        annotation_files = glob.glob(os.path.join(self.input_dir, '*.txt'))
        
        print(f"Found {len(annotation_files)} annotation files to process.")
        
        for file_path in annotation_files:
            try:
                self._process_file(file_path)
            except Exception as e:
                print(f"Error processing file {file_path}: {str(e)}")
        
        self._create_classes_file()

    def _process_file(self, file_path):
        print(f"Processing file: {file_path}")
        with open(file_path, 'r') as file:
            lines = file.readlines()
        
        updated_lines = []
        for line in lines:
            parts = line.strip().split()
            if parts:
                try:
                    old_class = int(parts[0].rstrip(':'))
                    if old_class in self.keep_classes:
                        new_class = self.keep_classes[old_class]
                        if ':' in parts[0]:
                            updated_line = f"{new_class}: {' '.join(parts[1:])}\n"
                        else:
                            updated_line = f"{new_class} {' '.join(parts[1:])}\n"
                        updated_lines.append(updated_line)
                    else:
                        print(f"  Removing annotation with class {old_class}")
                except ValueError:
                    print(f"  Skipping invalid line: {line.strip()}")
        
        if updated_lines:
            output_file = os.path.join(self.output_dir, os.path.basename(file_path))
            with open(output_file, 'w') as file:
                file.writelines(updated_lines)
            print(f"  Wrote {len(updated_lines)} annotations to {output_file}")
            self._copy_related_image(file_path)
        else:
            print(f"  No annotations left after cleaning, skipping output file")

    def _copy_related_image(self, annotation_file_path):
        base_name = os.path.splitext(os.path.basename(annotation_file_path))[0]
        for ext in ['.jpg', '.jpeg', '.png', '.bmp']:
            image_file = os.path.join(self.input_dir, base_name + ext)
            if os.path.exists(image_file):
                dest_file = os.path.join(self.output_dir, os.path.basename(image_file))
                shutil.copy2(image_file, dest_file)
                print(f"  Copied related image: {dest_file}")
                return
        print(f"  No related image found for {annotation_file_path}")

    def _create_classes_file(self):
        classes_file_path = os.path.join(self.output_dir, 'classes.txt')
        with open(classes_file_path, 'w') as file:
            for class_name in self.new_class_names:
                file.write(f"{class_name}\n")
        print(f"Created classes.txt file at {classes_file_path}")

if __name__ == "__main__":
    keep_classes = {
        1: 3,  #initial class changed to new 
        3: 4,  
    }

    new_class_names = [
        'hard hat',
        'safety shoes',
    ]

    input_directory = r"c:\Users\jack\Desktop\awa"
    output_directory = r"c:\Users\jack\Desktop\removed"

    cleaner = AnnotationCleaner(input_directory, output_directory, keep_classes, new_class_names)
    cleaner.clean_annotations()

    print(f"Annotation cleaning complete. Cleaned files and related images are in {output_directory}")