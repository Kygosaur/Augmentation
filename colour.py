import cv2
import numpy as np

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

image_path = r'c:\Users\Kygo\Desktop\test\2024-02-26 17-24-02_frame_978.jpg' 
image = cv2.imread(image_path)

augmented_image = random_color_augmentation(image)

cv2.imshow('Original Image', image)
cv2.imshow('Augmented Image', augmented_image)

# Wait for a key press and close the windows
cv2.waitKey(0)
cv2.destroyAllWindows()
