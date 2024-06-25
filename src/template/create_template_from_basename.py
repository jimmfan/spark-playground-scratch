import os
import shutil
import yaml

def create_pipeline_folders(source_dir, target_dir):
    # Get all pipeline scripts in the source directory
    pipeline_scripts = [f for f in os.listdir(source_dir) if f.endswith('.py')]

    for script in pipeline_scripts:
        # Extract the pipeline name from the script name
        pipeline_name = os.path.splitext(script)[0]

        # Create the new folder path
        pipeline_folder = os.path.join(target_dir, pipeline_name)
        
        # Create the folder if it doesn't exist
        os.makedirs(pipeline_folder, exist_ok=True)

        # Create an empty __init__.py file
        init_file = os.path.join(pipeline_folder, '__init__.py')
        with open(init_file, 'w') as f:
            pass

        # Create the config.yml file with the pipeline name
        config_file = os.path.join(pipeline_folder, 'config.yml')
        config_data = {'name': pipeline_name}
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False)

        # Copy the script into the new folder and rename it to run_pipeline.py
        original_script_path = os.path.join(source_dir, script)
        new_script_path = os.path.join(pipeline_folder, 'run_pipeline.py')
        shutil.copy(original_script_path, new_script_path)

    print("Pipeline folders created and scripts copied successfully.")

# Specify the source directory and target directory
source_dir = 'src/jobs'  # Adjust this path as needed
target_dir = 'src/pipelines'  # Adjust this path as needed

create_pipeline_folders(source_dir, target_dir)
