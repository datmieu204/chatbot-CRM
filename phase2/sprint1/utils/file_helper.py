# phase2/sprint1/utils/file_helper.py

import os
import json

def load_prompt(file_path: str) -> str:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Prompt file not found: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()
    
def load_schema(file_path: str) -> dict:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Schema file not found: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)