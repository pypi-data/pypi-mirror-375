import yaml
import platformdirs
import os

def load_config():
    config_dir = platformdirs.user_config_dir("root")
    config_path = os.path.join(config_dir, "config.yaml")
    default_config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    
    os.makedirs(config_dir, exist_ok=True)
    with open(default_config_path, "r") as f:
        default_config = yaml.safe_load(f)
    with open(config_path, "w") as f:
        yaml.safe_dump(default_config, f)
    return default_config

def get_config_path():
    return os.path.join(platformdirs.user_config_dir("root"), "config.yaml")
