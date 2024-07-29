import os
from PIL import Image
from AnnoteCheck import count_objects_per_class

def check_bounding_boxes(annotation_file, image_path):
    with Image.open(image_path) as img:
        width, height = img.size
    
    # Normalize dimensions inside the loop
    normalized_width = 1.0 / width
    normalized_height = 1.0 / height
    
    with open(annotation_file, 'r') as file:
        for line in file:
            parts = line.strip().split()
            if len(parts) != 5:
                print(f"Invalid annotation format: {line}")
                return False
            
            class_id, x_center, y_center, box_width, box_height = map(float, parts)
            
            # Check if coordinates are within bounds
            if x_center < 0 or x_center > 1 or y_center < 0 or y_center > 1:
                print(f"Out of bounds coordinates: {line}")
                return False
            
            # Check if dimensions are correctly calculated
            if box_width <= 0 or box_height <= 0 or box_width > 1 or box_height > 1:
                print(f"Invalid bounding box dimensions: {line}")
                return False
            
            # Normalize dimensions inside the loop
            x_center_norm = x_center * normalized_width
            y_center_norm = y_center * normalized_height
            box_width_norm = box_width * normalized_width
            box_height_norm = box_height * normalized_height
            
            if x_center_norm + box_width_norm > 1 or y_center_norm + box_height_norm > 1:
                print(f"Normalized coordinates out of bounds: {line}")
                return False
    
    return True

def check_annotation_files(directory):
    files = os.listdir(directory)
    jpg_files = [f for f in files if f.endswith('.jpg')]
    
    for jpg_file in jpg_files:
        txt_file = os.path.splitext(jpg_file)[0] + '.txt'
        if txt_file not in files:
            print(f"No .txt file found for {jpg_file}.")
            continue
        
        txt_file_path = os.path.join(directory, txt_file)
        if not check_bounding_boxes(txt_file_path, os.path.join(directory, jpg_file)):
            print(f"Incorrectly formatted bounding boxes found in {txt_file}.")

if __name__ == "__main__":
    directory = r"c:\Users\Kygo\Desktop\trainHD"
    check_annotation_files(directory)
    class_counts = count_objects_per_class(directory)
    
    print("Number of objects per class:")
    for class_id, count in class_counts.items():
        print(f"Class {class_id}: {count} objects")
