from .mdb_ScreenBuffer import ScreenBuffer
from . import mdb_pretty_print as pretty_print 
import time
from . import mdb_loop_progress as loop_progress 

def get_debug_record(lst, is_2D, display, length):
    """
    Validates and filters a list (1D or 2D) while providing a dynamic debug display
    using ScreenBuffer. Primarily used in MaxCleanerDB to visualize and debug
    data structure inconsistencies.

    Parameters:
    ----------
    lst : list
        The list to validate. Can be a 1D list or a 2D list (list of lists).
    
    is_2D : bool
        Indicates whether the expected structure of `lst` is 2D (True) or 1D (False).
        - If True: validates that each element is a list of a specific `length`.
        - If False: validates that each element is **not** a list.
    
    show : bool
        If True, displays messages for invalid records as they are processed.
        These messages are shown in the ScreenBuffer output area.
    
    length : int
        Applicable only when `is_2D` is True.
        Used to validate that each inner list in the 2D structure matches this length.
    
    Returns:
    -------
        list
                A new list (`cleaned`) containing only the valid records that passed structural validation.
    """

    def get_screen (wait, start = True):
        message = '📊 MaxCleanerDB Debug Mode.'
        message = pretty_print.stylize (message, bold=True )
        return ScreenBuffer(
            wait = wait,
            max_wait = 9,
            max_display = 8,
            start = start,
            header = message,
            header_alignment = 10,
            show_header = True,
            silent_display = None,
            only_display = None,
            auto_clean_edges = True,
            auto_clean_silent_only_display = False,
            shift_max_display = True  
        )

    if display is True:
        wait = False
    elif display is False:
        wait = True
    screen = get_screen(wait) #get your screenbuffered screen
    
    if not isinstance(lst, list):
        screen.put("❌ Major Issue | This file is not a list.")
        screen.put("🛠️ Manual Inspection Required.")
        screen.put("To Solve This")
        screen.put("Step 1 - Move file to MaxCleanerDB backup location using the backup def/function [ MaxDBcleaner.backup(filename) ].")
        screen.put("Step 2 - Get the content manually using [ with open( filepath, "r") as f ] to clean/debug it.")
        screen.put("Step 3 - Reset the file validation using [ MaxCleanerDB.w(filename, []) ]")
        screen.put("Step 4 – Now move the manually cleaned file into the orignal file you just reset validation for.")
        return False
    
    def create_trimmable_list(trim_len):
        lst = []
    
        def add_or_get(item=None):
            nonlocal lst
            if item is not None:
                lst.append(str(item))
                if len(lst) > trim_len:
                    lst = lst[-trim_len:]
            return "\n".join(lst)
    
        return add_or_get
        
    add_to_list = create_trimmable_list(3)
    cleaned = []
    for i, item in enumerate(lst):
        total = len(lst)
        valid = len(cleaned)
        invalid = total - valid
        percent_valid = (valid / total * 100) if total > 0 else 0
        percent_invalid = 100 - percent_valid

        if i == 0:
            screen.clear()

        screen.put(f"🧮  Total  : {total}", index = 0)
        screen.put(f"❌ Invalid : {invalid:,} ({round(percent_invalid)}%)", index = 1)
        screen.put(f"✅  Valid  : {valid:,} ({round(percent_valid)}%)", index = 2)
        screen.put ("", index = 3)

        if is_2D:
            if isinstance(item, list):
                if len(item) == length:
                    cleaned.append(item)
                else:
                    add_to_list(f"Row {i} mismatch inner list/2D length: {str(item)}")
            else:
                add_to_list(f"Row {i} mismatch (Not a 2D list): {str(item)}")
        else:
            if not isinstance(item, list):
                cleaned.append(item)
            else:
                add_to_list(f"Row {i} mismatch (Not a 1D List): {str(item)}")

        screen.put(add_to_list(), index = 4 )
        screen.put("", index = 5)
        screen.put(loop_progress.get(i+1, total), index = 6)
        time.sleep(0.3)
        
    return cleaned

def debug_validation(txt_name, is_2D, clean=None, length=None, display=True):
    # Validate txt_name
    if not isinstance(txt_name, str):
        raise TypeError("txt_name must be a string.")

    # Validate is_2D
    if not isinstance(is_2D, bool):
        raise TypeError("is_2D must be a boolean.")

    # Validate display
    if not isinstance(display, bool):
        raise TypeError("display must be a boolean.")

    # Validate clean (optional)
    if clean is not None and not isinstance(clean, bool):
        raise TypeError("clean must be a boolean if provided.")

    # Validate length based on is_2D
    if is_2D:
        if length is None:
            raise ValueError("length must be provided when is_2D is True.")
        if not isinstance(length, int):
            raise TypeError("length must be an integer when is_2D is True.")
        if length <= 0:
            raise ValueError("length must be greater than zero when is_2D is True.")


