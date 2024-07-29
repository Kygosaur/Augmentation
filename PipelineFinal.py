import os
import cv2
import numpy as np
from scipy.ndimage import gaussian_filter, map_coordinates

def dilate_image(image, kernel_size=5, iterations=1):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    dilated_image = cv2.dilate(gray_image, kernel, iterations=iterations)
    return cv2.cvtColor(dilated_image, cv2.COLOR_GRAY2BGR)

def erode_image(image, kernel_size=5, iterations=1):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    eroded_image = cv2.erode(gray_image, kernel, iterations=iterations)
    return cv2.cvtColor(eroded_image, cv2.COLOR_GRAY2BGR)

def elastic_transform(image, alpha=120, sigma=12, alpha_affine=120, random_state=None):
    if random_state is None:
        random_state = np.random.RandomState(None)

    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    shape = gray_image.shape
    shape_size = shape[:2]

    center_square = np.float32(shape_size) // 2
    square_size = min(shape_size) // 3
    pts1 = np.float32([center_square + np.float32([-1, -1]) * square_size,
                       center_square + np.float32([-1, 1]) * square_size,
                       center_square + np.float32([1, -1]) * square_size])
    pts2 = pts1 + random_state.uniform(-alpha_affine, alpha_affine, size=pts1.shape).astype(np.float32)
    M = cv2.getAffineTransform(pts1, pts2)
    image = cv2.warpAffine(gray_image, M, shape_size[::-1], borderMode=cv2.BORDER_REFLECT_101)

    dx = gaussian_filter((random_state.rand(*shape) * 2 - 1), sigma) * alpha
    dy = gaussian_filter((random_state.rand(*shape) * 2 - 1), sigma) * alpha

    if len(shape) == 2:
        x, y = np.meshgrid(np.arange(shape[1]), np.arange(shape[0]))
        indices = np.reshape(y + dy, (-1, 1)), np.reshape(x + dx, (-1, 1))
    else:
        x, y, z = np.meshgrid(np.arange(shape[1]), np.arange(shape[0]), np.arange(shape[2]))
        indices = np.reshape(y + dy, (-1, 1)), np.reshape(x + dx, (-1, 1)), np.reshape(z, (-1, 1))

    distored_image = map_coordinates(image, indices, order=1, mode='reflect').reshape(shape)

    return cv2.cvtColor(distored_image, cv2.COLOR_GRAY2BGR)

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

def process_images(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            image_path = os.path.join(input_dir, filename)
            image = cv2.imread(image_path, cv2.IMREAD_COLOR)

            dilated_image = dilate_image(image)
            eroded_image = erode_image(image)
            elastic_image = elastic_transform(image)

            augmented_dilated_image = random_color_augmentation(dilated_image)
            augmented_eroded_image = random_color_augmentation(eroded_image)
            augmented_elastic_image = random_color_augmentation(elastic_image)

            cv2.imwrite(os.path.join(output_dir, "dilated_" + filename), augmented_dilated_image)
            cv2.imwrite(os.path.join(output_dir, "eroded_" + filename), augmented_eroded_image)
            cv2.imwrite(os.path.join(output_dir, "elastic_" + filename), augmented_elastic_image)

if __name__ == "__main__":
    input_dir = r'C:\Users\Kygo\Desktop\test'
    output_dir = r'c:\Users\Kygo\Desktop\new'
    process_images(input_dir, output_dir)