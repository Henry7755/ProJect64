from pathlib import Path
import yaml 

def load_yaml(path):
    if not Path(path).exists():
        raise FileNotFoundError(f"YAML file not found at {path}")
    with open(path, 'r') as file:
        return yaml.safe_load(file)