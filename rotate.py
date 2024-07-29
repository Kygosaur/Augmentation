import os
from PIL import Image
import math

# Define the source and output directories
source_dir = r'c:\Users\Kygo\Desktop\rotate'
output_dir = r'c:\Users\Kygo\Desktop\output'

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

def rotate_coordinates(x_center, y_center, width, height, angle):
    """
    Rotate the bounding box coordinates by the given angle.
    """
    # Convert angle from degrees to radians
    angle_rad = math.radians(angle)
    
    # Calculate the new coordinates
    new_x_center = x_center * math.cos(angle_rad) - y_center * math.sin(angle_rad)
    new_y_center = x_center * math.sin(angle_rad) + y_center * math.cos(angle_rad)
    
    # The width and height remain the same
    return new_x_center, new_y_center, width, height

def process_image_and_label(image_path, label_path, output_dir, angle):
    """
    Rotate an image and its corresponding label file by the given angle.
    """
    # Load the image
    img = Image.open(image_path)
    # Rotate the image
    rotated_img = img.rotate(angle)
    # Construct the output path for the rotated image
    output_image_name = os.path.splitext(os.path.basename(image_path))[0] + f'_rotate_{angle}' + os.path.splitext(image_path)[1]
    output_image_path = os.path.join(output_dir, output_image_name)
    # Save the rotated image
    rotated_img.save(output_image_path)
    
    # Construct the output path for the rotated label file
    output_label_name = os.path.splitext(os.path.basename(label_path))[0] + f'_rotate_{angle}.txt'
    output_label_path = os.path.join(output_dir, output_label_name)
    
    # Rotate the coordinates in the label file
    with open(label_path, 'r') as infile, open(output_label_path, 'w') as outfile:
        for line in infile:
            components = line.strip().split(' ')
            class_index = components[0]
            x_center = float(components[1])
            y_center = float(components[2])
            width = float(components[3])
            height = float(components[4])
            
            rotated_x_center, rotated_y_center, rotated_width, rotated_height = rotate_coordinates(x_center, y_center, width, height, angle)
            
            outfile.write(f"{class_index} {rotated_x_center} {rotated_y_center} {rotated_width} {rotated_height}\n")

# Define the rotation angle
angle = 90 # Rotate by 90 degrees

# Iterate over all files in the source directory
for filename in os.listdir(source_dir):
    # Check if the file is an image (e.g., .jpg, .png)
    if filename.endswith(('.jpg', '.png')):
        # Construct the full path to the image and its corresponding label file
        image_path = os.path.join(source_dir, filename)
        label_path = os.path.join(source_dir, os.path.splitext(filename)[0] + '.txt')
        
        # Check if the label file exists
        if os.path.exists(label_path):
            process_image_and_label(image_path, label_path, output_dir, angle)

print(f"Images and labels have been rotated by {angle} degrees and copied to the output directory with '_rotate_{angle}' appended to their names.")
