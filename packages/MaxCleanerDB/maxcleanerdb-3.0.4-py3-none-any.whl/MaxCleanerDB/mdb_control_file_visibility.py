import os
import sys
import shutil
import subprocess

def unhide_folder(path):
    if not os.path.exists(path):
        return f"Error: Path '{path}' does not exist."

    if sys.platform.startswith('win'):
        # Windows: remove hidden (and system) attribute
        import ctypes
        FILE_ATTRIBUTE_HIDDEN = 0x02
        FILE_ATTRIBUTE_SYSTEM = 0x04

        attrs = ctypes.windll.kernel32.GetFileAttributesW(path)
        if attrs == -1:
            return f"Error: Could not get attributes for '{path}'."

        new_attrs = attrs & ~(FILE_ATTRIBUTE_HIDDEN | FILE_ATTRIBUTE_SYSTEM)
        result = ctypes.windll.kernel32.SetFileAttributesW(path, new_attrs)
        if result == 0:
            return f"Error: Failed to remove hidden attribute for '{path}'."
        else:
            return f"Success: '{path}' is no longer hidden."

    elif sys.platform == 'darwin':  # macOS
        # First try removing 'hidden' flag if set
        try:
            # Remove the hidden flag (if set)
            subprocess.run(['chflags', 'nohidden', path], check=True)
        except subprocess.CalledProcessError as e:
            return f"Error removing hidden flag: {e}"

        # Also handle dot prefix (rename if needed)
        folder_name = os.path.basename(path)
        dir_name = os.path.dirname(path)

        if folder_name.startswith('.'):
            new_name = folder_name.lstrip('.')
            if not new_name:
                return "Error: Cannot unhide folder named only '.'"
            new_path = os.path.join(dir_name, new_name)

            if os.path.exists(new_path):
                return f"Error: Target folder '{new_path}' already exists."

            shutil.move(path, new_path)
            return f"Success: Removed hidden flag and renamed '{path}' to '{new_path}'."
        else:
            return f"Success: Removed hidden flag from '{path}'."

    else:
        # Other Unix-like systems: just rename if starts with dot
        folder_name = os.path.basename(path)
        dir_name = os.path.dirname(path)

        if folder_name.startswith('.'):
            new_name = folder_name.lstrip('.')
            if not new_name:
                return "Error: Cannot unhide folder named only '.'"
            new_path = os.path.join(dir_name, new_name)

            if os.path.exists(new_path):
                return f"Error: Target folder '{new_path}' already exists."

            shutil.move(path, new_path)
            return f"Success: Renamed '{path}' to '{new_path}' to unhide."
        else:
            return f"'{path}' is not hidden (no leading dot)."


def hide_folder(path):
    if not os.path.exists(path):
        return f"Error: Path '{path}' does not exist."

    if sys.platform.startswith('win'):
        # Windows: set hidden attribute
        import ctypes
        FILE_ATTRIBUTE_HIDDEN = 0x02

        attrs = ctypes.windll.kernel32.GetFileAttributesW(path)
        if attrs == -1:
            return f"Error: Could not get attributes for '{path}'."

        new_attrs = attrs | FILE_ATTRIBUTE_HIDDEN
        result = ctypes.windll.kernel32.SetFileAttributesW(path, new_attrs)
        if result == 0:
            return f"Error: Failed to set hidden attribute for '{path}'."
        else:
            return f"Success: '{path}' is now hidden."

    elif sys.platform == 'darwin':
        # macOS: set hidden flag using chflags
        try:
            subprocess.run(['chflags', 'hidden', path], check=True)
            return f"Success: '{path}' is now hidden."
        except subprocess.CalledProcessError as e:
            return f"Error setting hidden flag: {e}"

    else:
        # Unix-like: rename folder to add '.' prefix if not already hidden
        folder_name = os.path.basename(path)
        dir_name = os.path.dirname(path)

        if not folder_name.startswith('.'):
            new_name = '.' + folder_name
            new_path = os.path.join(dir_name, new_name)

            if os.path.exists(new_path):
                return f"Error: Target folder '{new_path}' already exists."

            os.rename(path, new_path)
            return f"Success: Renamed '{path}' to '{new_path}' to hide."
        else:
            return f"'{path}' is already hidden."