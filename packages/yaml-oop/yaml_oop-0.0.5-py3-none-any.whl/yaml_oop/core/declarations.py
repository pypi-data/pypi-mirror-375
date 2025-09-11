"""
Declarations (keywords) using in YAML compose processing.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Set, Optional


class DeclarationType():
    """Types of declarations that can be applied to YAML elements."""

    BASE_CONFIG = "(base_config)"       
    BASE_CONFIG_PATH = "(path)"

    VARIABLES = "(variables)"
    OPTIONAL = "(optional)"
    CARRYOVER = "(carryover)"
    GLOBAL = "(global)"

    ABSTRACT_CONFIG = "(abstract_config)"
    SEALED_CONFIG = "(sealed_config)"
    OVERRIDE_CONFIG = "(override_config)"

    ABSTRACT = "(abstract)"
    SEALED = "(sealed)"
    PRIVATE = "(private)"
    OVERRIDE = "(override)"
    APPEND = "(append)"
    PREPEND = "(prepend)"
    MERGE = "(merge)"

    # Convenience sets for different declaration categories

    BASE_KEY_DECLARATIONS = {
        ABSTRACT,
        SEALED,
        PRIVATE,
        OPTIONAL
    }

    # Declarations available to keys in sub class
    SUB_KEY_DECLARATIONS = {
        OVERRIDE,
        APPEND,
        PREPEND,
        MERGE,
        OPTIONAL
    }

    # Declarations available to variables
    VARIABLE_DECLARATIONS = {
        ABSTRACT,  # Abstract variables cannot be used until overriden.
        SEALED,  # Sealed variables cannot be overriden.
        OVERRIDE,
        CARRYOVER,  # Declared during instantiation. Inherits variables from base config during instantiation.
        GLOBAL,  # Declared anywhere. Inherits variables from base config through all levels of instantiation.
    }

    # Declarations for entire file
    CONFIG_DECLARATIONS = {
        ABSTRACT_CONFIG,
        SEALED_CONFIG,
        OVERRIDE_CONFIG
    }
   

@dataclass(frozen=True)
class Declarations:
    """Represents a declaration (keyword) applied to a YAML element."""
    
    type: DeclarationType
    parsed_key: str
    original_key: str

    # TO DO: Data extraction functions here

    