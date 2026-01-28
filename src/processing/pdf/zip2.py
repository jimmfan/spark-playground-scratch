import os
import zipfile

def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            # Create a relative path for files to keep the structure
            rel_dir = os.path.relpath(root, path)
            rel_file = os.path.join(rel_dir, file)
            ziph.write(os.path.join(root, file), rel_file)

if __name__ == '__main__':
    # Path to the cv2 library in your .local directory
    cv2_path = '/path/to/your/.local/lib/python3.6/site-packages/cv2'
    # The destination directory where you want the zip file to be saved
    destination_directory = '/desired/path/to/save/the/zip'
    zip_file_name = 'cv2_package.zip'  # Name of the zip file
    
    # Ensuring the destination directory exists
    if not os.path.exists(destination_directory):
        os.makedirs(destination_directory)

    # Full path for the zip file
    full_zip_path = os.path.join(destination_directory, zip_file_name)

    # Create a zip file
    with zipfile.ZipFile(full_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipdir(cv2_path, zipf)

    print(f"cv2 library zipped successfully at {full_zip_path}")
