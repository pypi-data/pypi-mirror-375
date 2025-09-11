from . import mdb_core as MDB
from . import mdb_session_id_generator as session_id_generator
from datetime import datetime, timezone
import time
import random
import uuid
import os
from . import mdb_control_file_visibility as control_file_visibility

    

def jittery_delay(jitter_range_secs=(0, 0.9)):
    """
    Generate a random jitter delay in seconds within a specified range,
    plus a small unique component to ensure uniqueness across calls.

    This function is useful for adding random timing variation (jitter) 
    to prevent synchronized operations, reduce contention, or avoid 
    predictable timing patterns.

    Parameters:
        jitter_range_secs (tuple): A tuple of two floats (min, max) representing 
                                   the range of jitter delay in seconds. Default is (0.1, 0.3).

    Example:
        delay = generate_jitter_only((0.05, 0.1))
        time.sleep(delay)  # sleep for a random delay between 0.05 and 0.1 seconds plus a unique offset
    """
    min_jitter_ns = int(jitter_range_secs[0] * 1e9)  # convert seconds to nanoseconds
    max_jitter_ns = int(jitter_range_secs[1] * 1e9)
    jitter_ns = random.randint(min_jitter_ns, max_jitter_ns)  # random jitter in nanoseconds

    # Add a small unique component derived from a UUID to ensure uniqueness
    unique_component_ns = (uuid.uuid4().int >> 64) % 1000  # nanoseconds

    total_jitter_ns = jitter_ns + unique_component_ns

    total_jitter_ns = total_jitter_ns / 1e9

    time.sleep(total_jitter_ns)

def format_read_duration(seconds):
    if seconds < 60:
        return "60s"
    else:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        if remaining_seconds == 0:
            return f"{minutes}m"
        else:
            return f"{minutes}m {remaining_seconds}s"


def get_current_utc_timestamp():
    """
    Returns the current UTC time as a formatted string.
    Format: YYYY-MM-DD HH:MM:SS
    """
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def read_worker(txt_name):
    """
    Reads and returns the uncorrupted data from a given txt file using MDB logic.
    
    Parameters:
    - txt_name (str): The name of the file to read.

    Returns:
    - folder_path (str): Path to the file's folder.
    - proposed_uncorrupted_data (Any): Cleaned and verified data from the file.
    """
    folder_path, validation_path, validation = MDB.resolve_txt_path_and_validation(txt_name)
    proposed_uncorrupted_data = MDB.majority_vote_file_reader(txt_name, folder_path)
    return folder_path, proposed_uncorrupted_data


def ready_to_go_check(session_id, folder_path, queue_name, queue_id, read_duration, counter, debug=True):
    """
    Determines whether it's safe to proceed with a write operation,
    based on timing logic and multi-console context.

    Parameters:
    - session_id (str): Unique ID of the current session.
    - folder_path (str): Path to where queue files are stored.
    - queue_name (str): The name of the queue (e.g. the txt file name).
    - queue_id (str): The metadata file used to store last session timestamp.
    - read_duration (float): Time taken to read the file (used to space out writes).
    - wait (bool): Whether to enforce waiting logic (True for multi-console setups).
    - debug (bool): If True, prints debug messages.

    Returns:
    - bool: True if it's safe to proceed with a write, False otherwise.
    """
    #print(f"Counter: {counter}")
    
    last_write = MDB.majority_vote_file_reader(queue_name, folder_path)
    if last_write is None: #newfile
        signal_green = 4
    else:
        jittery_delay() #cause unpredicatable delay
        
        last_session_data = MDB.majority_vote_file_reader(queue_id, folder_path)
        if last_session_data is None:
            signal_green = 0
        else:
            last_event_tag = last_session_data[2]
            if last_event_tag == "Done":
                if counter <= 0:
                    signal_green = 4
                    for _ in range(9):
                        if MDB.majority_vote_file_reader(queue_id, folder_path)[2] == "Active":
                            signal_green = 1
                            break
            else: 
                last_session_time_str = last_session_data[1]
                last_session_time = datetime.strptime(last_session_time_str, "%Y-%m-%d %H:%M:%S.%f").replace(tzinfo=timezone.utc)
                now_utc = datetime.now(timezone.utc)
                diff_seconds = (now_utc - last_session_time).total_seconds()

                if diff_seconds > (read_duration * 22) and counter == 0:
                    signal_green = 4

                elif (read_duration/diff_seconds) * 100  <= 9:
                    signal_green = 2
                    
                elif diff_seconds > (read_duration * 9):
                    signal_green = 1
                else:
                    signal_green = 0

    return signal_green

