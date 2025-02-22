def append_prefix_to_keys(d, prefix):
    """
    Appends a prefix to all keys in a nested dictionary.

    Parameters:
    - d (dict): The input dictionary, possibly nested.
    - prefix (str): The prefix to append to each key.

    Returns:
    - dict: A new dictionary with prefixes appended to all keys.
    """
    if isinstance(d, dict):
        return {
            (prefix + key if isinstance(key, str) else key): append_prefix_to_keys(value, prefix)
            for key, value in d.items()
        }
    elif isinstance(d, list):
        return [append_prefix_to_keys(item, prefix) for item in d]
    else:
        return d

# Example usage:
if __name__ == "__main__":
    original_dict = {
        "name": "Alice",
        "details": {
            "age": 30,
            "address": {
                "city": "New York",
                "zip": "10001"
            }
        },
        "hobbies": ["reading", "traveling"]
    }

    prefix = "user_"
    new_dict = append_prefix_to_keys(original_dict, prefix)

    print("Original Dictionary:")
    print(original_dict)
    print("\nModified Dictionary with Prefix:")
    print(new_dict)
