import yaml
import yaml_oop.core.parser.variable_parser as variable_parser
import yaml_oop.core.parser.config_parser as config_parser


def oopify(file_path: str, directory: str, Loader, variables=None):
    """Read a YAML file, process it with inheritance rules, and return the complete YAML data as dict or list."""
    if variables is None:
        variables = {}

    yaml_data = {}
    try:
        with open(file_path, 'r') as file:
            yaml_data = yaml.load(file, Loader=Loader)
    except Exception as e:
        print(f"Error reading YAML file: {e}")
        return None

    variables = variable_parser.add_injected_variables(variables)
    yaml_data = config_parser.process_root_yaml(yaml_data=yaml_data, directory=directory, variables=variables, loader=Loader)
    return yaml_data
