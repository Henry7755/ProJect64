import os
from pathlib import Path

# print(Path.cwd())

# for p in Path().iterdir():
#     print(p)

base_dir = Path("src")
print (f"Base directory: {base_dir.name}")
p = Path(__file__).resolve().parents[1]
print (p)