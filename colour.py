import os
import numpy as np
from PIL import Image
import cv2
import random

# Define the source and output directories
source_dir = r'c:\Users\Jack\Desktop\new'
output_dir = r'c:\Users\Jack\Desktop\augmented'

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

def replace_color(image, lower_bound, upper_bound, new_color):
    """Replace a color range in the image with a new color."""
    # Convert PIL Image to numpy array
    np_image = np.array(image)
    
    # Convert to HSV color space
    hsv = cv2.cvtColor(np_image, cv2.COLOR_RGB2HSV)
    
    # Create a mask for the specified color range
    mask = cv2.inRange(hsv, lower_bound, upper_bound)
    
    # Change the color where the mask is true
    np_image[mask > 0] = new_color
    
    # Convert back to PIL Image
    return Image.fromarray(np_image)

def augment_image(image):
    """Apply random color augmentation to the image."""
    # Convert image to RGB if it's not
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Randomly decide whether to replace yellow with blue (50% chance)
    if random.random() < 0.5:
        # Define yellow color range in HSV
        lower_yellow = np.array([20, 100, 100])
        upper_yellow = np.array([30, 255, 255])
        
        # Define new color (blue in this case)
        new_color = [random.randint(0, 50), random.randint(0, 50), random.randint(200, 255)]  # Blue
        
        # Replace yellow with blue
        image = replace_color(image, lower_yellow, upper_yellow, new_color)
    
    # Apply other color augmentations
    # Convert to numpy array for easier manipulation
    np_image = np.array(image)
    
    # Adjust brightness
    np_image = np_image * random.uniform(0.8, 1.2)
    np_image = np.clip(np_image, 0, 255).astype(np.uint8)
    
    # Adjust contrast
    mean = np.mean(np_image, axis=(0, 1), keepdims=True)
    np_image = (np_image - mean) * random.uniform(0.8, 1.2) + mean
    np_image = np.clip(np_image, 0, 255).astype(np.uint8)
    
    # Adjust saturation
    hsv = cv2.cvtColor(np_image, cv2.COLOR_RGB2HSV)
    hsv[:,:,1] = hsv[:,:,1] * random.uniform(0.8, 1.2)
    np_image = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
    
    # Adjust hue
    hsv = cv2.cvtColor(np_image, cv2.COLOR_RGB2HSV)
    hsv[:,:,0] = (hsv[:,:,0] + random.randint(-10, 10)) % 180
    np_image = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
    
    return Image.fromarray(np_image)

def process_image_and_label(image_path, label_path, output_dir):
    """Augment an image and copy its corresponding label file."""
    # Load and augment the image
    img = Image.open(image_path)
    augmented_img = augment_image(img)
    
    # Construct the output path for the augmented image
    base_name, ext = os.path.splitext(os.path.basename(image_path))
    output_image_name = f"{base_name}_aug{ext}"
    output_image_path = os.path.join(output_dir, output_image_name)
    
    # Save the augmented image
    augmented_img.save(output_image_path)

    # Construct the output path for the label file
    output_label_name = f"{os.path.splitext(os.path.basename(label_path))[0]}_aug.txt"
    output_label_path = os.path.join(output_dir, output_label_name)

    # Copy the label file without changes
    with open(label_path, 'r') as infile, open(output_label_path, 'w') as outfile:
        outfile.write(infile.read())

# Iterate over all files in the source directory
for filename in os.listdir(source_dir):
    # Check if the file is an image (e.g., .jpg, .png)
    if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff')):
        # Construct the full path to the image and its corresponding label file
        image_path = os.path.join(source_dir, filename)
        label_path = os.path.join(source_dir, os.path.splitext(filename)[0] + '.txt')

        # Check if the label file exists
        if os.path.exists(label_path):
            process_image_and_label(image_path, label_path, output_dir)

print("Augmented images and copied labels have been saved in the output directory.")