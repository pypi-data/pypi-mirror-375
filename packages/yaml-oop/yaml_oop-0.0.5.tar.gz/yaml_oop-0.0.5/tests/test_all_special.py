import pytest
import os
import sys
import yaml

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
TESTS_DIR = os.path.join(BASE_DIR, 'tests')
sys.path.append(BASE_DIR)

from tests.test import assert_result_config
from yaml_oop.core import oopify
from yaml_oop.core.custom_errors import (
    KeySealedError, 
    ConflictingDeclarationError, 
    NoOverrideError, 
    InvalidDeclarationError,
    CircularInheritanceError)


def test_failed_circular_inheritance():
    input_path = os.path.join(TESTS_DIR, 'test_special', 'failed_circular_inheritance', 'sub_config.yaml')
    with pytest.raises(CircularInheritanceError) as executeInfo:
        oopify(file_path=input_path, directory=TESTS_DIR, Loader=yaml.FullLoader)
    assert executeInfo.type is CircularInheritanceError