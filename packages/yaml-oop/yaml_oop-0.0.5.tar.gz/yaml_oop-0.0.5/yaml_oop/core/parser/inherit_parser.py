import sys
import os
from typing import Dict, Any, Set, Optional
from yaml_oop.core.custom_errors import (
    KeySealedError,
    ConflictingDeclarationError,
    NoOverrideError,
    InvalidVariableError,
    InvalidInstantiationError,
    InvalidDeclarationError,
)

import yaml_oop.core.parser.parser as parser
from yaml_oop.core.declarations import DeclarationType
import yaml_oop.core.parser.config_parser as config_parser
import yaml_oop.core.parser.next_parser as next_parser
from yaml_oop.core.parser.context import ProcessingContext


def process_inherit(
    sub_data: dict,
    base_data: dict,
    context: ProcessingContext
) -> None:

    if DeclarationType.BASE_CONFIG in base_data:
        config_parser.process_base_config_declaration(yaml_data=base_data,
                                                      context=context)

    # Map matches the base_data keys to the sub keys with their declarations.
    # sub_key_map Key = parsed key (no declaration)
    # sub_key_map Value = Full key
    sub_key_map = map_parsed_sub_keys(sub_data)

    # List containing:
    # [base_key (without declarations), full_key (with_declaratios), list of declarations]
    base_key_list = list_parsed_base_keys(base_data)

    # Iterate through parsed base keys and perform inheritance logic
    for parsed_base_key, full_base_key, base_declarations in base_key_list:

        # Initialize base declaration logic
        full_base_key, base_key_declarations = context.extract_base_declarations(base_data, full_base_key)  
        if DeclarationType.PRIVATE in base_key_declarations:
            continue  # Do no inherit private keys

        # Matching sub_key does not exist. Apply full inheritance logic.
        if parsed_base_key not in sub_key_map:
            if DeclarationType.ABSTRACT in context.base_declarations or DeclarationType.ABSTRACT in base_key_declarations:
                raise NotImplementedError(f"Base YAML declares abstract, but base key: '{parsed_base_key}' is not implemented in sub YAML: '{sub_data}'.")
            if contains_conflicting_declaration(base_data[full_base_key], set()):
                raise ConflictingDeclarationError(f"Base key: '{parsed_base_key}' cannot declare more than one of: abstract, sealed, private.")
            if DeclarationType.OVERRIDE in context.sub_declarations:
                # If override was declared for a key.
                # New keys are not inherited.
                continue
            remove_all_key_declarations(base_data[full_base_key], "key", DeclarationType.PRIVATE)
            sub_data[full_base_key] = base_data[full_base_key]
            continue

        # Matching sub_key exists. Apply standard inheritance logic.
        sub_key = sub_key_map.pop(parsed_base_key)
        sub_key, sub_key_declarations = context.extract_sub_declarations(sub_data, sub_key)
        # Catch case where type mismatch between base and sub occurs
        if sub_key in sub_data and is_type_mismatch(sub_data[sub_key], base_data[full_base_key]):
            raise TypeError(f"Type mismatch for base YAML key: '{full_base_key}': {type(base_data[full_base_key])}, and sub YAML key: '{sub_key}': {type(sub_data[sub_key])}.")
        # Cannot inherit from sealed base keys
        if DeclarationType.SEALED in context.base_declarations or DeclarationType.SEALED in base_key_declarations:
            raise KeySealedError(f"Cannot override base key: '{full_base_key}' when base key is sealed.")
        if type(base_data[full_base_key]) is dict:
            process_inherit(
                sub_data=sub_data[sub_key],
                base_data=base_data[full_base_key],
                context=ProcessingContext(
                    directory=context.directory,
                    loader=context.loader,
                    variables=context.variables,
                    sub_files=context.sub_files.copy(),
                    sub_declarations=context.sub_declarations.copy() | sub_key_declarations,
                    base_declarations=context.base_declarations.copy() | base_key_declarations
                )
            )
        elif type(base_data[full_base_key]) is list:
            if DeclarationType.APPEND in sub_key_declarations:
                sub_data[sub_key] = process_append_prepend(sub_data[sub_key], base_data[full_base_key], "append", context)
                continue
            if DeclarationType.PREPEND in sub_key_declarations:
                sub_data[sub_key] = process_append_prepend(sub_data[sub_key], base_data[full_base_key], "prepend", context)
                continue
            if DeclarationType.MERGE in sub_key_declarations:
                sub_data[sub_key] = process_merge(sub_data[sub_key], base_data[full_base_key], context)
                continue
            if DeclarationType.OVERRIDE not in sub_key_declarations and DeclarationType.OVERRIDE not in context.sub_declarations:
                raise NoOverrideError(f"No override declared for '{sub_key}' list despite having matching key in base_config.")
        else:  # Data is scalar
            if DeclarationType.OVERRIDE in sub_key_declarations or DeclarationType.OVERRIDE in context.sub_declarations:
                continue  # Maintain sub_data's values.
            raise NoOverrideError(f"No override declared for '{sub_key}' scalar despite having matching key in base_config.")
            # Maintain sub_data's values.
        # else:  # base_data[full_base_key] is a scalar
        #     if DeclarationType.OVERRIDE not in sub_key_declarations and DeclarationType.OVERRIDE not in context.sub_declarations:
        #         raise NoOverrideError(f"No override declared for '{sub_key}' scalar despite having matching key in base_config.")

    # Process remaining sub_data keys that did not match base_data keys
    for sub_key in sub_key_map.values():
        sub_key, sub_key_declarations = context.extract_sub_declarations(sub_data, sub_key)
        if DeclarationType.APPEND in sub_key_declarations or DeclarationType.PREPEND in sub_key_declarations or DeclarationType.MERGE in sub_key_declarations:
            raise InvalidDeclarationError(f"Key: '{sub_key}' cannot declare append, prepend, or merge without an immediate base key to inherit from.")
        next_data = next_parser.process_next(
            yaml_data=sub_data[sub_key],
            context=ProcessingContext(
                directory=context.directory,
                loader=context.loader,
                variables=context.variables,
                sub_files=context.sub_files.copy(),
                sub_declarations=context.sub_declarations.copy() | sub_key_declarations,
            )
        )
        sub_data[sub_key] = next_data if next_data is not None else sub_data[sub_key]


