import os
import ast
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from . import mdb_validations as validations
from . import mdb_control_file_visibility as control_file_visibility
import shutil
from datetime import datetime
import re

parent_dir = current_dir = os.getcwd() 
backups = 3
package_name = "MaxCleanerDB"  # fixed folder name
CORRUPT_TAG = ['!!<<CORRUPT_DATA_BLOCK::UNRECOVERABLE::ID#e3f7!!>>']

# Prints a centered welcome message if 'MaxCleanerDB' is newly created.
# previously done by create_package_and_get_txt_folder_path def
main_package_path = os.path.join(current_dir, package_name)
if not os.path.exists(main_package_path):
    os.makedirs(main_package_path)

    message = f"⭐ Welcome To {package_name}: Folder created at: {main_package_path}\n"
    print("")
    print(message)
    
    print("📌 Must Read 📌- import MaxCleanerDB as mdb \n")
    
    print("🔍 The visibility of the files in the backend is intentional for easier inspection.")
    print("⚠️ Do NOT manually edit or tamper with them!")
    print("📁 All 3 related files are required to have identical data.")
    print("❌ Any mismatch will cause a read error.\n")
    print("🛟 For Quick guide call MaxCleanerDB.help() or mdb.help() function\n")
        

def create_package_and_get_txt_folder_path(txt_name: str, position: str = "main") -> str:
    """
    Creates one of the folders 'MaxCleanerDB', 'MaxCleanerDB Snapshots', or 'MaxCleanerDB Backups'
    in the current working directory (where the function is called) if it doesn't exist.
    Returns the full absolute path to txt_name inside that folder.
    """
    package_name = "MaxCleanerDB"  # Define the base package name
    current_dir = os.getcwd()      # Use the directory where the function is called

    folder_map = {
        "main": package_name,
        "snapshot": f"{package_name} Snapshots",
        "backup": f"{package_name} Backups"
    }

    if position not in folder_map:
        raise ValueError(f"Invalid position '{position}'. Must be one of: {list(folder_map.keys())}")

    folder_name = folder_map[position]
    package_path = os.path.join(current_dir, folder_name)

    full_txt_path = os.path.join(package_path, txt_name)
    return full_txt_path


def delete_empty_folder(path):
    """
    Deletes a folder and all its contents.

    Args:
        path (str): Path to the folder to delete.

    Returns:
        bool: True if deleted successfully, False otherwise.
    """
    if os.path.isdir(path):
        try:
            # Remove folder and all its contents
            shutil.rmtree(path)
            return True
        except Exception as e:
            print(f"Error deleting folder: {e}")
            return False
    return False

def clean_and_normalize_txt_name(txt_name: str) -> str:
    """
    Validates and normalizes a file name.

    - Removes trailing '.txt' if present.
    - Strips leading/trailing whitespace.
    - Rejects names containing '/', '\\', or '.' (after removing '.txt').

    Args:
        txt_name (str): The file name to clean and validate.

    Returns:
        str: A validated and cleaned file name.

    Raises:
        ValueError: If the file name contains invalid characters.
    """
    txt_name = txt_name.strip()

    # Remove .txt extension if present
    if txt_name.endswith('.txt'):
        txt_name = txt_name[:-4]

    # Blacklist characters that are not allowed (after removing '.txt')
    blacklist = ['\\', '/', '.']
    if any(char in txt_name for char in blacklist):
        raise ValueError("Invalid Txt_Naming Format: txt_name must not contain /, \\, or . (dot) | to hide use the update def.")

    return txt_name


def get_final_txt_path_dest(i, folder_path, txt_name):
    """
    Generates file path for primary and backup files.

    Args:
        i (int): Backup index (0 = main file, 1 = first backup, etc.).
        txt_name (str): Base name of the file.

    Returns:
        str: The full file path with appropriate suffix.
    """

    i +=1

    file_path = (
        f'{txt_name}.txt' if i == 0 else
        f'{txt_name}_{i}.txt'
    )
    return str(os.path.join(folder_path, file_path))

def read_txt(file_path: str) -> list:
    """
    Reads a .txt file and parses its contents into a list.

    For each non-empty line in the file:
        - Attempts to evaluate the line as a Python literal (e.g., list, int, dict).
        - If parsing fails, keeps the line as a raw string.

    This approach allows mixed content in the file, such as both structured data
    and plain text, to be safely processed.

    Args:
        file_path (str): Path to the file to read.

    Returns:
        list | None: A list of parsed lines, or None if the file doesn't exist 
        or contains no non-empty lines.
    """
            
    if not os.path.exists(file_path):
        return None
    
    results = []
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                parsed_line = ast.literal_eval(line)
            except (SyntaxError, ValueError):
                parsed_line = line  # Keep original line if it can't be evaluated
            results.append(parsed_line)

    # corruption test.
    if results:
        if results and isinstance(results[-1], str) and results[-1].startswith('--- [ (c)'):
            return results[:-1]  # Remove the last item
        else:
            return CORRUPT_TAG
    else:
        return None


