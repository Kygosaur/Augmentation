import cv2
import numpy as np
import os
import shutil
import random

def simulate_lighting(image: np.ndarray, mode: str = 'morning') -> np.ndarray:
    """
    Simulates different lighting conditions on an input image.

    Args:
        image (numpy.ndarray): Input image.
        mode (str): Lighting condition to simulate. Options are 'morning', 'evening', or 'night'.

    Returns:
        numpy.ndarray: Image with simulated lighting condition.
    """
    # Convert image to HSV color space
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    if mode == 'morning':
        # Increase brightness and saturation for morning scene
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.2, 0, 255)
        hsv[:, :, 2] = np.clip(hsv[:, :, 2] * 1.1, 0, 255)
    elif mode == 'evening':
        # Decrease brightness and saturation for evening scene
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 0.8, 0, 255)
        hsv[:, :, 2] = np.clip(hsv[:, :, 2] * 0.9, 0, 255)
    elif mode == 'night':
        # Significantly decrease brightness for night scene
        hsv[:, :, 2] = np.clip(hsv[:, :, 2] * 0.5, 0, 255)
    else:
        raise ValueError(f"Invalid mode '{mode}'. Choose 'morning', 'evening', or 'night'.")

    # Convert back to BGR color space
    augmented_image = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    return augmented_image

def process_images_and_texts(input_dir: str, output_dir: str):
    """
    Process images and text files in the input directory.
    Copies all files to the output directory and creates augmented versions of the images
    with different lighting conditions and random horizontal flipping for 1/3 of the augmented images.
    Text files are also copied and renamed accordingly.
    """
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        input_path = os.path.join(input_dir, filename)
        if os.path.isfile(input_path):
            shutil.copy(input_path, output_dir)

        if filename.endswith((".jpg", ".png")):
            image = cv2.imread(input_path)
            if image is None:
                print(f"Failed to read image: {input_path}")
                continue

            for mode in ['morning', 'evening', 'night']:
                augmented_image = simulate_lighting(image, mode)

                # Apply random horizontal flipping to 1/3 of the augmented images
                if random.random() < 1 / 3:
                    augmented_image = cv2.flip(augmented_image, 1)

                new_filename = f"{mode}_{filename}"
                cv2.imwrite(os.path.join(output_dir, new_filename), augmented_image)

                # Copy and rename .txt file
                txt_filename = os.path.splitext(filename)[0] + '.txt'
                txt_path = os.path.join(input_dir, txt_filename)
                if os.path.exists(txt_path):
                    new_txt_filename = f"{mode}_{txt_filename}"
                    shutil.copy(txt_path, os.path.join(output_dir, new_txt_filename))

if __name__ == "__main__":
<<<<<<< HEAD
    input_dir = r'c:\Users\Kygo\Desktop\new'
    output_dir = r'C:\Users\Kygo\Desktop\extra'
=======
    input_dir = r'C:\Users\Kygo\Portfolio\yolov7\train'
    output_dir = r'C:\Users\Kygo\Desktop\train'
>>>>>>> 8126ae5d52b5ca214272d46f2873dd5b981d4dab
    process_images_and_texts(input_dir, output_dir)