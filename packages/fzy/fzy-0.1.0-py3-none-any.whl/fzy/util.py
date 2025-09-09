"""
The dreaded miscellaneous routines module...
"""

import yaml


def use_yaml_multiline_strings() -> None:
    """
    Globally configure the `yaml` module's dump functions to format multiline
    strings using the ``|`` syntax.
    """

    def represent_str(dumper: yaml.Dumper, string: str):
        if len(string.splitlines()) > 1:
            return dumper.represent_scalar("tag:yaml.org,2002:str", string, style="|")
        else:
            return dumper.represent_scalar("tag:yaml.org,2002:str", string)

    yaml.add_representer(str, represent_str)
