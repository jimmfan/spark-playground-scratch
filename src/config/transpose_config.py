import yaml

# Read the original servers-focused configuration
with open('servers_config.yml', 'r') as file:
    servers_config = yaml.safe_load(file)

# Transform servers-focused configuration to environments-focused configuration
environments_config = {'environments': {}}

for server_name, environments in servers_config['servers'].items():
    for env_name, details in environments.items():
        if env_name not in environments_config['environments']:
            environments_config['environments'][env_name] = {'servers': {}}
        
        environments_config['environments'][env_name]['servers'][server_name] = details

# Write the transformed environments-focused configuration
with open('environments_config.yml', 'w') as file:
    yaml.dump(environments_config, file, default_flow_style=False)

print("Transformation complete. The new configuration is saved in 'environments_config.yml'.")
