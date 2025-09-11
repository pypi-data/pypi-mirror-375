import sys
import os
import yaml
from typing import Tuple, Any, Dict, Optional, Set
from yaml_oop.core.custom_errors import (
    KeySealedError,
    ConflictingDeclarationError,
    NoOverrideError,
    InvalidVariableError
)
import yaml_oop.core.parser.parser as parser
from yaml_oop.core.declarations import DeclarationType


def process_variables(data: Any, parent_variables: Dict[str, Any], is_base_config: bool) -> bool:
    """Process variables within data in place.
    Returns True if this node became empty and should be removed by its parent."""
    if is_base_config is False:
        parent_variables = add_variables(data, parent_variables.copy())
    return replace_with_variables(data, parent_variables, is_base_config)


def inherit_variables(base_data: Any, config_info: Dict[str, Any]) -> Dict[str, Any]:
    """When inheriting variables from instantiation, search both base and sub data for variable config and variable declarations.
       Then add variables to existing variable dict with inheritance and instantiation rules inplace.
       Pops variable decarations from data inplace.
       Returns variable dictionary."""

    base_variables = add_variables(base_data, {})
    instantiation_variables = add_variables(config_info, base_variables)
    return instantiation_variables


def replace_with_variables(data: Any, variables: Dict[str, Any], is_base_config: bool) -> bool:
    """Replaces values/items and processes child nodes in place.
    Returns True if this node became empty and should be removed by its parent."""
    if type(data) is dict:
        for key in list(data.keys()):
            if key == DeclarationType.BASE_CONFIG:
                is_base_config = True

            if is_base_config and DeclarationType.VARIABLES in find_variable_declarations(key):
                carryover_variables = {variable_key: value for variable_key, value in data[key].items() if DeclarationType.CARRYOVER in variable_key}
                carryover_variables.update({variable_key: value for variable_key, value in variables.items() if DeclarationType.GLOBAL in value[1]})
                for carryover_key in carryover_variables:
                    carryover_key_declarations, parsed_carryover_key = find_variable_key_declarations(carryover_key)
                    if parsed_carryover_key in variables:
                        data[key][carryover_key] = variables[parsed_carryover_key][0]
                        carryover_key = parser.remove_key_declaration(data[key], carryover_key, DeclarationType.CARRYOVER)
                        if DeclarationType.ABSTRACT in carryover_key_declarations:
                            parser.remove_key_declaration(data[key], carryover_key, DeclarationType.ABSTRACT)
            elif DeclarationType.OPTIONAL in parser.find_key_declarations(key):
                key = parser.remove_key_declaration(data, key, DeclarationType.OPTIONAL)
                if type(data[key]) is not str:
                    raise InvalidVariableError(f"Optional declaration must be associated with a string value. Key {key} is type: {type(data[key])}")
                if data[key] in variables:
                    replace_value(data, key, variables)
                else:
                    data.pop(key)
            elif type(data[key]) is dict or type(data[key]) is list:
                if process_variables(data[key], variables, is_base_config):
                    data.pop(key)
            else:
                replace_value(data, key, variables)
        return data == {} or data == []
    elif type(data) is list:
        i = 0
        while i < len(data):
            if type(data[i]) is str and data[i] == DeclarationType.BASE_CONFIG:
                is_base_config = True

            if type(data[i]) is str and DeclarationType.OPTIONAL in parser.find_key_declarations(data[i]):
                data[i] = " ".join(data[i].split()[1:])
                if data[i] in variables:
                    replace_value(data, i, variables)
                    i += 1
                else:
                    data.pop(i)
            elif type(data[i]) is dict or type(data[i]) is list:
                if is_base_config and type(data[i]) is str and DeclarationType.VARIABLES in find_variable_declarations(data[i]):
                    for j in data[i]:
                        if j == DeclarationType.BASE_CONFIG:
                            replace_value(data[i], j, variables)
                            i += 1
                else:
                    if process_variables(data[i], variables, is_base_config):
                        data.pop(i)
                    else:
                        i += 1
            else:
                replace_value(data, i, variables)
                i += 1
        return data == []
    else:
        return False


def add_variables(data: Any, parent_variables: Dict[str, Any]) -> Dict[str, Any]:
    """Search data for variable config and variable declarations.
       Then add variables to existing variable dict with inheritance rules inplace.
       Pops variable decarations from data inplace.
       Should be called at each node before applying inheritance rules to data keys.
       Returns modified variable dictionary inplace."""
    if type(data) is dict:
        for key in list(data.keys()):
            if type(key) is not str:
                continue
            declarations = find_variable_declarations(key)
            if DeclarationType.VARIABLES in declarations:
                variable_declaration_to_keys_declarations(declarations, data[key])
                merge_variables(parent_variables, data[key])
                data.pop(key)
    elif type(data) is list:
        i = 0
        while i < len(data):
            if type(data[i]) is dict and len(data[i]) == 1 \
                    and any(DeclarationType.VARIABLES in key for key in data[i]):
                for key in data[i]:  # Should be only 1 key
                    declarations = find_variable_declarations(key)
                    variable_declaration_to_keys_declarations(declarations, data[i])
                    merge_variables(parent_variables, data[i][key])
                    data.pop(i)
            else:
                i += 1
    return parent_variables


