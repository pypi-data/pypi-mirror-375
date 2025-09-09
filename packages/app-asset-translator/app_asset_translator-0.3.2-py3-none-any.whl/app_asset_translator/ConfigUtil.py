import os

import yaml

def get_config(config_path=None):
    try:
        path = config_path or "app-asset-translator.yaml"
        print(f"Opening config: {os.path.abspath(path)}")
        return yaml.safe_load(open(path))
    except Exception as e:
        print(f"Config error: {e}")
        return {}
