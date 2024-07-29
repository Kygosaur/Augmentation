import os
from PIL import Image

# Define the source and output directories
source_dir = r'c:\Users\Kygo\Desktop\320-croppadded'
output_dir = r'c:\Users\Kygo\Desktop\crop-padflip'

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

def flip_coordinates(x_center, y_center, width, height):
    """Flip the x_center of the bounding box coordinates."""
    # Flip the x_center
    flipped_x_center = 1 - x_center
    # The width and height remain the same
    return flipped_x_center, y_center, width, height

def process_image_and_label(image_path, label_path, output_dir):
    """Flip an image and its corresponding label file."""
    # Load the image
    img = Image.open(image_path)
    # Flip the image
    flipped_img = img.transpose(Image.FLIP_LEFT_RIGHT)
    # Construct the output path for the flipped image
    output_image_name = os.path.basename(image_path)
    output_image_path = os.path.join(output_dir, output_image_name)
    # Save the flipped image
    flipped_img.save(output_image_path)

    # Construct the output path for the flipped label file
    output_label_name = os.path.splitext(os.path.basename(label_path))[0] + '.txt'
    output_label_path = os.path.join(output_dir, output_label_name)

    # Flip the coordinates in the label file
    with open(label_path, 'r') as infile, open(output_label_path, 'w') as outfile:
        for line in infile:
            components = line.strip().split(' ')
            try:
                class_index = components[0]
                x_center = float(components[1])
                y_center = float(components[2])
                width = float(components[3])
                height = float(components[4])
                flipped_x_center, flipped_y_center, flipped_width, flipped_height = flip_coordinates(x_center, y_center, width, height)
                outfile.write(f"{class_index} {flipped_x_center} {flipped_y_center} {flipped_width} {flipped_height}\n")
            except ValueError:
                print(f"Warning: Skipping line '{line.strip()}' due to non-numerical values.")

# Iterate over all files in the source directory
for filename in os.listdir(source_dir):
    # Check if the file is an image (e.g., .jpg, .png)
    if filename.endswith(('.jpg', '.png')):
        # Construct the full path to the image and its corresponding label file
        image_path = os.path.join(source_dir, filename)
        label_path = os.path.join(source_dir, os.path.splitext(filename)[0] + '.txt')

        # Check if the label file exists
        if os.path.exists(label_path):
            process_image_and_label(image_path, label_path, output_dir)

print("Flipped images and labels have been saved in the output directory.")