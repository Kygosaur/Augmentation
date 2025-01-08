import os
import yaml
import shutil
from datetime import datetime

def load_yaml_config(yaml_path):
    """
    Read the YAML configuration file to get class information.
    
    :param yaml_path: Path to the YAML file containing class configuration
    :return: Dictionary with number of classes and their names
    """
    with open(yaml_path, 'r') as file:
        config = yaml.safe_load(file)
    
    return {
        'num_classes': config.get('nc', 0),
        'class_names': config.get('names', [])
    }

def find_max_class_in_annotations(input_folder):
    """
    Find the highest class number in all annotation files.
    
    :param input_folder: Folder containing YOLO annotation text files
    :return: Highest class number found in the annotations
    """
    max_class = -1
    
    for filename in os.listdir(input_folder):
        if filename.endswith('.txt'):
            file_path = os.path.join(input_folder, filename)
            
            with open(file_path, 'r') as file:
                for line in file:
                    # Split and clean the line
                    parts = line.strip().split()
                    if parts:
                        try:
                            # Try to extract the class number, handling different formats
                            class_part = parts[0]
                            
                            # Remove any ':' or other non-numeric characters
                            class_num = int(''.join(filter(str.isdigit, class_part)))
                            
                            max_class = max(max_class, class_num)
                        except (ValueError, IndexError):
                            # Skip lines that can't be parsed
                            print(f"Warning: Could not parse line in {filename}: {line.strip()}")
    
    return max_class

def remap_class_annotations(input_folder,       # Folder with annotation files #
    yaml_path,          # Path to the YAML configuration file
    class_mapping=None, # Optional: Custom class mapping
    add_new_classes=None, # Optional: List of new classes to add
    output_base=None,
    copy_images=True   # New parameter to control image copying
):
    """
    Modify class annotations and create a new output directory with remapped files.
    
    Returns:
    - Path to the new output directory
    - Path to the new classes.txt file
    """
    # Create a timestamped output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_base = os.path.dirname(input_folder)
    output_folder = os.path.join(output_base, f"remapped_annotations_{timestamp}")
    os.makedirs(output_folder, exist_ok=True)
    
    # Load the current class configuration from YAML
    config = load_yaml_config(yaml_path)
    
    # Create a default 1:1 mapping if no custom mapping provided
    if class_mapping is None:
        class_mapping = {i: i for i in range(config['num_classes'])}
    
    # Validate the class mapping
    max_original_class = max(class_mapping.keys())
    if max_original_class >= config['num_classes']:
        raise ValueError(
            f"Class mapping contains class {max_original_class}, "
            f"but configuration only defines {config['num_classes']} classes"
        )
    
    # Find the highest class number in existing annotations
    max_existing_class = find_max_class_in_annotations(input_folder)
    
    # Prepare class names for mapping and new classes
    class_names = config['class_names'].copy()
    
    # Handle adding new classes
    if add_new_classes:
        # Start new class numbers after the highest existing class
        new_class_start = max_existing_class + 1
        
        # Map new classes to sequential numbers
        for i, new_class_name in enumerate(add_new_classes):
            class_mapping[config['num_classes'] + i] = new_class_start + i
            class_names.append(new_class_name)
        
        # Update the YAML configuration file
        with open(yaml_path, 'r') as file:
            yaml_config = yaml.safe_load(file)
        
        # Increase total number of classes and add new class names
        yaml_config['nc'] = len(yaml_config['names']) + len(add_new_classes)
        yaml_config['names'].extend(add_new_classes)
        
        # Write updated configuration back to the YAML file
        with open(yaml_path, 'w') as file:
            yaml.dump(yaml_config, file)
        
        print(f"Added new classes: {add_new_classes}")
    
    # Create classes.txt file in the output directory
    classes_txt_path = os.path.join(output_folder, 'classes.txt')
    with open(classes_txt_path, 'w') as f:
        for idx, (orig_name, mapped_class) in enumerate(
            zip(class_names, range(len(class_names)))
        ):
            # Find the original class that maps to this new class number
            original_class = next(
                (orig for orig, mapped in class_mapping.items() 
                 if mapped == mapped_class), 
                mapped_class
            )
            f.write(f"{mapped_class}: {orig_name} (originally class {original_class})\n")
    
    # Process each annotation file and copy to new directory
    for filename in os.listdir(input_folder):
        if filename.endswith('.txt'):
            file_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)
            
            # Read existing annotations
            with open(file_path, 'r') as file:
                lines = file.readlines()
            
            # Remap class annotations
            remapped_lines = []
            for line in lines:
                parts = line.strip().split()
                if parts:
                    # Extract only digits from the first part
                    original_class = int(''.join(filter(str.isdigit, parts[0])))
                    
                    # Change class number if it's in the mapping
                    if original_class in class_mapping:
                        parts[0] = str(class_mapping[original_class])
                    
                    # Reconstruct the line with new class number
                    remapped_lines.append(' '.join(parts) + '\n')
            
            # Write updated annotations to the new file
            with open(output_path, 'w') as file:
                file.writelines(remapped_lines)
        
        # Copy corresponding images if they exist
        if copy_images:
            # Try different image extensions
            image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
            base_filename = os.path.splitext(filename)[0]
            
            for ext in image_extensions:
                image_path = os.path.join(input_folder, base_filename + ext)
                if os.path.exists(image_path):
                    shutil.copy2(image_path, output_folder)
                    print(f"Copied image: {base_filename + ext}")
                    break
    
    print(f"Class annotations remapped successfully!")
    print(f"\n🗂️ Output Directory: {output_folder}")
    print(f"📄 Classes Mapping: {classes_txt_path}")
    
    return output_folder, classes_txt_path

