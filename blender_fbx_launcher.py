import os
import subprocess
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import Manager
import sys

# Directory containing the folders
directory = "C:\\Users\\Drizzle\\Desktop\\PBR Animations\\Models-Anims"

# Blender executable path
blender_path = "C:\\Users\\Drizzle\\Desktop\\PBR Animations\\Blender 2.93\\blender.exe"

# Blender script path
blender_script = "C:\\Users\\Drizzle\\Desktop\\PBR Animations\\toFBX.py"

def get_folder_paths(directory):
    return [os.path.join(directory, folder_name) for folder_name in os.listdir(directory) if os.path.isdir(os.path.join(directory, folder_name))]

def run_blender_instance(folder_path, total_count, completed_count, lock):
    subprocess.run([blender_path, "--background", "--python", blender_script, "--", folder_path])
    with lock:
        completed_count.value += 1
        print_progress(total_count.value, completed_count.value)

def print_progress(total, completed):
    percent_complete = (completed / total) * 100
    print(f"{completed}/{total} | {percent_complete:.2f}% complete")

def main():
    folder_paths = get_folder_paths(directory)
    total_count = len(folder_paths)

    with Manager() as manager:
        completed_count = manager.Value('i', 0)
        total_count_shared = manager.Value('i', total_count)
        lock = manager.Lock()

        with ProcessPoolExecutor() as executor:
            futures = [executor.submit(run_blender_instance, folder_path, total_count_shared, completed_count, lock) for folder_path in folder_paths]
            
            for future in as_completed(futures):
                try:
                    future.result()  # Wait for the result to catch exceptions if any
                except Exception as e:
                    print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