def normal_write_file(file_path, content , skip_hide = True):
    """
    Writes a string to a file.

    direct except was intentional this file read validataion.
    any form of error go as None and it will be solve during resolve_txt_path_and_validation.
    
    Parameters:
    - file_path (str): Full path to the file.
    - content (str): The string content to write.
    """
    
    content = str(content)
    
    if not content:
        conetnt = 'n'+'n'+ validations.corruption_tag(package_name)
    else:
        content += '\n'+'\n'+validations.corruption_tag(package_name)

    
    control_file_visibility.unhide_folder(file_path)
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(str(content))
    except:
        control_file_visibility.hide_folder(file_path)
        return None
    control_file_visibility.hide_folder(file_path)

def resolve_txt_path_and_validation(txt_name, skip_validation_error = False):
    """
    Prepares and returns the working environment for a given text file name.

    This function is used across read, write, append, and delete operations. It:
        - Validates and normalizes the provided text file name.
        - Ensures the target folder exists (creating it if necessary).
        - Constructs the path to the validation file.
        - Loads the validation data (if it exists).

    Args:
        txt_name (str): The base name of the text file (without invalid characters or '.txt').

    Returns:
        tuple:
            - folder_path (str): Full path to the folder where the text files are stored.
            - read_validation (list | None): Parsed content of the validation file, 
              or None if the file doesn't exist.
            - validation_path (str): Full path to the validation file.

    Raises:
        ValueError: If the text name contains disallowed characters such as '/', '\\', or '.'.
    """
    class ValidationError(Exception):
        """Custom exception for validation errors."""
        pass
    
    txt_name = clean_and_normalize_txt_name(txt_name)
    folder_path = create_package_and_get_txt_folder_path(txt_name)
    os.makedirs(folder_path, exist_ok=True)
    validation_path = os.path.join(folder_path, f'{txt_name}_validation.txt')
    read_validation = read_txt(validation_path)
    validation = read_validation[0]if read_validation else None

    if validation != '1D' and not isinstance(validation, int):
        if skip_validation_error:
            validation = None
        else:
            if os.path.isdir(validation_path):
                raise ValidationError(f"🛑 Validation Error: Corrupted Validation Tag")

    return folder_path, validation_path, validation

def validate_and_register_row_shape(items: list, validation: int | str | None, validation_path: str) -> None:
    """
    Validates that all rows in a list have consistent lengths.

    - If validation is not provided, infers it from the first item.
    - Handles both 1D and 2D data.
    - Writes the inferred length to a validation file if it's the first write.

    Args:
        items (list): A list of elements or sublists to validate.
        validation: Expected length of each row, or None to infer it.
        validation_path (str): Path to write validation data if it's a new file.

    Raises:
        ValueError: If any row length differs from the first row's length.
    """
    first_write = False
    if validation is None:
        if items:
            if not isinstance(items[0], list):
                validation = '1D'
            else:
                validation = len(items[0])
        first_write = True
    
    for i, row in enumerate(items):
        if not isinstance(row, list):
            row_len = '1D'
        else:
            row_len = len(row)

        if row_len != validation:
            raise IndexError(
                f"Inconsistent row lengths Passed in the Parameter list at row {i}:\n"
                f"            Expected {validation} Length but got {row_len} => {row}.\n"
                f"            If using this in a loop, we suggest enclosing your data with [ ] to convert it into a 1D or 2D list."
            )

    if first_write is True:
        # print("⚠️ New File | If this is not a New file, kindly confirm the validation manually.")
        normal_write_file(validation_path, validation)

def write_all_files(write_list, folder_path, txt_name, single_write = False):
    """
    Creates multiple backup files by writing the same content to each.

    Parameters:
        write_list (list): The list of items to write into each backup file. Each item will be converted to a string.
        folder_path (str): The directory where backup files will be stored.
        txt_name (str): The base name of the text file (without index or extension).

    backups(int) - is a global variable
    Each file will be saved using the path generated by `get_final_txt_path_dest(i, folder_path, txt_name)`.
    """
    # Prepare string to write: join list items with newlines

    if write_list == []:
        write_str ='' #for empty which is also to reset validation
    else:
        write_str = '\n'.join(str(x) for x in write_list) + '\n'

    # very vital top to know a folder is tempered or corrupted.
    write_str += '\n'+'\n'+ validations.corruption_tag(package_name)

    if single_write == True:
        final_dest_path = os.path.join(folder_path, txt_name)
        with open(final_dest_path, 'w', encoding='utf-8') as f:
            f.write(write_str)
    else:
        for i in range(backups):
            final_dest_path = get_final_txt_path_dest(i, folder_path, txt_name)
            with open(final_dest_path, 'w', encoding='utf-8') as f:
                f.write(write_str)
            
