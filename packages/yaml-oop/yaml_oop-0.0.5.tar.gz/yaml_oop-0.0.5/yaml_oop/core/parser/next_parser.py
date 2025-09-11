from typing import Any, Optional

from yaml_oop.core.custom_errors import (
    KeySealedError,
    ConflictingDeclarationError,
    NoOverrideError,
    InvalidVariableError,
    InvalidInstantiationError,
    InvalidDeclarationError,
)

import yaml_oop.core.parser.parser as parser
import yaml_oop.core.parser.config_parser as config_parser
from yaml_oop.core.declarations import DeclarationType
from yaml_oop.core.parser.context import ProcessingContext


def process_next(yaml_data: Any, context: ProcessingContext) -> Optional[Any]:
    """Traverse yaml_data to process base_config declarations.
    Returns a replacement node if the current yaml_data should be replaced by another object (e.g., a list).
    Otherwise returns None if yaml_data should be unmodified."""

    if type(yaml_data) is list:
        i = 0
        while i < len(yaml_data):
            item = yaml_data[i]
            if type(item) is dict and DeclarationType.BASE_CONFIG in item:
                base_data = config_parser.process_base_config_declaration(
                    yaml_data=item,
                    context=context)
                yaml_data[i] = base_data if base_data is not None else yaml_data[i]
                if type(yaml_data[i]) is list:
                    # List insertion
                    yaml_data[i:i + 1] = yaml_data[i]
            else:
                process_next(
                    yaml_data=item,
                    context=context)
                i += 1

    elif type(yaml_data) is dict:
        if DeclarationType.BASE_CONFIG in yaml_data:
            base_data = config_parser.process_base_config_declaration(
                yaml_data=yaml_data,
                context=context)
            if base_data is not None:
                return base_data
            
        for key in list(yaml_data.keys()):
            key, declarations = context.extract_next_declarations(yaml_data, key)
            if DeclarationType.APPEND in declarations or DeclarationType.PREPEND in declarations or DeclarationType.MERGE in declarations:
                raise InvalidDeclarationError(f"Base key: '{key}' cannot declare append or prepend without an immediate base key to inherit from.")
            next_data = process_next(
                yaml_data=yaml_data[key],
                context=ProcessingContext(
                    directory=context.directory,
                    loader=context.loader,
                    variables=context.variables,
                    sub_declarations=context.sub_declarations.copy() | declarations,
                    base_declarations=set(),
                )
            )
            yaml_data[key] = next_data if next_data is not None else yaml_data[key]
    return None
