from pathlib import Path
import yaml 

BASE_DIR = Path(__file__).resolve().parents[2]
print (f"Base directory set to: {BASE_DIR}")

def load_yaml(path):
    if not Path(path).exists():
        raise FileNotFoundError(f"YAML file not found at {path}")
    with open(path, 'r') as file:
        return yaml.safe_load(file)
    
def get_base_dir():
    """Get the base directory of the project."""
    return BASE_DIR