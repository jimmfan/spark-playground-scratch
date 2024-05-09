import yaml
from yaml.loader import SafeLoader
import importlib.resources as pkg_resources  # Use importlib_resources for Python<3.7

class UniqueKeyLoader(SafeLoader):
    def construct_mapping(self, node, deep=False):
        mapping = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            if key in mapping:
                raise ValueError(f"Duplicate key found: {key}")
            else:
                mapping[key] = self.construct_object(value_node, deep=deep)
        return mapping

def check_yaml_from_package(package, resource):
    try:
        with pkg_resources.open_text(package, resource) as file:
            yaml.load(file, Loader=UniqueKeyLoader)
        print("No duplicate keys found.")
    except ValueError as e:
        print(e)
    except Exception as e:
        print("Failed to read YAML:", e)

# Example usage
check_yaml_from_package('your_package_name', 'yourfile.yaml')
