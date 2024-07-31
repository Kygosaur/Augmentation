from PIL import Image
import os
import shutil

def resize_images(image_dir, resized_dir, size=(640, 640)):
    """
    Resizes images in the given directory to the specified size and copies corresponding .txt files.

    Parameters:
    - image_dir (str): Path to the directory containing the images.
    - resized_dir (str): Path to the directory where resized images will be saved.
    - size (tuple): The target size for the images as (width, height).
    """
    try:
        if not os.path.exists(resized_dir):
            os.makedirs(resized_dir)

        for filename in os.listdir(image_dir):
            try:
                if filename.endswith(".png") or filename.endswith(".jpg"):
                    img_path = os.path.join(image_dir, filename)
                    img = Image.open(img_path)

                    resized_img = img.resize(size, Image.LANCZOS)

                    resized_img.save(os.path.join(resized_dir, filename))

                    # Copy corresponding .txt file to the resized directory
                    txt_filename = os.path.splitext(filename)[0] + ".txt"
                    txt_path = os.path.join(image_dir, txt_filename)
                    if os.path.exists(txt_path):
                        shutil.copy(txt_path, os.path.join(resized_dir, txt_filename))

            except Exception as e:
                print(f"Error processing image '{filename}': {e}")

        print(f"Images resized successfully to {size}.")

    except Exception as e:
        print(f"Error during resizing operation: {e}")


if __name__ == "__main__":
    image_dir = r"c:\Users\jack\Desktop\removed"
    resized_dir = r"c:\Users\jack\Desktop\resized"

    resize_images(image_dir, resized_dir)