def process_append_prepend(sub_data, base_data, mode: str, context: ProcessingContext):
    """Append sub_data's values to base_data's values and return new list."""

    # TO DO: Test nested append prepend merge
    remove_all_key_declarations(base_data, "declaration", DeclarationType.SEALED)
    remove_all_key_declarations(base_data, "declaration", DeclarationType.OVERRIDE)
    remove_all_key_declarations(base_data, "key", DeclarationType.PRIVATE)
    next_parser.process_next(
        yaml_data=base_data,
        context=ProcessingContext(
            directory=context.directory,
            loader=context.loader,
            variables=context.variables,
            sub_files=context.sub_files.copy(),
        )
    )

    if mode == "append":
        return base_data + sub_data
    elif mode == "prepend":
        return sub_data + base_data
    else:
        # Should not reach this point
        raise Exception("Incorrect mode arg in process_append_prepend function call. Please open a Github issue with your given input.")


def process_merge(sub_data, base_data, context: ProcessingContext):
    """Merge base_data's list values into sub_data's list values and return new list.
       Merging involving applying inheritance rules to each item of matching index in sub and base lists."""

    total_length = max(len(sub_data), len(base_data))
    for i in range(total_length):
        if i >= len(sub_data):
            sub_data.append(base_data[i])
        elif i >= len(base_data):
            pass
        elif sub_data[i] is None:
            sub_data[i] = base_data[i]
        elif base_data[i] is None:
            pass
        else:
            # Sub and base both have values, so apply inheritance rules
            # Apply inheritance rules only if both sub and base are dicts
            if (type(sub_data[i]) is not dict and base_data[i] is not None) or \
               (type(base_data[i]) is not dict and sub_data[i] is not None):
                raise TypeError(f"Cannot merge list items at index {i} because one or both items are not dictionaries.")
            process_inherit(
                sub_data=sub_data[i],
                base_data=base_data[i],
                context=ProcessingContext(
                    directory=context.directory,
                    loader=context.loader,
                    variables=context.variables,
                    sub_files=context.sub_files.copy(),
                )
            )
    return sub_data


def remove_all_key_declarations(data, mode: str, declaration: str):
    """Removes all keys and subkeys that declares declaration inplace.
       Mode == "declaration" to remove declaration.
       Mode == "key" to remove entire key."""
    if type(data) is dict:
        for key in list(data.keys()):
            if declaration in parser.find_key_declarations(key):
                if mode == "key":
                    data.pop(key)
                elif mode == "declaration":
                    parser.remove_key_declaration(data, key, declaration)
            else:
                remove_all_key_declarations(data[key], mode, declaration)
    if type(data) is list:
        for item in data:
            remove_all_key_declarations(item, mode, declaration)
    return data


def map_parsed_sub_keys(sub_data: dict) -> dict:
    """Map parsed sub keys to their declaration and full key.
       Key = parsed key (no declaration)
       Value = full key."""
    key_map = {}
    for full_key in sub_data:
        parsed_key = parser.key_without_declaration(full_key)
        key_map[parsed_key] = full_key
    return key_map


def list_parsed_base_keys(base_data: dict) -> list:
    """List parsed base keys to their declaration and full key.
       Value = parsed key, full key, list of declarations."""
    key_list = []
    for full_key in base_data:
        declarations = parser.find_key_declarations(full_key)    
        parsed_key = parser.key_without_declaration(full_key)
        key_list.append((parsed_key, full_key, declarations))
    return key_list


def is_type_mismatch(sub_data, base_data) -> bool:
    """Returns true if types of base and sub prevent inheritance."""
    if sub_data is None or base_data is None:
        return False
    # Empty dicts or lists are essentially None
    elif not sub_data or not base_data:
        return False
    elif type(base_data) is not type(sub_data):
        return True
    # sub and base are both non-empty dicts or non-empty lists 
    return False


# TO DO: Inefficient. Should not iterate through all child keys.
def contains_conflicting_declaration(data, found_declarations: set) -> bool:
    """Returns true if members of base data contain one or more of declarations arg.
       A conflict is defined as more than one declaration type of abstract, sealed, and private."""
    if type(data) is dict:
        for key in data:
            declarations = parser.find_key_declarations(key)
            found_declarations_copy = found_declarations.copy()
            for declaration in declarations:
                if declaration in DeclarationType.BASE_KEY_DECLARATIONS:
                    found_declarations_copy.add(declaration)

            if len(found_declarations_copy) > 1:
                return True
            elif contains_conflicting_declaration(data[key], found_declarations_copy):
                return True
    elif type(data) is list:
        for item in data:
            if contains_conflicting_declaration(item, found_declarations.copy()):
                return True
    return False
