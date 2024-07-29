import os
import cv2
import numpy as np
from scipy.ndimage import gaussian_filter, map_coordinates

def dilate_image(image, kernel_size=5, iterations=1):
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    dilated_image = cv2.dilate(image, kernel, iterations=iterations)
    return dilated_image

def erode_image(image, kernel_size=5, iterations=1):
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    eroded_image = cv2.erode(image, kernel, iterations=iterations)
    return eroded_image

def elastic_transform(image, alpha=120, sigma=12, alpha_affine=120, random_state=None):
    if random_state is None:
        random_state = np.random.RandomState(None)

    shape = image.shape
    shape_size = shape[:2]

    center_square = np.float32(shape_size) // 2
    square_size = min(shape_size) // 3
    pts1 = np.float32([center_square + np.float32([-1, -1]) * square_size,
                       center_square + np.float32([-1, 1]) * square_size,
                       center_square + np.float32([1, -1]) * square_size])
    pts2 = pts1 + random_state.uniform(-alpha_affine, alpha_affine, size=pts1.shape).astype(np.float32)
    M = cv2.getAffineTransform(pts1, pts2)
    image = cv2.warpAffine(image, M, shape_size[::-1], borderMode=cv2.BORDER_REFLECT_101)

    dx = gaussian_filter((random_state.rand(*shape) * 2 - 1), sigma) * alpha
    dy = gaussian_filter((random_state.rand(*shape) * 2 - 1), sigma) * alpha

    if len(shape) == 2:
        x, y = np.meshgrid(np.arange(shape[1]), np.arange(shape[0]))
        indices = np.reshape(y + dy, (-1, 1)), np.reshape(x + dx, (-1, 1))
    else:
        x, y, z = np.meshgrid(np.arange(shape[1]), np.arange(shape[0]), np.arange(shape[2]))
        indices = np.reshape(y + dy, (-1, 1)), np.reshape(x + dx, (-1, 1)), np.reshape(z, (-1, 1))

    distored_image = map_coordinates(image, indices, order=1, mode='reflect').reshape(shape)

    return distored_image

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

            cv2.imwrite(os.path.join(output_dir, "dilated_" + filename), dilated_image)
            cv2.imwrite(os.path.join(output_dir, "eroded_" + filename), eroded_image)
            cv2.imwrite(os.path.join(output_dir, "elastic_" + filename), elastic_image)

if __name__ == "__main__":
    input_dir = r'C:\Users\Kygo\Desktop\test'
    output_dir = r'c:\Users\Kygo\Desktop\new'
    process_images(input_dir, output_dir)
