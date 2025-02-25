"""
This module loads the application configuration from a YAML file.
"""

import yaml

with open("application.yml") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