def add_injected_variables(injected_variables: Dict[str, Any]) -> Dict[str, Tuple[Any, Set[str]]]:
    """Converts injected variables into modified variable dict format.
       Variable dict format:
       Key = key without declaration (key is the substring to be replaced in YAML)
       Value = (replacement substring, declarations set)"""
    return_variables = {}
    for variable in injected_variables:
        declarations, parsed_key = find_variable_key_declarations(variable)
        return_variables[parsed_key] = (injected_variables[variable], declarations)
    return return_variables


def merge_variables(parent_variables: Dict[str, Tuple[Any, Set[str]]], child_variables: Any) -> Dict[str, Tuple[Any, Set[str]]]:
    """Add child variables to parent variables inplace.
       Variable dict format:
       Key = key without declaration (key is the substring to be replaced in YAML)
       Value = (replacement substring, declarations set)"""
    if not child_variables:
        return parent_variables
    
    if type(child_variables) is not dict:
        raise InvalidVariableError(f"Variable must be a dict. Invalid value: '{child_variables}'")
    
    for child_key in child_variables:
        child_declarations, child_parsed_key = find_variable_key_declarations(child_key)
        new_variable = (child_variables[child_key], child_declarations)

        if not child_declarations:
            if child_parsed_key in parent_variables:
                raise NoOverrideError(f"Cannot override variable: '{child_parsed_key}' when child variable does not declare override.")
            else:
                parent_variables[child_parsed_key] = new_variable
        if DeclarationType.ABSTRACT in child_declarations:
            if child_parsed_key in parent_variables and DeclarationType.OVERRIDE not in child_declarations:
                raise NoOverrideError(f"Cannot override variable: '{child_parsed_key}' when parent variable does not declare override.")
            else:
                parent_variables[child_parsed_key] = new_variable
        if DeclarationType.SEALED in child_declarations:
            if child_parsed_key in parent_variables and DeclarationType.OVERRIDE not in child_declarations:
                raise NoOverrideError(f"Cannot override variable: '{child_parsed_key}' when child variable is sealed.")
            else:
                parent_variables[child_parsed_key] = new_variable
        if DeclarationType.OVERRIDE in child_declarations:
            if child_parsed_key not in parent_variables:
                print(f"Warning. Override was declared for variable: '{child_parsed_key}', but no parent variable exists to override.")
            elif DeclarationType.SEALED in parent_variables[child_parsed_key][1]:
                raise KeySealedError(f"Cannot override variable: '{child_parsed_key}' when parent variable is sealed.")
            parent_variables[child_parsed_key] = new_variable
    return parent_variables


def replace_value(data: Any, key_or_index: Any, variables: Dict[str, Tuple[Any, Set[str]]]) -> None:
    """For non-string value in data, replaces any matching data_value with variable value inplace.
       For string value in data, replaces any matching substring of data_value with variable value inplace.
       Returns replaced value."""
    if type(data[key_or_index]) is str:
        for variable_key, variable_value in variables.items():
            if type(data[key_or_index]) is not str:
                break  # value was replaced with a non-string; multiple replacements not possible
            elif variable_key in data[key_or_index]:
                if DeclarationType.ABSTRACT in variable_value[1]:
                    raise NotImplementedError(f"Abstract variable {variable_key} cannot be used before being overriden.")
                if type(variable_value[0]) is str:  # TO DO: Multiple string replacements possible. But what if string replacements are ambiguous?
                    data[key_or_index] = data[key_or_index].replace(variable_key, variable_value[0])
                else:
                    data[key_or_index] = variable_value[0]
                    break  # value was replaced with a non-string; multiple replacements not possible
    else:
        if data[key_or_index] in variables.items():
            data[key_or_index] = variables[data[key_or_index]][0]
    

def find_variable_declarations(key: str) -> set:
    """Returns all declarations within the potential variable declaration."""
    if key == "" or key is None:
        return set()
    else:
        declarations = set()
        for item in key.split(" "):
            if item in DeclarationType.VARIABLE_DECLARATIONS or item == DeclarationType.VARIABLES:
                declarations.add(item)
        return declarations


def find_variable_key_declarations(key: str) -> tuple[set, str]:
    """Returns all declarations and key with no declarations within a variable key."""
    if key == "" or key is None:
        return set(), key
    else:
        declarations = set()
        for item in key.split(" "):
            if item in DeclarationType.VARIABLE_DECLARATIONS:
                declarations.add(item)
        return declarations, key.split(" ")[-1]


def variable_declaration_to_keys_declarations(declarations: set, variables: Dict[str, Any]) -> None:
    """Replaces all variable's declarations to key declarations inplace."""
    
    if not variables:
        return
        
    if type(variables) is not dict:
        raise InvalidVariableError("Variables must be a dict.")

    is_abstract, is_sealed, is_override, is_optional = False, False, False, False
    if DeclarationType.ABSTRACT in declarations:
        is_abstract = True
    if DeclarationType.SEALED in declarations:
        is_sealed = True
    if DeclarationType.OVERRIDE in declarations:
        is_override = True
    if DeclarationType.OPTIONAL in declarations:
        is_optional = True

    for key in list(variables.keys()):
        if is_abstract:
            key = parser.add_key_declaration(variables, key, DeclarationType.ABSTRACT)
        if is_sealed:
            key = parser.add_key_declaration(variables, key, DeclarationType.SEALED)
        if is_override:
            key = parser.add_key_declaration(variables, key, DeclarationType.OVERRIDE)
        if is_optional:
            key = parser.add_key_declaration(variables, key, DeclarationType.OPTIONAL)
        