# phase2/sprint2/src/parsers/postman_parser.py

import json

def load_postman(file_path: str) -> dict:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def extract_postman_tools(collection: dict) -> list:
    tools = []
    for item in collection.get("item", []):
        request = item.get("request", {})
        method = request.get("method", "GET")
        url = request.get("url", {})
        name = item.get("name", f"{method}_{url}")

        tool = {
            "name": name,
            "description": request.get("description", ""),
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }

        if request.get("body", {}).get("raw"):
            try:
                body_schema = json.loads(request["body"]["raw"])
                for k, v in body_schema.items():
                    tool["parameters"]["properties"][k] = {"type": type(v).__name__}
            except:
                pass

        tools.append(tool)
    return tools
