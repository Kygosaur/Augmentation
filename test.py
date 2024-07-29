import cv2
import numpy as np

def sharpen_image(image):
    laplacian_kernel = np.array([[0, -1, 0],
                                 [-1, 1, -1],
                                 [0, -1, 0]])
    
    sharpened_image = cv2.filter2D(image, -1, laplacian_kernel)
    
    sharpened_image = np.clip(sharpened_image, 0, 255).astype(np.uint8)
    
    return sharpened_image

def process_single_image(image_path):
    image = cv2.imread(image_path)
    if image is None:
        print(f"Failed to read image: {image_path}")
        return

    sharpened_image = sharpen_image(image)

    cv2.imshow('Original Image', image)
    cv2.imshow('Sharpened Image', sharpened_image)

    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    image_path = r'yolov7/train/5_Standing_10W42  Jacket Pre-Fabrication Area-5 20231030 1136-1138.png' 
    process_single_image(image_path)
