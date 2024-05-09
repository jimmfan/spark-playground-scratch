import yaml
from yaml.loader import SafeLoader

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

def check_yaml(filename):
    try:
        with open(filename, 'r') as file:
            yaml.load(file, Loader=UniqueKeyLoader)
        print("No duplicate keys found.")
    except ValueError as e:
        print(e)

# Example usage
check_yaml('yourfile.yaml')
