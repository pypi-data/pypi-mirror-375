import fnmatch
import os
import shutil
import time

from typing import Optional
import os
import uuid

from ivette.types import SystemInfo
import platform


def print_color(text, color_code):
    """
    Function to print colored text using ANSI escape codes
    """
    print(f"\033[{color_code}m{text}\033[0m")


def clean_up(prefix):
    for filename in os.listdir():
        if filename.startswith(prefix):
            os.remove(filename)

    # Check if the "tmp" subdirectory exists and then remove it
    tmp_dir = os.path.join(os.getcwd(), "tmp")
    if os.path.exists(tmp_dir) and os.path.isdir(tmp_dir):
        shutil.rmtree(tmp_dir)

    # Check if the "cosmo.xyz" file exists and then remove it
    cosmo_file = os.path.join(os.getcwd(), "cosmo.xyz")
    if os.path.exists(cosmo_file):
        os.remove(cosmo_file)


def waiting_message(process: str):
    # Create an animated "Waiting" message using Braille characters
    waiting_message = "⣾⣷⣯⣟⡿⢿⣻⣽"  # Customize this as needed

    for braille_char in waiting_message:
        print(f"   Running {process} Job {braille_char}", end="\r", flush=True)
        time.sleep(0.1)


def is_nwchem_installed():
    return shutil.which("nwchem") is not None


def get_total_memory():
    """
    This function returns the total memory on the system in megabytes.

    Returns:
    int: The total memory on the system in megabytes.
    """
    with open('/proc/meminfo', 'r') as mem:
        total_memory = 0
        for i in mem:
            sline = i.split()
            if str(sline[0]) == 'MemTotal:':
                total_memory = int(sline[1])
                break
    return total_memory / 1024  # convert from KiB to MB


def trim_file(filename: str, desired_size: float) -> None:
    """
    Trims a file to a desired size by removing lines from the middle.

    This function calculates the current size of the file and if it's larger than the desired size,
    it calculates the number of lines to keep. It then keeps an equal number of lines from the
    beginning and the end of the file, and removes the rest. A message is inserted in the middle
    of the file indicating that it was trimmed.

    Parameters:
    filename (str): The path to the file to be trimmed.
    desired_size_mb (float): The desired size of the file in megabytes (MB).

    Returns:
    None

    """
    # Calculate the number of lines in the file
    with open(filename, 'r') as file:
        lines = file.readlines()
    total_lines = len(lines)

    # Calculate the current size of the file in MB
    current_size_mb = os.path.getsize(filename) / (1024 * 1024)

    # If the current size is less than or equal to the desired size, do nothing
    if current_size_mb <= desired_size:
        return

    # Calculate the number of lines to keep based on the desired size
    lines_to_keep = int(total_lines * desired_size / current_size_mb)

    # Calculate the number of lines to keep from the beginning and the end
    start_lines = lines_to_keep // 2
    end_lines = lines_to_keep - start_lines

    # Get the lines to keep
    new_lines = lines[
        :start_lines
    ] + [
        '\n\n... this file was trimmed to reduce size\n\n'
    ] + lines[
        -end_lines:
    ]

    # Write the new lines back to the file
    with open(filename, 'w') as file:
        file.writelines(new_lines)


def get_system_info():
    info = SystemInfo(
        system_id=str(uuid.getnode()),
        system=platform.system(),
        node=platform.node(),
        release=platform.release(),
        version=platform.version(),
        machine=platform.machine(),
        processor=platform.processor(),
        # Assign a default value of 0 if get_cpu_core_count() returns None
        ntotal=int(os.cpu_count()) or 0
    )
    return info
