import os
import platform

class VSCodeExtensionLocator:
    """
    A class to locate VS Code extensions on different operating systems.
    """

    def __init__(self):
        """
        Initialize the VSCodeExtensionLocator.
        Sets up the path to the extensions directory.
        """
        self.extensions_dir = self._get_extensions_directory()

    def _get_extensions_directory(self):
        """
        Determine the path to the VS Code extensions directory based on the operating system.
        
        Returns:
            str or None: The path to the extensions directory if it exists, None otherwise.
        """
        if platform.system() == "Windows":
            path = os.path.join(os.getenv('USERPROFILE'), '.vscode', 'extensions')
        elif platform.system() == "Darwin":  # macOS
            path = os.path.expanduser('~/Library/Application Support/Code/User/extensions')
        else:  # Linux and other Unix
            path = os.path.expanduser('~/.vscode/extensions')
        
        return path if os.path.exists(path) else None

    def list_extensions(self):
        """
        List all the extensions installed in the VS Code extensions directory.

        Returns:
            list: A list of extension names (directory names in the extensions folder).
        """
        if not self.extensions_dir:
            print("Could not find VS Code extensions directory.")
            return []

        try:
            return [d for d in os.listdir(self.extensions_dir) 
                    if os.path.isdir(os.path.join(self.extensions_dir, d))]
        except OSError:
            print("Error reading the extensions directory.")
            return []

    def write_to_file(self, output_file):
        """
        Write the list of extensions to a specified output file.

        Args:
            output_file (str): The path to the file where extensions will be written.
        """
        extensions = self.list_extensions()
        
        if not extensions:
            print("No extensions to write.")
            return

        with open(output_file, 'w') as f:
            f.write("VS Code Extensions:\n\n")
            for ext in extensions:
                f.write(f"- {ext}\n")
        
        print(f"Extensions list written to {output_file}")

def main():
    """
    The main function to run the VS Code extension listing process.
    """
    locator = VSCodeExtensionLocator()
    output_file = "vscode_extensions.txt"
    locator.write_to_file(output_file)

if __name__ == "__main__":
    main()