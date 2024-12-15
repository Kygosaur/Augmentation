import os
from collections import defaultdict

def count_objects_per_class(annotation_dir):
    """
    Counts the number of objects per class in a dataset with YOLO-style annotations.

    Parameters:
    - annotation_dir (str): Path to the directory containing the annotation files.

    Returns:
    - class_counts (dict): A dictionary mapping class IDs to the number of objects of that class.
    """
    class_counts = defaultdict(int)

    for filename in os.listdir(annotation_dir):
        if filename.endswith(".txt"):
            file_path = os.path.join(annotation_dir, filename)
            try:
                with open(file_path, 'r') as file:
                    for line in file:
                        parts = line.strip().split()
                        if len(parts) ==  5:
                            class_id = int(parts[0])    
                            class_counts[class_id] +=  1
            except Exception as e:
                print("Error for {file_path}:{e}")

    return class_counts

annotation_dir = r"g:\new dataset\640-original"
class_counts = count_objects_per_class(annotation_dir)

print("Number of objects per class:")
for class_id, count in class_counts.items():
    print(f"Class {class_id}: {count} objects")
