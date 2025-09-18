# crm_chatbot/graph/actions.py

import json, logging, httpx

logger = logging.getLogger("CRMChatbot")

def execute_crm_action(client: httpx.Client, action, args):
    if not action:
        return {"ok": False, "error": "Action not found"}
    
    method = action.get("method", "GET").upper()
    path = action.get("path", "/")
    path_params = {k for k in args if f"{{{k}}}" in path}
    body_or_params = {k: v for k, v in args.items() if k not in path_params}

    for k in path_params:
        path = path.replace(f"{{{k}}}", str(args[k]))

    try:
        if method in ("GET", "DELETE"):
            r = client.request(method, path, params=body_or_params)
        else:
            r = client.request(method, path, json=body_or_params)
            
        r.raise_for_status()

        return {"ok": True, "result": r.json() if r.content else {}}
    except Exception as e:
        logger.error(f"Lỗi khi gọi API: {e}", exc_info=True)
        return {"ok": False, "error": str(e)}
