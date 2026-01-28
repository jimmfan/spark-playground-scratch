import os
import zipfile
import io
from sys import version_info
from pyspark import SparkContext

def zipdir(path, ziph, base_dir):
    for root, dirs, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, start=base_dir)
            ziph.write(file_path, arcname)


def distribute_to_spark(
    spark, 
    local_packages, 
    src_package_path=None, 
    tmp_package_path='/tmp/temp_udf_package.zip'
):
    py_version = f"{version_info.major}.{version_info.minor}"

    src_package_path = (
        src_package_path if src_package_path else f"./.local/lib/python{py_version}/site-packages/"
    )

    with zipfile.ZipFile(tmp_package_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for lib in local_packages:
            lib_dir = f"{src_package_path}/{lib}"
            zipdir(lib_dir, zipf, os.path.dirname(lib_dir))

    spark.sparkContext.addPyFiel(tmp_package_path)
    print(f"Added {local_packages} to SparkContext")
