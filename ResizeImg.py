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
    discarded_annotations = []
    significant_changes = []

    for annotation in annotations:
        class_id, x_center, y_center, width, height = map(float, annotation.split())
        
        # Store original values for comparison
        original_values = (x_center, y_center, width, height)
        
        # Adjust for resizing and padding
        x_center = (x_center * orig_w * resized_w / orig_w + paste_x) / new_w
        y_center = (y_center * orig_h * resized_h / orig_h + paste_y) / new_h
        width = width * resized_w / new_w
        height = height * resized_h / new_h

        # Clip values to ensure they're within 0-1 range
        x_center = max(0, min(1, x_center))
        y_center = max(0, min(1, y_center))
        width = max(0, min(1, width))
        height = max(0, min(1, height))

        # Check if the object is too small (e.g., less than 1 pixel in either dimension)
        if width * new_w >= 1 and height * new_h >= 1:
            adjusted_annotations.append(f"{int(class_id)} {x_center} {y_center} {width} {height}")
            
            # Log significant changes
            if abs(x_center - original_values[0]) > 0.1 or abs(y_center - original_values[1]) > 0.1 or \
               abs(width - original_values[2]) > 0.1 or abs(height - original_values[3]) > 0.1:
                significant_changes.append(f"  Original: {original_values}\n  Adjusted: {(x_center, y_center, width, height)}")
        else:
            discarded_annotations.append(annotation)

    return adjusted_annotations, discarded_annotations, significant_changes

def resize_images(image_dir, resized_dir, size=(640, 640)):
    """
    Resizes images in the given directory to the specified size, maintaining aspect ratio,
    and adjusts corresponding .txt files with YOLO format annotations.
    """
    if not os.path.exists(resized_dir):
        os.makedirs(resized_dir)

    total_original_annotations = 0
    total_adjusted_annotations = 0
    lost_annotations_log = []
    all_discarded_annotations = []
    all_significant_changes = []

    for filename in os.listdir(image_dir):
        if filename.lower().endswith((".png", ".jpg", ".jpeg")):
            img_path = os.path.join(image_dir, filename)
            try:
                img = Image.open(img_path)
            except Exception as e:
                print(f"Error opening image '{filename}': {e}")
                continue

            original_size = img.size

            try:
                resized_img, paste_info = resize_image_with_aspect_ratio(img, size)
                resized_img.save(os.path.join(resized_dir, filename), quality=95)
            except Exception as e:
                print(f"Error resizing image '{filename}': {e}")
                continue

            # Adjust and save corresponding .txt file
            txt_filename = os.path.splitext(filename)[0] + ".txt"
            txt_path = os.path.join(image_dir, txt_filename)
            if os.path.exists(txt_path):
                try:
                    with open(txt_path, 'r') as f:
                        annotations = f.read().strip().split('\n')
                    
                    total_original_annotations += len(annotations)
                    
                    adjusted_annotations, discarded, significant_changes = adjust_annotations(annotations, original_size, size, paste_info)
                    
                    total_adjusted_annotations += len(adjusted_annotations)

                    if len(annotations) != len(adjusted_annotations):
                        lost_annotations_log.append(f"File: {txt_filename}, Original: {len(annotations)}, Adjusted: {len(adjusted_annotations)}")
                    
                    if discarded:
                        all_discarded_annotations.append(f"File: {txt_filename}")
                        all_discarded_annotations.extend([f"  {ann}" for ann in discarded])
                    
                    if significant_changes:
                        all_significant_changes.append(f"File: {txt_filename}")
                        all_significant_changes.extend(significant_changes)
                    
                    with open(os.path.join(resized_dir, txt_filename), 'w') as f:
                        f.write('\n'.join(adjusted_annotations))
                except Exception as e:
                    print(f"Error processing annotations for '{txt_filename}': {e}")

    print(f"\nImages resized successfully to {size} while maintaining aspect ratio and adjusting annotations.")
    print(f"Original annotations: {total_original_annotations}")
    print(f"Adjusted annotations: {total_adjusted_annotations}")
    print(f"Total lost annotations: {total_original_annotations - total_adjusted_annotations}")
    
    if lost_annotations_log:
        print("\nFiles with lost annotations:")
        for log in lost_annotations_log:
            print(log)
    
    if all_discarded_annotations:
        print("\nDiscarded annotations:")
        for log in all_discarded_annotations:
            print(log)
    
    if all_significant_changes:
        print("\nSignificant changes in annotations:")
        for log in all_significant_changes:
            print(log)

if __name__ == "__main__":
    image_dir = r"c:\Users\jack\Desktop\val-b4"
    resized_dir = r"c:\Users\jack\Desktop\val"

    resize_images(image_dir, resized_dir)