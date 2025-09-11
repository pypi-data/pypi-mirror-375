import sys
import os
import yaml

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(BASE_DIR)

import yaml_oop.core.parser.config_parser as config_parser
import yaml_oop.core.parser.variable_parser as variable_parser
from yaml_oop.core.declarations import DeclarationType


def key_without_declaration(key: str) -> str:
    """Returns the key without any declarations."""
    if key == "" or key is None:
        return ""
    return " ".join([
        item for item in key.split()
        if item not in DeclarationType.BASE_KEY_DECLARATIONS and item not in DeclarationType.SUB_KEY_DECLARATIONS
    ])


def find_key_declarations(key: str) -> set:
    """Returns all declarations within the key."""
    if key == "" or key is None:
        return set()
    else:
        declarations = set()
        for item in key.split(" "):
            if item in DeclarationType.BASE_KEY_DECLARATIONS or item in DeclarationType.SUB_KEY_DECLARATIONS:
                declarations.add(item)
        return declarations


def remove_key_declaration(data: dict, key: str, declaration: str) -> str:
    """Remove a declaration from a specific key of the YAML data inplace.
       Returns the new key without the declaration"""

    new_key = key.replace(declaration + " ", "")
    new_data = data[key]
    data.pop(key, None)
    data[new_key] = new_data
    return new_key


def add_key_declaration(data: dict, key: str, declaration: str): 
    """Adds a declaration to a key in the YAML data."""
    new_key = declaration + " " + key
    new_data = data[key]
    data.pop(key)
    data[new_key] = new_data
    return new_key
