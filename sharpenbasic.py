import cv2
import numpy as np
import os
import shutil

def sharpen_image(image):
    # Define the Laplacian kernel
    laplacian_kernel = np.array([[0, -1, 0],
                                 [-1, 5, -1],
                                 [0, -1, 0]])
    
    # Apply the Laplacian kernel to the image
    sharpened_image = cv2.filter2D(image, -1, laplacian_kernel)
    
    # Clip the values to the range [0, 255]
    sharpened_image = np.clip(sharpened_image, 0, 255).astype(np.uint8)
    
    return sharpened_image

def copy_all_files(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        file_path = os.path.join(input_dir, filename)
        if os.path.isfile(file_path):
            shutil.copy(file_path, output_dir)

def process_images_and_texts(input_dir, output_dir):
    copy_all_files(input_dir, output_dir)

    for filename in os.listdir(input_dir):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            image_path = os.path.join(input_dir, filename)
            image = cv2.imread(image_path)
            if image is None:
                print(f"Failed to read image: {image_path}")
                continue

            sharpened_image = sharpen_image(image)
            new_filename = "sharpen_" + filename
            cv2.imwrite(os.path.join(output_dir, new_filename), sharpened_image)

            # use here to copy and rename .txt file
            txt_filename = filename.rsplit('.', 1)[0] + '.txt'
            txt_path = os.path.join(input_dir, txt_filename)
            if os.path.exists(txt_path):
                new_txt_filename = "sharpen_" + txt_filename
                shutil.copy(txt_path, os.path.join(output_dir, new_txt_filename))

if __name__ == "__main__":
    input_dir = r'c:\Users\Kygo\Desktop\trainCrop'
    output_dir = r'C:\Users\Kygo\Desktop\train'
    process_images_and_texts(input_dir, output_dir)
