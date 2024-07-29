import os
from PIL import Image
import shutil

# Define the source and output directories
source_dir = r'c:\Users\Kygo\Desktop\crop-original'
output_dir = r'c:\Users\Kygo\Desktop\320-croppadded'

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Define the target size for padding
target_size = (640, 640)

def process_image(image_path, output_dir):
    """Pad an image to the target size."""
    # Load the image
    img = Image.open(image_path)

    # Get the current size of the image
    current_width, current_height = img.size

    # Calculate the padding needed for each dimension
    pad_width = (target_size[0] - current_width) // 2
    pad_height = (target_size[1] - current_height) // 2

    # Create a new image with the target size and white background
    padded_img = Image.new('RGB', target_size, (0, 0, 255))

    # Paste the original image onto the padded image
    padded_img.paste(img, (pad_width, pad_height))

    # Construct the output path for the padded image
    output_image_name = os.path.splitext(os.path.basename(image_path))[0] + '_padded' + os.path.splitext(image_path)[1]
    output_image_path = os.path.join(output_dir, output_image_name)

    # Save the padded image
    padded_img.save(output_image_path)

    # Construct the output path for the corresponding .txt file
    txt_file = os.path.splitext(os.path.basename(image_path))[0] + '.txt'
    source_txt_path = os.path.join(source_dir, txt_file)
    output_txt_name = os.path.splitext(output_image_name)[0] + '.txt'
    output_txt_path = os.path.join(output_dir, output_txt_name)

    # Copy the .txt file to the output directory with the new name and update coordinates
    if os.path.exists(source_txt_path):
        with open(source_txt_path, 'r') as infile, open(output_txt_path, 'w') as outfile:
            for line in infile:
                try:
                    components = line.strip().split(' ')
                    class_index = components[0]
                    x_center = float(components[1])
                    y_center = float(components[2])
                    width = float(components[3])
                    height = float(components[4])

                    # Update coordinates based on the padding and resizing
                    new_x_center = (x_center * current_width + pad_width) / target_size[0]
                    new_y_center = (y_center * current_height + pad_height) / target_size[1]
                    new_width = width * current_width / target_size[0]
                    new_height = height * current_height / target_size[1]

                    outfile.write(f"{class_index} {new_x_center:.6f} {new_y_center:.6f} {new_width:.6f} {new_height:.6f}\n")
                except ValueError:
                    print(f"Warning: Skipping line '{line.strip()}' due to non-numerical values.")

# Iterate over all files in the source directory
for filename in os.listdir(source_dir):
    # Check if the file is an image (e.g., .jpg, .png)
    if filename.endswith(('.jpg', '.png')):
        # Construct the full path to the image
        image_path = os.path.join(source_dir, filename)

        process_image(image_path, output_dir)

print("Images have been padded and copied to the output directory with '_padded' appended to their names.")