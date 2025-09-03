# phase2/sprint2/src/parsers/openapi_parser.py

import yaml
import json
import requests
from functools import lru_cache

@lru_cache(maxsize=None)
def fetch_remote_spec(url):
    """Fetches and caches remote specifications."""
    print(f"   - INFO: Fetching remote schema from {url}...")
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"   - ⚠️ WARNING: Could not fetch remote ref {url}. Error: {e}. Skipping.")
        return None

def resolve_ref(spec, ref):
    """
    Resolves a $ref pointer, supporting both local and remote URLs.
    """
    if not isinstance(ref, str) or '#' not in ref:
        return ref

    url, pointer = ref.split('#', 1)
    
    # Determine the document to search in
    if url:
        document = fetch_remote_spec(url)
        if document is None:
            return {"type": "object", "description": f"Unresolved remote reference: {url}"}
    else:
        document = spec

    # Navigate through the pointer
    parts = pointer.strip('/').split('/')
    d = document
    for part in parts:
        if part in d:
            d = d[part]
        else:
            return {"type": "object", "description": f"Unresolved path: {pointer}"}
    
    # If the resolved part is another reference, resolve it recursively
    if isinstance(d, dict) and '$ref' in d:
        return resolve_ref(spec, d['$ref'])
        
    return d

def parse_openapi_spec(file_path):
    """
    Parses an OpenAPI specification file (JSON or YAML).
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            if file_path.endswith(('.yaml', '.yml')):
                spec = yaml.safe_load(f)
            else:
                spec = json.load(f)
        
        print(f"Successfully analyzed OpenAPI file: {spec['info']['title']}")
        return spec
    except Exception as e:
        print(f"Error parsing OpenAPI file {file_path}: {e}")
        return None