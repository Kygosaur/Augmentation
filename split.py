import os
import shutil
import random

# Define the source directory and the target directories
source_dir = r'c:\Users\Kygo\Desktop\yolov7'
train_dir = os.path.join(source_dir, 'train')
val_dir = os.path.join(source_dir, 'val')
test_dir = os.path.join(source_dir, 'test')

# Create the target directories if they don't exist
os.makedirs(train_dir, exist_ok=True)
os.makedirs(val_dir, exist_ok=True)
os.makedirs(test_dir, exist_ok=True)

# Create subdirectories for images and labels in each target directory
for target_dir in [train_dir, val_dir, test_dir]:
    os.makedirs(os.path.join(target_dir, 'images'), exist_ok=True)
    os.makedirs(os.path.join(target_dir, 'labels'), exist_ok=True)

# Get all image and label files
image_files = [f for f in os.listdir(source_dir) if f.endswith('.jpg')]
label_files = [f for f in os.listdir(source_dir) if f.endswith('.txt')]

# Split the dataset into training, validation, and testing sets
random.shuffle(image_files)
split_index = int(len(image_files) * 0.7)
train_files = image_files[:split_index]
val_files = image_files[split_index:split_index + int(len(image_files) * 0.15)]
test_files = image_files[split_index + int(len(image_files) * 0.15):]

# Move the files to the appropriate directories
for file_list, target_dir in zip([train_files, val_files, test_files], [train_dir, val_dir, test_dir]):
    for file in file_list:
        # Move the image
        shutil.move(os.path.join(source_dir, file), os.path.join(target_dir, 'images', file))
        # Move the corresponding label
        label_file = file.replace('.jpg', '.txt')
        if label_file in label_files:
            shutil.move(os.path.join(source_dir, label_file), os.path.join(target_dir, 'labels', label_file))

print("Dataset has been split and organized.")
