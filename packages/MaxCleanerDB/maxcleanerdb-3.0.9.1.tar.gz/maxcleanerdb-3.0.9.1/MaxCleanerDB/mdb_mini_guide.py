def help():
    """
    📝 MDB Helper Documentation
    ===========================

    🚨 IMPORTANT: Validation Behavior
    ---------------------------------
    - On the **first write (`w`) or append (`a`)**, the system automatically stores the data's structure:
        • Whether it's 1D or 2D
        • If 2D, the expected row length

    - This structure becomes a **locked validation schema**. All future data passed to `w()` or `a()` **must match** this structure.

    - If future data mismatches the structure (e.g., wrong row length or type), a **ValueError** will be raised.

    - To **reset the structure and validation**, you must explicitly clear the file first:

        w("students", [])  # Clears the file and resets validation
        w("students", [["New", 1], ["Structure", 2]])  # Applies new structure

    - This behavior ensures consistency across all reads, appends, deletes, and backups.

    ================================================================

    FUNCTIONS
    =========

    1. w(txt_name: str, write_list: list) -> None
       ------------------------------------------
       Overwrites a file with a new list of data. Clears file validation if `write_list` is [].
       
       Example:
           w("students", [["John", 20], ["Anna", 22]])
           w("students", [])  # Clears the file and resets validation

       Parameters:
           txt_name   : str   -> File name (no extension)
           write_list : list  -> List of rows (1D or 2D)

    2. r(txt_name: str, set_new: list | None = [], notify_new: bool = True) -> list | None
       ----------------------------------------------------------------------------------
       Reads a file. If it doesn't exist, returns `set_new`.

       Example:
           data = r("students")             # Reads data
           data = r("students", [], False)  # if notify_new is False, Silent display if new file

       Parameters:
           txt_name   : str       -> File name
           set_new    : list|None -> Used if file is missing
           notify_new : bool      -> Show new file alert

    3. a(txt_name: str, append_list: list) -> list
       ------------------------------------------
       Appends rows to a file and returns the updated data.

       Example:
           a("students", [["Chris", 25]])

       Parameters:
           txt_name     : str   -> File name
           append_list  : list  -> New data to append

    4. d(txt_name: str, del_list: list = [], index: int | list = None, cutoff: int = None, 
         keep: int = None, reverse: bool = False, size: int = None) -> int, list
       ----------------------------------------------------------------------------
       Deletes specific rows from a file using matching rules or trimming logic.
    
       ✅ Deletion Modes:
    
       • Match-based Deletion:
           - For 2D lists:
               • You can specify a single `index` or a list of indexes (e.g., `index=[0, 2]`)
               • Corresponding values in `del_list` will be combined and matched.
           - For 1D lists:
               • `index` must be `None`.
               • Deletion is based on exact value matching.
    
       • Wildcard Deletion:
           - If `del_list = ["*"]`, it deletes **all records** (equivalent to full wipe).
             Example:
                 d("students", del_list=["*"])
    
       • Size-based Trimming:
           - If `size` is set, keeps only the last `size` rows.
    
       Examples:
           d("students", del_list=[["John", 20]], index=0)
           d("students", del_list=[["John", "Math"]], index=[0, 2])  # Multi-index delete
           d("students", del_list=["*"])  # Deletes all rows
           d("students", size=100)  # Keeps last 100 records only
    
       Parameters:
           txt_name  : str        -> File name
           del_list  : list       -> Items to delete (or ["*"] for full wipe)
           index     : int|list   -> Index/Indexes to match against (2D only)
           cutoff    : int        -> Max number of deletions per value
           keep      : int        -> Retain at most X entries per value
           reverse   : bool       -> Delete from end first
           size      : int        -> Trim list to this length after deletion
    
       Returns:
           (int, list) -> Number of items deleted, and the remaining data

    5. backup(txt_name: str, display: bool = True) -> None
       ---------------------------------------------------
       Manually backs up a file or all files (`*`) to "Backup 💾"

       Examples:
           backup("students")
           backup("*")  # All files

       Parameters:
           txt_name : str   -> File name or "*"
           display  : bool  -> Show progress

    6. snapshot(txt_name: str, unit: str, gap: int, begin=0, display=True) -> bool
       --------------------------------------------------------------------------
       A timed backup is a snapshot Creates a time-based snapshot if gap has elapsed.

       Examples:
           snapshot("students", unit="h", gap=6)
           snapshot("*", "day", 1)  # Daily snapshot

       Parameters:
           txt_name : str        -> File name or "*"
           unit     : str        -> Time unit: ['s', 'm', 'h', 'd', 'mo', 'y']
           gap      : int|float  -> Minimum interval to snapshot again
           begin    : int        -> Day start hour (0-23)
           display  : bool       -> Show messages

    7. debug(txt_name: str, is_2D: bool = None, clean: bool = None, 
             length: int = None, display: bool = True) -> None
       -------------------------------------------------------------------
       Scans and optionally fixes structure issues in the file.

       Examples:
           debug("students", is_2D=True)
           debug("students", clean=True)

       Parameters:
           txt_name : str     -> File name
           is_2D    : bool    -> Specify list type
           clean    : bool    -> Rewrite fixed file
           length   : int     -> Expected row length
           display  : bool    -> Show messages


    ----------------------------
    🧠 Notes:
    - All files are handled as `.txt` internally.
    - Data must be consistent (1D or 2D, not mixed).
    - All functions auto-handle backup syncing.
    - Use `normalize_to_list()` for consistency.

    ⚠️ Errors will be raised for:
       - Mismatched data structure
       - Missing or invalid `index`
       - Invalid parameter types
       - Invalid list shape compared to stored validation

    🔚 End of Documentation
    """
    print(help.__doc__)
