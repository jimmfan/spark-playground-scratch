import os
import zipfile
import io
from pyspark import SparkContext

def zipdir(path, ziph, base_dir):
    for root, dirs, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, start=base_dir)
            ziph.write(file_path, arcname)

def create_in_memory_zip(project_dir, lib_dirs):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add the entire project directory
        zipdir(project_dir, zipf, project_dir)
        
        # Add the specified libraries
        for lib_dir in lib_dirs:
            zipdir(lib_dir, zipf, os.path.dirname(lib_dir))
    
    buffer.seek(0)
    return buffer

# Path to the project directory containing UDFs
project_dir = './src/project'

# List of library directories to include in the zip
lib_dirs = [
    '.local/python3.6/site-packages/requests',
    '.local/python3.6/site-packages/numpy',
    '.local/python3.6/site-packages/pandas'
]

# Create the in-memory zip file
in_memory_zip = create_in_memory_zip(project_dir, lib_dirs)

# Initialize SparkContext
sc = SparkContext.getOrCreate()

# Add the in-memory zip file to SparkContext
sc.addPyFile(in_memory_zip)

print("Added in-memory zip file to SparkContext")
