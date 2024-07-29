import os

def append_string_to_file_names(directory, string_to_append):
    # Ensure the directory ends with a slash
    if not directory.endswith('/'):
        directory += '/'
    
    # Iterate over all files in the directory
    for filename in os.listdir(directory):
        # Check if the file is a .txt, .jpg, or .png file
        if filename.endswith('.txt') or filename.endswith('.jpg') or filename.endswith('.png'):
            # Construct the new file name by appending the specified string
            new_filename = filename.rsplit('.', 1)[0] + string_to_append + '.' + filename.rsplit('.', 1)[1]
            # Rename the file
            os.rename(directory + filename, directory + new_filename)
            print(f"Renamed '{filename}' to '{new_filename}'.")

# Example usage
directory = r'c:\Users\jack\Desktop\test'
string_to_append = 'why' # Example string to append to file names
append_string_to_file_names(directory, string_to_append)