def wait_queue_event_stamp(folder_path, queue_id, event_tag, session_id = None):
    
    for i in range(3):
        path = MDB.get_final_txt_path_dest(i, folder_path, queue_id)
        control_file_visibility.unhide_folder(path)

    try:
        if session_id:
            now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")
        else:
            last_write = MDB.majority_vote_file_reader(queue_id, folder_path)
            last_write[2] = event_tag
            now_utc = last_write[1]
            session_id = last_write[0]
            
        last_user_timestamp = [session_id, now_utc, event_tag]               
        MDB.write_all_files(last_user_timestamp, folder_path, queue_id)
    except TypeError:
        session_id = 'new'
        now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")
        last_user_timestamp = [session_id, now_utc, "Done"]
        MDB.write_all_files(last_user_timestamp, folder_path, queue_id)

    for i in range(3):
        path = MDB.get_final_txt_path_dest(i, folder_path, queue_id)
        control_file_visibility.hide_folder(path)

        
def wait_read(queue_name, wait=False, debug=False):
    """
    Core method that coordinates safe reading and writing in a queue-based system.

    It ensures that:
    - File reads are not duplicated unnecessarily.
    - Writes are protected by a soft timing lock.
    - Only proceeds to write if 3 consecutive "green" checks pass.

    Parameters:
    - queue_name (str): Name of the queue (file to read/write).
    - worker_func (function): Function that performs the actual file read.
    - *args: Positional arguments passed to worker_func.
    - wait (bool): Set True if using multiple consoles (forces wait between sessions).
    - debug (bool): If True, prints debug messages.
    - **kwargs: Keyword arguments passed to worker_func.

    Returns:
    - proposed_uncorrupted_data (Any): The data read by the worker_func.
    """
    queue_name = queue_name.strip()
    session_id = session_id_generator.get()

    queue_id = f"{queue_name}_queue"
    queue_file_len = f"{queue_name}_queue_len"  # Optional usage not shown

    green_check = 0
    counter =  0
    aprrove_print = False

    while True:
        start_time = time.time()
        folder_path, proposed_uncorrupted_data = read_worker(queue_name)
        end_time = time.time()

        read_duration = (end_time - start_time)
        if debug:
            #print(f"📊 Execution time (scaled): {read_duration:.2f} seconds")
            pass

        check_event = ready_to_go_check(session_id, folder_path, queue_name, queue_id, read_duration, counter, debug=debug)
        
        if check_event == 4:
            green_check = 4
        elif check_event == 2:
            if counter <= 0:
                green_check += 2
            else:
                green_check  += 1 
                if aprrove_print is False and counter <= 0:
                    aprrove_print = True
                    print(f"❌ File {queue_name.title()} Read access denied.")
                    print(f"⚠️ multiple consoles detected.")

        elif check_event == 1:
            green_check  += 1 
            if counter == 0:
                aprrove_print = True
                print(f"❌ File {queue_name.title()} Read access denied.")
                print(f"⚠️ multiple consoles detected.")
                
        else:
            green_check = 0
            if counter == 0:
                aprrove_print = True
                print(f"❌ File {queue_name.title()} Read access denied.")
                print(f"⚠️ multiple consoles detected.")
                
        if green_check >= 3:
            wait_queue_event_stamp(folder_path, queue_id, "Active", session_id = session_id)
            if debug:
                if aprrove_print is True:
                    print('')
                    print(f"✅ Read Access granted.")
            return proposed_uncorrupted_data


        counter += 1