def print_current_classes(yaml_path):
    """
    Display the current classes defined in the YAML configuration.
    
    :param yaml_path: Path to the YAML configuration file
    """
    # Load and print class information
    config = load_yaml_config(yaml_path)
    print("Current Classes:")
    for idx, name in enumerate(config['class_names']):
        print(f"{idx}: {name}")

# Main script execution
if __name__ == "__main__":
    # IMPORTANT: Replace these paths with your actual paths
    YAML_CONFIG_PATH = r'C:\Users\USER\OneDrive\Desktop\projects\Yolo Ultralytics\custom.yaml'
    ANNOTATION_FOLDER = r"C:\Users\USER\OneDrive\Desktop\projects-ai recognition\640-original"
    
    # STEP 1: View current class configuration
    print("Step 1: Current Class Configuration")
    print_current_classes(YAML_CONFIG_PATH)
    
    # STEP 2: Define class mapping
    example_mapping = {
        0: 1,   # Change original class 0 to class 1
        1: 4,   # Change original class 1 to class 4
        2: 2,   # Keep original class 2 as class 2
        3: 3,   # Keep original class 3 as class 3
        4: 5,    # Change original class 4 to class 5
    }
    
    # STEP 3: Optional - Add new classes
    new_classes_to_add = []
    
    # STEP 4: Remap annotations
    print("\nStep 2: Remapping Annotations")
    output_dir, classes_map_path = remap_class_annotations(
        ANNOTATION_FOLDER,        # Folder with annotation files
        YAML_CONFIG_PATH,         # YAML configuration file
        class_mapping=example_mapping,  # Class number changes
        add_new_classes=new_classes_to_add,  # New classes to add
        copy_images=True  # New parameter to copy images
    )
    
    # STEP 5: Verify updated classes
    print("\nStep 3: Updated Class Configuration")
    print_current_classes(YAML_CONFIG_PATH)

# INSTRUCTIONS FOR USE:
# 1. Install required libraries: 'pip install pyyaml'
# 2. Replace YAML_CONFIG_PATH with path to your custom.yaml
# 3. Replace ANNOTATION_FOLDER with path to your annotation files
# 4. Customize example_mapping to match your desired class changes
# 5. Customize new_classes_to_add if you want to add classes
# 6. Run the script