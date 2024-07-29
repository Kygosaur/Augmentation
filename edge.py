import cv2
import numpy as np

def random_color_jitter(image, brightness_range=(-0.2, 0.2), contrast_range=(-0.2, 0.2), saturation_range=(-0.2, 0.2), hue_range=(-10, 10)):
    """
    Apply random color jittering to an image.

    Args:
        image (numpy.ndarray): Input image.
        brightness_range (tuple): Range for random brightness adjustment.
        contrast_range (tuple): Range for random contrast adjustment.
        saturation_range (tuple): Range for random saturation adjustment.
        hue_range (tuple): Range for random hue adjustment.

    Returns:
        numpy.ndarray: Color jittered image.
    """
    # Convert image to HSV color space
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Generate random adjustment factors
    brightness_factor = np.random.uniform(brightness_range[0], brightness_range[1])
    contrast_factor = np.random.uniform(contrast_range[0], contrast_range[1])
    saturation_factor = np.random.uniform(saturation_range[0], saturation_range[1])
    hue_shift = np.random.uniform(hue_range[0], hue_range[1])

    # Adjust brightness
    hsv[:, :, 2] = np.clip(hsv[:, :, 2] * (1 + brightness_factor), 0, 255)

    # Adjust contrast
    mean = np.mean(image)
    image = cv2.addWeighted(image, 1 + contrast_factor, image, 0, -mean * contrast_factor)

    # Adjust saturation
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * (1 + saturation_factor), 0, 255)

    # Adjust hue
    hsv[:, :, 0] = np.clip(hsv[:, :, 0] + hue_shift, 0, 179)

    # Convert back to BGR color space
    jittered_image = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    return jittered_image

# Example usage
image_path = r"c:\Users\Kygo\Desktop\frames\datasets\2024-02-26 17-24-02_frame_408.jpg"
image = cv2.imread(image_path)

# Apply random color jittering
jittered_image = random_color_jitter(image)

# Display images
#cv2.imshow('Original Image', image)
cv2.imshow('Color Jittered Image', jittered_image)
cv2.waitKey(0)
cv2.destroyAllWindows()