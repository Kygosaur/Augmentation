import numpy as np
import cv2

def random_shear(image, shear_range):
    shear_x = np.random.uniform(-shear_range, shear_range)
    shear_y = np.random.uniform(-shear_range, shear_range)
    (h, w) = image.shape[:2]
    M = np.float32([[1, shear_x, 0], [shear_y, 1, 0]])
    return cv2.warpAffine(image, M, (w, h))

def random_flip(image):
    flip_code = np.random.choice([0, 1, -1])
    return cv2.flip(image, flip_code)

def random_noise(image, mean=0, std=0.1):
    noise_type = np.random.choice(['gaussian', 'salt_and_pepper'])
    
    if noise_type == 'gaussian':
        noise = np.random.normal(mean, std, image.shape)
    elif noise_type == 'salt_and_pepper':
        noise = np.random.choice([0, 55], size=image.shape, p=[0.5, 0.5])
    
    return np.clip(image + noise, 0, 255).astype(np.uint8)

if __name__ == "__main__":
    image_path = r'c:\Users\Kygo\Desktop\test\2024-02-26 17-24-02_frame_978.jpg'
    image = cv2.imread(image_path)
    
    augmented_image = random_shear(image, shear_range=0.2)
    #augmented_image = random_flip(image)
    #augmented_image = random_noise(image, mean=1, std=0.3)
    
    cv2.imshow('Original Image', image)
    cv2.imshow('Augmented Image', augmented_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
