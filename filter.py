import cv2
import numpy as np
import random

def add_gaussian_noise(image, mean=0, std_dev=25):
    noise = np.random.normal(mean, std_dev, image.shape)
    noisy_image = np.clip(image + noise, 0, 255).astype(np.uint8)
    return noisy_image

def add_noise(img): 
    row , col = img.shape 
    number_of_pixels = random.randint(300, 10000) 
    for i in range(number_of_pixels): 
        y_coord = random.randint(0, row - 1) 
        x_coord = random.randint(0, col - 1) 
        img[y_coord][x_coord] = 255 # Salt
    number_of_pixels = random.randint(300 , 10000) 
    for i in range(number_of_pixels): 
        y_coord = random.randint(0, row - 1) 
        x_coord = random.randint(0, col - 1) 
        img[y_coord][x_coord] = 0 # Pepper
    return img 

def add_gaussian_blur(image, ksize=(5, 5), sigmaX=0):
    blurred_image = cv2.GaussianBlur(image, ksize, sigmaX)
    return blurred_image

if __name__ == "__main__":
    image = cv2.imread(r'c:\Users\Kygo\Desktop\test\2024-02-26 17-24-02_frame_978.jpg')
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    gaussian_noisy_image = add_gaussian_noise(gray_image, mean=0, std_dev=25)
    cv2.imshow('Gaussian Noisy Image', gaussian_noisy_image)
    cv2.waitKey(0)

    salt_pepper_noisy_image = add_noise(gray_image)
    cv2.imshow('Salt-and-Pepper Noisy Image', salt_pepper_noisy_image)
    cv2.waitKey(0)

    gaussian_blurred_image = add_gaussian_blur(gray_image, ksize=(15, 15), sigmaX=10)
    cv2.imshow('Gaussian Blurred Image', gaussian_blurred_image)
    cv2.waitKey(0)

    cv2.destroyAllWindows()
