import os
import zipfile

def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file),
                       os.path.relpath(os.path.join(root, file),
                                       os.path.join(path, '..')))

if __name__ == '__main__':
    # Path to the directory you want to zip
    directory_path = 'your_directory_path'
    # The name of the zip file you create
    zip_file_name = 'your_archive_name.zip'
    
    zipf = zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED)
    zipdir(directory_path, zipf)
    zipf.close()
