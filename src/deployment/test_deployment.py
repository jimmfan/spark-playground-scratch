import subprocess
import sys
import json
import os
import logging
import time
from pathlib import Path
import shutil

logging.basicConfig(level=logging.INFO)

def create_virtualenv(venv_path):
    subprocess.check_call([sys.executable, "-m", "venv", venv_path])

def install_and_test_module(venv_path, module_name):
    python_executable = venv_path / "bin" / "python"
    try:
        subprocess.check_call([python_executable, "-m", "pip", "install", "--upgrade", "pip"])
        subprocess.check_call([python_executable, "-m", "pip", "install", module_name])
        subprocess.check_call([python_executable, "-c", f"import runpy; runpy.run_module('{module_name}')"])
        logging.info(f"Deployment test for {module_name} passed.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Deployment test for {module_name} failed: {e}")
        raise

def clean_up(venv_path):
    shutil.rmtree(venv_path, ignore_errors=True)    

def test_deployment(module_name, retries=3):
    venv_path = Path(f"venv_{module_name}")
    if not venv_path.exists():
        create_virtualenv(venv_path)
    
    attempt = 0
    try:
        while attempt < retries:
            try:
                install_and_test_module(venv_path, module_name)
                return
            except subprocess.CalledProcessError:
                attempt += 1
                logging.error(f"Retry {attempt}/{retries} for {module_name}")
                time.sleep(5)  # wait before retrying
    finally:
        clean_up(venv_path)
    logging.critical(f"Deployment test for {module_name} failed after {retries} attempts.")


if __name__ == "__main__":
    with open("modules_config.json", "r") as file:
        config = json.load(file)
    
    modules = config.get("modules", [])
    
    for module in modules:
        test_deployment(module)
