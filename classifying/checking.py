import os
from PIL import Image

def check_image_files(directory):
    """
    Checks if each .jpg file in the specified directory can be opened and is not corrupted.
    Also checks for file encoding and format issues.
    Prints messages only if there is a problem.

    Parameters:
    - directory (str): The path to the directory containing the .jpg files.
    """
    # List all files in the directory
    files = os.listdir(directory)
    
    # Filter out .jpg files
    jpg_files = [f for f in files if f.endswith('.jpg')]
    
    for jpg_file in jpg_files:
        file_path = os.path.join(directory, jpg_file)
        
        # Check if the file can be opened
        try:
            img = Image.open(file_path)
            img.verify()  # Verify that the file is not corrupted
        except (IOError, SyntaxError) as e:
            print(f"Error opening {jpg_file}: {e}.")
        
        # Check file encoding (assuming the file name is encoded in UTF-8)
        try:
            jpg_file.encode('utf-8')
        except UnicodeEncodeError:
            print(f"{jpg_file} has an invalid UTF-8 encoding.")
        
        # Check file format (assuming the file is a JPEG)
        if not jpg_file.lower().endswith(('.jpg', '.jpeg')):
            print(f"{jpg_file} is not in a supported format (JPEG).")

if __name__ == "__main__":
    directory = r"c:\Users\Kygo\Desktop\train1"  # Update this to your directory
    check_image_files(directory)