def read_files_concurrently(file_paths: list[str], max_workers: int = 5) -> list:
    """
    Reads multiple files concurrently using ThreadPoolExecutor.

    Args:
        file_paths (list): List of file paths to read.
        max_workers (int): Maximum number of threads to use.

    Returns:
        list: Contents of the files in the same order as `file_paths`.
    """
    results = [None] * len(file_paths)

    def read_task(index, path):
        return index, read_txt(path)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(read_task, i, path) for i, path in enumerate(file_paths)]

        for future in as_completed(futures):
            index, content = future.result()
            results[index] = content

    return results
 
def most_common_row(list_of_lists):
    """
    Finds the most frequent row based on stringified values.
    Converts each element to string for comparison,
    then evals the most common row twice to restore data types.
    """

    def safe_literal_eval(value):
        """
        Tries to ast.literal_eval a string value.
        Falls back to original if it fails (e.g. 'jef' is not quoted).
        """
        try:
            return ast.literal_eval(value)
        except (ValueError, SyntaxError):
            return value
    #Start✅
    if not list_of_lists:
        return []

    # Step 1: Normalize all rows by converting each element to str
    str_rows = [str([str(item) for item in row]) for row in list_of_lists]

    # Step 2: Count frequency
    count = Counter(str_rows)
    max_freq = max(count.values())
    most_common = [row for row, freq in count.items() if freq == max_freq]

    # Step 3: Raise error if tie
    if len(most_common) > 1:
        parsed_rows = [ast.literal_eval(row) for row in most_common]
        raise ValueError(
            f"Corrupted data: tie in most common rows with frequency {max_freq}: {parsed_rows}"
        )

    # Step 4: Eval once to get list of strings
    first_eval = ast.literal_eval(most_common[0])

    # Step 5: Safely eval each item to restore its type (int, float, etc.)
    second_eval = [safe_literal_eval(item) for item in first_eval]

    return second_eval
    
def majority_vote_file_reader(txt_name: str, folder_path: str) -> list | None:
    """
    Reads multiple backup files concurrently and returns the most commonly occurring file content.
    
    This function uses a majority-vote mechanism to determine the most reliable data from
    a set of backup files. If all backups are missing or if no consensus is found, it returns None or an empty list,
    respectively.

    Parameters:
        folder_path (str): The path to the folder containing the backup files.

    Returns:
        list | None: 
            - A list representing the most common file content if found.
            - `None` if all backups are missing.
            - An empty list if no consensus is reached (e.g., empty or reset files).
    """
    all_file_records = []
    files_to_thread = [get_final_txt_path_dest(i, folder_path, txt_name) for i in range(backups)]

    all_file_records = read_files_concurrently(files_to_thread)

    # Check 1: All files missing
    new_file_checker = sum(1 for item in all_file_records if item is None)
    if new_file_checker == backups:
        return None

    filtered_all_file_records = [row for row in all_file_records if row is not None]
    txt_read = most_common_row(filtered_all_file_records)

    # Check 2: Most common row not found (e.g., empty or reset file)
    if not txt_read:
        return []

    #corruption detection.
    if txt_read == CORRUPT_TAG:
        raise ValueError(f"🛑 File corruption detected. | Confirms filepath mannually {folder_path}.")

    return txt_read

def get_keep_deletion_rules_filter(file, index, cleaned_list, keep):
    """
    cleaned_list or str_del_list
    
    Determines which items to retain or delete based on frequency and 'keep' value.

    Args:
        file (list): The list of records (can be 1D or 2D).
        index (int | None): Index used to extract values for comparison.
        cleaned_list (list): Items being considered for deletion.
        keep (int): Number of allowed duplicates to retain.

    Returns:
        list: List of items that exceed the 'keep' threshold and should be deleted.
    """
    # Get the specific column/index for comparison if index is provided
    if index: # is not None and index >= 0:
        index_only = []
        for x in file:
            #select here mimic sql select
            for i,select_index in enumerate(index):
                if i == 0:
                    select = str(x[select_index])
                else:
                    select += str(x[select_index])
                index_only.append(select)
    
    else:
        index_only = [ str(x) for x in file ]

    # Count frequency of each value
    index_count = []
    for x in index_only:
        if x not in [ x[0] for x in index_count ]:
            if x in cleaned_list:
                index_count.append( [ x , index_only.count(x) ] )

    # Determine how many occurrences to remove
    cleaned_list = []   
    for x in index_count:
        keep_calculator_with_negative = x[1] - keep
        keep_calculator = (
            0 if keep_calculator_with_negative <= 0
            else keep_calculator_with_negative
        )
        cleaned_list  += ([x[0]] * keep_calculator)
    return cleaned_list


