# phase2/sprint1/utils/file_helper.py

import os
import json

from typing import List

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

def load_tools(dir_path: str) -> List[dict]:
    if not os.path.exists(dir_path):
        raise FileNotFoundError(f"Tools file not found: {dir_path}")
    tool_schemas = []
    for filename in os.listdir(dir_path):
        if filename.endswith(".json"):
            full_path = os.path.join(dir_path, filename)
            try:
                schema_content = load_schema(full_path)
                tool_schemas.append({
                    "type": "function",
                    "function": schema_content
                })
            except Exception as e:
                print(f"Warning: Could not load or parse {filename}. Error: {e}")
    
    return tool_schemas
