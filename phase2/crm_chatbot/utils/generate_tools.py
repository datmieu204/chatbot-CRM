# crm_chatbot/utils/generate_tools.py

import json
from typing import Any, Dict, List, Optional, Tuple


def load_openapi(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def json_type_to_py(t: str):
    return {
        "string": (str, None),
        "integer": (int, None),
        "number": (float, None),
        "boolean": (bool, None),
        "array": (list, None),
        "object": (dict, None),
    }.get(t, (str, None))


def method_to_action(method: str, path: str) -> str:
    m = method.upper()
    if m == "POST":
        return "create"
    if m in ("PUT", "PATCH"):
        return "update"
    if m == "DELETE":
        return "delete"
    if m == "GET":
        return "get" if "{" in path and "}" in path else "list"
    return "chat"


def infer_domain(path: str, operation: Dict[str, Any]) -> str:
    tags = operation.get("tags") or []
    if tags:
        return tags[0].lower()
    seg = path.strip("/").split("/")[0] if "/" in path else path.strip("/")
    return (seg or "general").lower()


def _resolve_ref(root: Dict[str, Any], ref: str) -> Dict[str, Any]:
    """Resolve a JSON Pointer like '#/components/schemas/Foo' from the OpenAPI root."""
    if not ref.startswith("#/"):
        raise KeyError(f"Unsupported $ref: {ref}")
    obj = root
    for part in ref.lstrip("#/").split("/"):
        obj = obj[part]
    return obj

def deref_once(obj: Dict[str, Any], root: Dict[str, Any]) -> Tuple[Dict[str, Any], Optional[str]]:
    """If obj is a $ref, resolve once against the OpenAPI root."""
    if isinstance(obj, dict) and "$ref" in obj:
        ref = obj["$ref"]
        return _resolve_ref(root, ref), ref
    return obj, None


def extract_parameters(operation: Dict[str, Any], openapi_root: Dict[str, Any]) -> Dict[str, Any]:
    properties: Dict[str, Any] = {}
    required: List[str] = []

    # 1) parameters (query/path), include refs
    for p in (operation.get("parameters") or []):
        if "$ref" in p:
            p, _ = deref_once(p, openapi_root)

        pname = p.get("name")
        if not pname:
            continue

        preq = p.get("required", False)

        if "schema" in p:
            pschema = p["schema"]
        elif "content" in p and isinstance(p["content"], dict) and p["content"]:
            _, mt_obj = next(iter(p["content"].items()))
            pschema = mt_obj.get("schema", {"type": "string"})
        else:
            pschema = {"type": "string"}

        pres, pref = deref_once(pschema, openapi_root)
        prop = {"description": p.get("description", ""), **pres}
        if pref:
            prop["x-fromRef"] = pref

        properties[pname] = prop
        if preq:
            required.append(pname)

    # 2) requestBody (application/json)
    rb = operation.get("requestBody")
    if rb:
        rb_req = rb.get("required", False)
        content = rb.get("content", {})
        appjson = content.get("application/json", {})
        if appjson:
            s = appjson.get("schema", {})
            sres, sref = deref_once(s, openapi_root)
            if sres.get("type") == "object":
                if sref:
                    sres["x-originalRef"] = sref
                for k, v in (sres.get("properties") or {}).items():
                    vres, vref = deref_once(v, openapi_root)
                    prop = {**vres}
                    if "description" not in prop:
                        prop["description"] = v.get("description", "")
                    if vref:
                        prop["x-fromRef"] = vref
                    properties[k] = prop
                for r in (sres.get("required") or []):
                    if r not in required:
                        required.append(r)
            else:
                properties["body"] = sres
                if rb_req:
                    required.append("body")

    return {"type": "object", "properties": properties, "required": required}



def build_tools_from_openapi(openapi_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
    paths = openapi_dict.get("paths", {})

    tools: List[Dict[str, Any]] = []
    for path, ops in paths.items():
        path_level_params = ops.get("parameters", [])  # path-level params
        for method, op in ops.items():
            if method.upper() not in ("GET", "POST", "PUT", "PATCH", "DELETE"):
                continue

            # Merge path-level + op-level parameters
            merged_params = (path_level_params or []) + (op.get("parameters") or [])
            op_merged = {**op, "parameters": merged_params}

            action = method_to_action(method, path)
            domain = infer_domain(path, op)
            params = extract_parameters(op_merged, openapi_dict)  # pass ROOT

            name = op.get("operationId") or f"{action}_{domain}".replace(" ", "_").lower()
            tool = {
                "name": name,
                "description": op.get("summary") or op.get("description") or f"{action} {domain}",
                "x-endpoint": {"method": method.upper(), "path": path},
                "x-router": {"action": action, "domain": domain},
                "parameters": params,
            }
            if "$ref" in op:
                tool["x-originalRef"] = op["$ref"]
            tools.append(tool)

    return tools