def delete_heart(file, cleaned_list, index, adjusted_index, cutoff, keep):
    """
    adjusted_index or is_2D
    cleaned_list or str_del_list
    
    Core delete logic that removes items based on cleaned_list, index, and limits.

    Args:
        file (list): The original list to process.
        cleaned_list (list): The items to delete.
        index (int): Index to use if working with 2D lists.
        adjusted_index (bool): Whether to treat elements as 1D items wrapped in a list.
        cutoff (int | None): Max number of deletions per value.
        keep (int | None): Number of items to retain.

    Returns:
        tuple: A tuple containing:
            - list: Items that remain after deletion.
            - int: Number of deletions performed.
    """

    def del_limit_reset(del_list: list[str], remove_from_del_list: str) -> list[str]:
        """
        Removes one occurrence of a value from a deletion list.
    
        Args:
            del_list (list[str]): List of values marked for deletion.
            remove_from_del_list (str): Value to remove from the list.
    
        Returns:
            list[str]: Updated deletion list.
        """
        del_index = None
        for i, x in enumerate(del_list):
            if remove_from_del_list == x:
                del_index = i
                break   
        del_list.pop(del_index)
        
        return del_list

    delete_counter = 0
    non_del_list = []
    if not cleaned_list :
        non_del_list = file
    else:
        for x in file:
            if adjusted_index == True:
                select = str(x)
            else:
                #the concantuate is like an and function when deleting.
                for i,select_where in enumerate(index):
                    try:
                        if i == 0:
                            select = str(x[select_where])
                        else:
                            select += str(x[select_where])
                    except IndexError:
                        raise IndexError("🚫 Your File List not up to this index/row_length")
            if select in cleaned_list:
                delete_counter += 1
                if cutoff or keep:
                    del_list = del_limit_reset ( cleaned_list , select) # this is for limit when and item is delete it removes from it limit
            else:
                if adjusted_index == True:
                    non_del_list.append(x)
                else:   
                    non_del_list.append(x)
                    
    return non_del_list, delete_counter  
                
def d(
    txt_name: str,
    del_list: list = [],
    index: int = None,
    cutoff: int = None,
    keep: int = None,
    reverse: bool = False,
    size: int = None,
) -> int | list:
    """
    Deletes matching entries from a file based on a delete list.

    Supports deletion using value match, cutoff limits, or keep limits.
    
    It's important to note that the author didn't use Pandas or any other libraries here,
    in order to avoid maintenance issues and dependencies.

    Args:
        txt_name (str): File to delete from.
        del_list (list): Items to delete.
        is_2d (bool): Whether data is 2D.
        index (int | None): Index for comparison in 2D rows.
        cutoff (int | None): Max number of deletions per value.
        keep (int | None): How many entries to retain per value.
        reverse (bool): If True, processes the list in reverse order.
        size (int | None): Trims the list to this length after deletion.

    Returns:
        int: Number of items deleted.

    Raises:
        IndexError: If index is missing for 2D or invalid for 1D.
        TypeError, ValueError: For invalid arguments.
    """
    
    # Continue with rest of the logic
    delete_counter = 0
    del_list= validations.normalize_to_list(del_list)
    index, del_list = validations.validate_delete_parameters_and_return_index(del_list, cutoff, keep, size, index, reverse)
    folder_path, validation_path, validation = resolve_txt_path_and_validation(txt_name)
    file = proposed_uncorrupted_data =  majority_vote_file_reader(txt_name, folder_path)
    if  proposed_uncorrupted_data  is None:
         proposed_uncorrupted_data  = []

    # Concatenate items in sublists, leave strings as-is, convert others to string
    # Concatenate important for mutiple index deletion
    str_del_list = [
        elem if isinstance(elem, str)
        else ''.join(str(i) for i in elem) if hasattr(elem, '__iter__') else str(elem)
        for elem in del_list
    ]
    
    # Deletion rules filter is to get the number of times an item will be delete.
    if cutoff:
        deletion_rules_filter = str_del_list * cutoff
    elif keep:
        deletion_rules_filter = get_keep_deletion_rules_filter(file, index, str_del_list, keep)
    else:
        deletion_rules_filter = str_del_list
    
    no_del_list = True #means no delete list, skip to check len_size
    if del_list:
        no_del_list = False
    
        # Reverse is a ascending and descending function.
        if reverse:
            file.reverse()
            
        # if a 1D list it helps the next step to indentify it is a 1D list. index not required.
        if validation == '1D':
            is_2D = True
            if index != None:
                raise IndexError("Index parameter for a Normal list should be None | index = None.") 
        else:
            is_2D = False
            if index == None:
                raise IndexError("Index parameter is required when processing a 2D list.")
            
        # items not deleted, get mumber of deletions. 
        remainingItems, delete_counter = delete_heart(file, deletion_rules_filter, index, is_2D, cutoff, keep)  
    
        if reverse: #if reversed intially, a reversal is important for output.   
            remainingItems.reverse()   

    if size:
        if not no_del_list:
            remainingItems = remainingItems[-size:] 
        else:
            original_len = len(file)
            if size is not None:
                remainingItems = file[-size:]
            new_len = len(remainingItems)
            delete_counter = original_len - new_len
            
    write_all_files(remainingItems, folder_path, txt_name) #peform write 

    return delete_counter, remainingItems


