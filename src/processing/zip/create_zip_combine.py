import os
import zipfile

def zipdir(path, ziph, base_dir):
    # Zip the contents of the directory
    for root, dirs, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, start=base_dir)
            ziph.write(file_path, arcname)

def create_zip(zip_name, udf_files, lib_dirs):
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add the UDF files
        for udf_file in udf_files:
            zipf.write(udf_file, arcname=os.path.basename(udf_file))
        
        # Add the specified libraries
        for lib_dir in lib_dirs:
            zipdir(lib_dir, zipf, os.path.dirname(lib_dir))
    
    print(f"Created {zip_name}")

# List of UDF files to include in the zip
udf_files = ['udfs/my_udf.py']

# List of library directories to include in the zip
lib_dirs = [
    '.local/python3.6/site-packages/requests',
    '.local/python3.6/site-packages/numpy',
    '.local/python3.6/site-packages/pandas'
]

# Name of the output zip file
zip_name = 'my_udf_package.zip'

# Create the zip file
create_zip(zip_name, udf_files, lib_dirs)
