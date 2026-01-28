import yaml
from yaml.loader import SafeLoader
import importlib.resources as pkg_resources

class UniqueKeyLoader(SafeLoader):
    def __init__(self, stream, warnings):
        super().__init__(stream)
        self.warnings = warnings  # Now the loader has its own reference to the warnings list

    def construct_mapping(self, node, deep=False):
        mapping = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            if key in mapping:
                # Append to the warnings list when a duplicate key is found
                self.warnings.append(f"Duplicate key found: {key}")
            else:
                mapping[key] = self.construct_object(value_node, deep=deep)
        return mapping

def check_yaml_from_package(package, resource, warnings):
    try:
        with pkg_resources.open_text(package, resource) as file:
            loader = UniqueKeyLoader(file, warnings)
            yaml.load(file, Loader=lambda stream: loader)
        if not warnings:
            print("No duplicate keys found.")
        else:
            print("Warnings:", warnings)
    except Exception as e:
        print("Failed to read YAML:", e)

# Example usage
warnings = []
check_yaml_from_package('your_package_name', 'yourfile.yaml', warnings)
