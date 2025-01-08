# Image Augmentation and YOLO Dataset Validation Tools

This repository contains a collection of tools for image augmentation and YOLO dataset annotation validation. These tools help improve model training by enhancing dataset variety and ensuring annotation quality.

## Image Augmentation Tools

The `augmentation` directory contains scripts for various image augmentation techniques to enhance your training dataset.

### Available Augmentations

#### Geometric Transformations
- **Rotation**: Rotates images by random angles
- **Flip**: Horizontal and vertical flipping
- **Scale**: Random scaling of images
- **Translation**: Shifts images in x and y directions
- **Shear**: Applies shear transformation

```python
def rotate_image(image, angle_range=(-30, 30)):
    """
    Rotate image by random angle within range.
    
    Args:
        image: numpy array of image
        angle_range: tuple of (min_angle, max_angle)
    Returns:
        Rotated image and adjusted bounding boxes
    """
    angle = np.random.uniform(*angle_range)
    height, width = image.shape[:2]
    matrix = cv2.getRotationMatrix2D((width/2, height/2), angle, 1.0)
    rotated = cv2.warpAffine(image, matrix, (width, height))
    return rotated, matrix

def flip_image(image, direction='horizontal'):
    """
    Flip image horizontally or vertically.
    
    Args:
        image: numpy array of image
        direction: 'horizontal' or 'vertical'
    Returns:
        Flipped image
    """
    if direction == 'horizontal':
        return cv2.flip(image, 1)
    return cv2.flip(image, 0)
```

#### Color/Intensity Transformations
- **Brightness**: Adjusts image brightness
- **Contrast**: Modifies image contrast
- **Noise**: Adds random noise (Gaussian, Salt & Pepper)
- **Blur**: Applies Gaussian blur
- **Color Jittering**: Randomly changes color properties

```python
def adjust_brightness(image, factor_range=(0.5, 1.5)):
    """
    Adjust image brightness.
    
    Args:
        image: numpy array of image
        factor_range: tuple of (min_factor, max_factor)
    Returns:
        Brightness adjusted image
    """
    factor = np.random.uniform(*factor_range)
    return cv2.convertScaleAbs(image, alpha=factor, beta=0)

def add_noise(image, noise_type='gaussian', amount=0.05):
    """
    Add noise to image.
    
    Args:
        image: numpy array of image
        noise_type: 'gaussian' or 'salt_pepper'
        amount: noise intensity
    Returns:
        Noisy image
    """
    if noise_type == 'gaussian':
        row, col, ch = image.shape
        mean = 0
        sigma = amount * 255
        gauss = np.random.normal(mean, sigma, (row, col, ch))
        noisy = image + gauss
        return np.clip(noisy, 0, 255).astype(np.uint8)
    return image
```

## YOLO Annotation Validation Tools

The `validation` directory contains scripts to verify and validate YOLO format annotations.

### Validation Checks

1. **Format Validation**
   - Checks if annotation files follow YOLO format
   - Validates class IDs are within valid range
   - Ensures coordinates are normalized (0-1)

```python
def validate_yolo_format(annotation_path):
    """
    Validate YOLO annotation format.
    
    Args:
        annotation_path: path to annotation file
    Returns:
        bool: True if valid, False otherwise
        list: Error messages if any
    """
    errors = []
    try:
        with open(annotation_path, 'r') as f:
            lines = f.readlines()
            
        for line_num, line in enumerate(lines, 1):
            parts = line.strip().split()
            if len(parts) != 5:
                errors.append(f"Line {line_num}: Invalid format")
                continue
                
            class_id = int(parts[0])
            x, y, w, h = map(float, parts[1:])
            
            if not (0 <= x <= 1 and 0 <= y <= 1 and 0 <= w <= 1 and 0 <= h <= 1):
                errors.append(f"Line {line_num}: Coordinates must be normalized (0-1)")
                
    except Exception as e:
        errors.append(f"File reading error: {str(e)}")
        
    return len(errors) == 0, errors
```

2. **Consistency Checks**
   - Verifies image-annotation file pairs exist
   - Checks for empty annotation files
   - Validates bounding box dimensions

```python
def check_dataset_consistency(dataset_path):
    """
    Check consistency between images and annotations.
    
    Args:
        dataset_path: path to dataset directory
    Returns:
        dict: Consistency check results
    """
    results = {
        'missing_annotations': [],
        'missing_images': [],
        'empty_annotations': [],
        'invalid_boxes': []
    }
    
    image_files = glob.glob(os.path.join(dataset_path, 'images', '*.*'))
    annotation_files = glob.glob(os.path.join(dataset_path, 'labels', '*.txt'))
    
    # Check for missing files
    for img_path in image_files:
        base_name = os.path.splitext(os.path.basename(img_path))[0]
        ann_path = os.path.join(dataset_path, 'labels', f'{base_name}.txt')
        if not os.path.exists(ann_path):
            results['missing_annotations'].append(base_name)
            
    return results
```

3. **Visualization Tools**
   - Draws bounding boxes on images
   - Highlights potential issues
   - Generates validation reports

```python
def visualize_annotations(image_path, annotation_path, output_path=None):
    """
    Visualize YOLO annotations on image.
    
    Args:
        image_path: path to image file
        annotation_path: path to annotation file
        output_path: path to save visualization
    """
    image = cv2.imread(image_path)
    height, width = image.shape[:2]
    
    with open(annotation_path, 'r') as f:
        for line in f:
            class_id, x, y, w, h = map(float, line.strip().split())
            
            # Convert normalized coordinates to pixel coordinates
            x1 = int((x - w/2) * width)
            y1 = int((y - h/2) * height)
            x2 = int((x + w/2) * width)
            y2 = int((y + h/2) * height)
            
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
    if output_path:
        cv2.imwrite(output_path, image)
    return image
```

## Usage

1. **Image Augmentation**
```python
from augmentation import geometric, color

# Apply multiple augmentations
image = cv2.imread('image.jpg')
augmented = geometric.rotate_image(image, angle_range=(-30, 30))
augmented = color.adjust_brightness(augmented, factor_range=(0.7, 1.3))
```

2. **Annotation Validation**
```python
from validation import checker

# Validate single annotation file
is_valid, errors = checker.validate_yolo_format('annotation.txt')

# Check entire dataset
results = checker.check_dataset_consistency('dataset_path')
```

## Requirements
- Python 3.7+
- OpenCV
- NumPy
- Pillow
