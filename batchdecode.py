import os
import subprocess
import concurrent.futures
from threading import Lock

lock = Lock()

def process_file(pbr_tool_path, file_path, total_files):
    try:
        # Open the process
        process = subprocess.Popen([pbr_tool_path, file_path], stdin=subprocess.PIPE, text=True)

        # Send "0\n\n" (0, enter key, enter key) to the process
        process.communicate(input="0\n\n")

        # Check if the process finished successfully
        if process.returncode == 0:
            with lock:
                process_file.processed_count += 1
                processed_count = process_file.processed_count
                percentage = (processed_count / total_files) * 100
                # Clear the screen
                os.system('cls')
                print(f"Decrypted {processed_count}/{total_files} [{percentage:.2f}%]")
        else:
            print(f"Error processing {file_path}: Return code {process.returncode}")

    except subprocess.CalledProcessError as e:
        print(f"Error processing {file_path}: {e}")

def run_pbr_tool():
    base_dir = r'C:\Users\Drizzle\Desktop\PBR Animations'
    models_anims_dir = os.path.join(base_dir, 'Models-Anims')
    pbr_tool_path = os.path.join(base_dir, 'PBR Tool', 'PBR-Tool.exe')

    # Check if the Models-Anims directory exists
    if not os.path.isdir(models_anims_dir):
        print(f"Directory not found: {models_anims_dir}")
        return

    # Check if the PBR-Tool executable exists
    if not os.path.isfile(pbr_tool_path):
        print(f"Executable not found: {pbr_tool_path}")
        return

    # Get the total number of .fsys files
    fsys_files = [f for f in os.listdir(models_anims_dir) if f.endswith('.fsys')]
    total_files = len(fsys_files)
    if total_files == 0:
        print("No .fsys files found to process.")
        return

    # Initialize the processed count
    process_file.processed_count = 0

    # Use ThreadPoolExecutor to process files concurrently with a max of 10 workers
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_file, pbr_tool_path, os.path.join(models_anims_dir, f), total_files) for f in fsys_files]

        # Wait for all futures to complete
        concurrent.futures.wait(futures)

if __name__ == "__main__":
    run_pbr_tool()
