import cv2
import numpy as np

def apply_bilateral_filter(image, d=9, sigmaColor=75, sigmaSpace=75):
    """
    Applies a Bilateral Filter to the input image to remove noise.

    Parameters:
    - image: The input image.
    - d: Diameter of each pixel neighborhood that is used during filtering.
    - sigmaColor: Filter sigma in the color space. A larger value means that farther colors within the pixel neighborhood will be mixed together, resulting in larger areas of semi-equal color.
    - sigmaSpace: Filter sigma in the coordinate space. A larger value means that farther pixels will influence each other as long as their colors are close enough.

    Returns:
    - The image with noise removed.
    """
    # Apply the Bilateral Filter
    filtered_image = cv2.bilateralFilter(image, d, sigmaColor, sigmaSpace)
    
    return filtered_image

# Example usage
if __name__ == "__main__":
    # Load an image
    image_path = r'yolov7/train/5_Standing_10W42  Jacket Pre-Fabrication Area-5 20231030 1136-1138.png' # Replace with your image path
    image = cv2.imread(image_path)
    
    if image is None:
        print(f"Failed to read image: {image_path}")
    else:
        # Apply the Bilateral Filter
        filtered_image = apply_bilateral_filter(image, d=9, sigmaColor=75, sigmaSpace=75)
        
        # Display the original and filtered images
        cv2.imshow('Original Image', image)
        cv2.imshow('Filtered Image', filtered_image)
        
        # Wait for a key press and then close the windows
        cv2.waitKey(0)
        cv2.destroyAllWindows()