def copy_folder(old_path, new_path, display, action_type):
    """
    Copies a folder from old_path to new_path.

    Parameters:
    - old_path (str): The path to the existing folder.
    - new_path (str): The path where the new folder should be created.

    Raises:
    - FileNotFoundError: If the old_path does not exist.
    - FileExistsError: If the new_path already exists.
    """
    if not os.path.exists(old_path):
        raise FileNotFoundError(f"Source folder does not exist: {old_path}.")
    
    if os.path.exists(new_path):
        raise FileExistsError(f"Destination folder already exists: {new_path}.")

    shutil.copytree(old_path, new_path)
    if display:
        print(f"General (*) {action_type} Successfully Done ✅.")

def create_named_path(name: str) -> str:
    """
    Generate a unique timestamped filename based on current datetime and given name.

    Parameters:
    -----------
    name : str
        Base name of the file.

    Returns:
    --------
    str
        Timestamped filename ending in `.txt`.
    """
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
    name_with_timestamp = f"{timestamp}_{name}.txt"
    return name_with_timestamp

def select_star_copy_paste_folder(display, action_type):

    #Use it to for backup and snaps to get the full app.
    
    copy_path = package_path = os.path.join(parent_dir, package_name)
    paste_folder = package_path = os.path.join(parent_dir, f"{package_name} All {action_type}")
    if not os.path.exists(paste_folder):
        os.makedirs(paste_folder)

    paste_path = os.path.join(paste_folder, create_named_path(package_name))

    copy_folder(copy_path, paste_path, display, action_type[:-1])


def cope_and_paste_file(txt_name: str, type: str, display: bool = True) -> bool:
    """
    Create a backup or snapshot of a text-based file.

    This function retrieves the data associated with a given file name (`txt_name`) 
    and writes it to a new file inside a designated backup or snapshot folder. 
    The file is timestamped to ensure versioning.

    Parameters:
    -----------
    txt_name : str
        The name of the text file to back up or snapshot.
        
    type : str
        The type of operation to perform. Accepts:
            - "Backup 💾"
            - "Snapshot 📸"
            
    display : bool, optional (default=True)
        If True, display messages indicating success or failure.

    Returns:
    --------
    bool
        True if the operation completes successfully or file is empty,
        False if the named file does not exist in the database.
    """

    folder_path, validation_path, validation = resolve_txt_path_and_validation(txt_name)

    data = majority_vote_file_reader(txt_name, folder_path)

    if data:
        if type == "Backup 💾":
            get_backup_path = create_package_and_get_txt_folder_path(txt_name, position = "backup")
        elif type == "Snapshot 📸":
            get_backup_path = create_package_and_get_txt_folder_path(txt_name, position = "snapshot")
            
        if not os.path.exists(get_backup_path):
            os.makedirs(get_backup_path)

        backup_name = create_named_path(txt_name)
        if not os.path.exists(get_backup_path):
            os.makedirs(get_backup_path)

        write_all_files(data, get_backup_path, backup_name, single_write=True)
        if display:
            print(f"{type} Successfully Done ✅.")
        return True
        
    elif data is None:
        if display:
            print("❌ Invalid Name as File Doesn't Exist Yet.")
        return False

    elif data == []:
        print(f"🚫 Can't {type} An Empty File.")
        return True
