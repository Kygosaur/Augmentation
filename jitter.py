import cv2
import numpy as np
import os
import shutil

def random_color_augmentation(image):
    brightness_factor = np.random.uniform(0.5, 1.5)
    image = cv2.convertScaleAbs(image, alpha=brightness_factor)
    
    contrast_factor = np.random.uniform(0.5, 1.5)
    mean = np.mean(image)
    image = cv2.addWeighted(image, contrast_factor, image, 0, -mean * (contrast_factor - 1))
    
    saturation_factor = np.random.uniform(0.5, 1.5)
    image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    image_hsv[:, :, 1] = np.clip(image_hsv[:, :, 1] * saturation_factor, 0, 255)
    image = cv2.cvtColor(image_hsv, cv2.COLOR_HSV2BGR)
    
    hue_shift = np.random.uniform(-0.2, 0.2)
    image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    image_hsv[:, :, 0] = np.clip(image_hsv[:, :, 0] + hue_shift * 180, 0, 179)
    image = cv2.cvtColor(image_hsv, cv2.COLOR_HSV2BGR)
    
    return image

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

            augmented_image = random_color_augmentation(image)
            new_filename = "jitter2_" + filename
            cv2.imwrite(os.path.join(output_dir, new_filename), augmented_image)

            # use here to copy and rename .txt file
            txt_filename = filename.rsplit('.', 1)[0] + '.txt'
            txt_path = os.path.join(input_dir, txt_filename)
            if os.path.exists(txt_path):
                new_txt_filename = "jitter2_" + txt_filename
                shutil.copy(txt_path, os.path.join(output_dir, new_txt_filename))

if __name__ == "__main__":
    input_dir = r'c:\Users\Kygo\Desktop\valcrop'
    output_dir = r'C:\Users\Kygo\Desktop\train'
    input_dir = r'c:\Users\Kygo\Desktop\valCrop'
    output_dir = r'C:\Users\Kygo\Desktop\val'
    process_images_and_texts(input_dir, output_dir)
