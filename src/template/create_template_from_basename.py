import os
import yaml

def create_pipeline_folders(jobs_folder, output_folder):
    # Get all pipeline scripts in the jobs folder
    pipeline_scripts = [f for f in os.listdir(jobs_folder) if f.endswith('.py')]

    for script in pipeline_scripts:
        # Extract the pipeline name from the script name
        pipeline_name = os.path.splitext(script)[0]

        # Create the new folder path
        pipeline_folder = os.path.join(output_folder, pipeline_name)
        
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

        # Move the script into the new folder
        os.rename(os.path.join(jobs_folder, script), os.path.join(pipeline_folder, script))

    print("Pipeline folders created successfully.")

# Specify the jobs folder and output folder
jobs_folder = 'src/jobs'  # Adjust this path as needed
output_folder = 'src/pipelines'  # Adjust this path as needed

create_pipeline_folders(jobs_folder, output_folder)
