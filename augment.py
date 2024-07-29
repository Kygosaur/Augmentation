import os
from PIL import Image
import cv2
import numpy as np

def display_image(image):
    """
    Display an image using OpenCV.
    """
    cv2.imshow('Image', image)
    cv2.waitKey(0) 
    cv2.destroyAllWindows()

def augment_image(image_path, output_dir):
    """
    Perform image augmentation on a single image.
    """
    try:
        img = Image.open(image_path)
        img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        
        # Flip the image horizontally
        img_flipped = cv2.flip(img_cv, 1)
        img_flipped_path = os.path.join(output_dir, f"flipped_{os.path.basename(image_path)}")
        cv2.imwrite(img_flipped_path, img_flipped)
        display_image(img_flipped)
        
        # Rotate the image at specified angles
        angles = [10, 20, 30]
        for angle in angles:
            (h, w) = img_cv.shape[:2]
            center = (w / 2, h / 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(img_cv, M, (w, h))
            rotated_path = os.path.join(output_dir, f"rotated_{angle}_{os.path.basename(image_path)}")
            cv2.imwrite(rotated_path, rotated)
            display_image(rotated)
        
    except Exception as e:
        print(f"Error augmenting image {image_path}: {e}")

def augment_images_in_dir(input_dir, output_dir):
    """
    Perform image augmentation on all images in a directory.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for filename in os.listdir(input_dir):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            image_path = os.path.join(input_dir, filename)
            augment_image(image_path, output_dir)

def main():
    input_dir = r"c:\Users\Kygo\Desktop\frames\datasets\2024-02-26 17-24-02_frame_408.jpg"
    output_dir = r"c:\Users\Kygo\Desktop\datasets_resized"
    
    # augment_images_in_dir(input_dir, output_dir)
    augment_image(input_dir, output_dir)

if __name__ == "__main__":
    main()
