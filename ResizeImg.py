from PIL import Image
import os
import shutil

def resize_image_with_aspect_ratio(image, target_size):
    """Resize image maintaining aspect ratio and filling with black if necessary."""
    aspect_ratio = image.width / image.height
    target_aspect = target_size[0] / target_size[1]

    if aspect_ratio > target_aspect:
        # Image is wider than target
        new_width = target_size[0]
        new_height = int(new_width / aspect_ratio)
    else:
        # Image is taller than target
        new_height = target_size[1]
        new_width = int(new_height * aspect_ratio)

    resized_image = image.resize((new_width, new_height), Image.LANCZOS)

    new_image = Image.new("RGB", target_size, (0, 0, 0))
    paste_x = (target_size[0] - new_width) // 2
    paste_y = (target_size[1] - new_height) // 2
    new_image.paste(resized_image, (paste_x, paste_y))

    return new_image, (paste_x, paste_y, new_width, new_height)

def adjust_annotations(annotations, original_size, new_size, paste_info):
    """Adjust YOLO format annotations after resizing."""
    orig_w, orig_h = original_size
    new_w, new_h = new_size
    paste_x, paste_y, resized_w, resized_h = paste_info

    adjusted_annotations = []
    for annotation in annotations:
        class_id, x_center, y_center, width, height = map(float, annotation.split())
        
        # Adjust for resizing and padding
        x_center = (x_center * orig_w * resized_w / orig_w + paste_x) / new_w
        y_center = (y_center * orig_h * resized_h / orig_h + paste_y) / new_h
        width = width * resized_w / new_w
        height = height * resized_h / new_h

        adjusted_annotations.append(f"{int(class_id)} {x_center} {y_center} {width} {height}")

    return adjusted_annotations

def resize_images(image_dir, resized_dir, size=(640, 640)):
    """
    Resizes images in the given directory to the specified size, maintaining aspect ratio,
    and adjusts corresponding .txt files with YOLO format annotations.
    """
    try:
        if not os.path.exists(resized_dir):
            os.makedirs(resized_dir)

        for filename in os.listdir(image_dir):
            try:
                if filename.lower().endswith((".png", ".jpg", ".jpeg")):
                    img_path = os.path.join(image_dir, filename)
                    img = Image.open(img_path)
                    original_size = img.size

                    resized_img, paste_info = resize_image_with_aspect_ratio(img, size)

                    resized_img.save(os.path.join(resized_dir, filename), quality=95)

                    # Adjust and save corresponding .txt file
                    txt_filename = os.path.splitext(filename)[0] + ".txt"
                    txt_path = os.path.join(image_dir, txt_filename)
                    if os.path.exists(txt_path):
                        with open(txt_path, 'r') as f:
                            annotations = f.read().strip().split('\n')
                        
                        adjusted_annotations = adjust_annotations(annotations, original_size, size, paste_info)
                        
                        with open(os.path.join(resized_dir, txt_filename), 'w') as f:
                            f.write('\n'.join(adjusted_annotations))

            except Exception as e:
                print(f"Error processing image '{filename}': {e}")

        print(f"Images resized successfully to {size} while maintaining aspect ratio and adjusting annotations.")

    except Exception as e:
        print(f"Error during resizing operation: {e}")

if __name__ == "__main__":
    image_dir = r"c:\Users\jack\Desktop\removed"
    resized_dir = r"c:\Users\jack\Desktop\aspect-640"

    resize_images(image_dir, resized_dir)