import os
import subprocess

class VSCodeExtensionManager:
    def __init__(self):
        """
        Initialize the VS Code Extension Manager.
        Determines the VS Code executable path and fetches the list of installed extensions.
        """
        print("Initializing VS Code Extension Manager...")
        self.vscode_path = self._get_vscode_path()
        self.installed_extensions = self._get_installed_extensions()

    def _get_vscode_path(self):
        """
        Determine the path to the VS Code executable.
        Tries several common installation paths. If not found, prompts the user for the path.
        """
        print("Determining VS Code installation path...")
        possible_paths = [
            os.path.join(os.getenv('LOCALAPPDATA'), 'Programs', 'Microsoft VS Code', 'bin', 'code.cmd'),
            os.path.join(os.getenv('LOCALAPPDATA'), 'Programs', 'Microsoft VS Code', 'bin', 'code.exe'),
            os.path.join(os.getenv('ProgramFiles'), 'Microsoft VS Code', 'bin', 'code.cmd'),
            os.path.join(os.getenv('ProgramFiles'), 'Microsoft VS Code', 'bin', 'code.exe'),
            os.path.join(os.getenv('ProgramFiles(x86)'), 'Microsoft VS Code', 'bin', 'code.cmd'),
            os.path.join(os.getenv('ProgramFiles(x86)'), 'Microsoft VS Code', 'bin', 'code.exe'),
            'code'  # For systems where 'code' is in the PATH
        ]
        for path in possible_paths:
            if os.path.exists(path) and os.path.isfile(path):
                print(f"VS Code executable found: {path}")
                return path
        
        # If no path is found, request user input
        print("VS Code executable not found. Please provide the path to the VS Code executable.")
        while True:
            path = input("Enter the full path to the VS Code executable (e.g., C:\\path\\to\\code.exe or /usr/bin/code): ").strip()
            if os.path.exists(path) and os.path.isfile(path):
                print(f"VS Code executable set to: {path}")
                return path
            else:
                print("Invalid path. Please try again.")

    def _get_installed_extensions(self):
        """
        Fetch the list of currently installed VS Code extensions.
        """
        print("Fetching installed VS Code extensions...")
        result = subprocess.run([self.vscode_path, '--list-extensions'], capture_output=True, text=True)
        if result.returncode == 0:
            installed_extensions = result.stdout.splitlines()
            print(f"Installed extensions: {installed_extensions}")
            return installed_extensions
        else:
            print("Failed to get installed extensions")
            print(f"Error message: {result.stderr}")
            return []

    def install_extensions_from_file(self, file_path):
        """
        Install extensions listed in the specified file.
        Reads the file, extracts extension IDs, and installs each extension if it's not already installed.
        """
        print(f"Reading extensions from file: {file_path}")
        try:
            with open(file_path, 'r') as f:
                # Extract only the extension IDs (remove any version numbers)
                extensions = [line.strip().split('@')[0] for line in f if line.strip() and not line.startswith("VS Code Extensions:")]
            print(f"Found {len(extensions)} extensions in the file.")
        except IOError:
            print(f"Error reading file: {file_path}")
            return

        # Batch install extensions
        extensions_to_install = [ext for ext in extensions if ext not in self.installed_extensions]
        if extensions_to_install:
            print("Installing extensions...")
            command = [self.vscode_path, '--install-extension'] + extensions_to_install
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode == 0:
                print("Successfully installed extensions.")
                self.installed_extensions.extend(extensions_to_install)
            else:
                print("Failed to install some extensions.")
                print(f"Error message: {result.stderr}")
        else:
            print("All extensions are already installed.")

        print("\nInstallation completed.")
        print(f"Total installed extensions: {len(self.installed_extensions)}")

def main():
    """
    Main function to start the VS Code Extension Installer.
    Initializes the extension manager, checks for the input file, and installs the extensions.
    """
    print("Starting VS Code Extension Installer...")
    manager = VSCodeExtensionManager()
    input_file = "vscode_extensions.txt"
    
    if not os.path.exists(input_file):
        input_file = input("Enter the full path to the 'vscode_extensions.txt' file: ").strip()
    
    if os.path.exists(input_file):
        print(f"Found input file: {input_file}")
        manager.install_extensions_from_file(input_file)
    else:
        print(f"File not found: {input_file}")

    print("VS Code Extension Installer completed.")
    print("Reloading VS Code to apply changes...")

    # Manually instruct the user to reload VS Code if needed
    print("Please manually reload or restart VS Code to apply changes.")

if __name__ == "__main__":
    main()
