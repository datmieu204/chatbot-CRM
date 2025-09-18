# crm_chatbot/core/config_loader.py

import os, json, glob, logging
from typing import Dict, Any

logger = logging.getLogger("CRMChatbot")

def load_action_map(file_path: str = "crm_chatbot/docs/actions.json") -> Dict[str, Any]:
    try:
        base_dir = os.getcwd()
        absolute_path = os.path.join(base_dir, file_path)

        with open(absolute_path, 'r', encoding='utf-8') as f:
            actions_list = json.load(f)
            
        action_map = {action['action_id'].replace('.', '_'): action for action in actions_list}
        logging.info(f"Successful load {len(action_map)} actions from file {absolute_path}")

        return action_map
    except Exception as e:
        logging.error(f"Error load action map: {e}", exc_info=True)
        raise

def load_all_domains(dir_path: str = "agent_domain/") -> Dict[str, Any]:
    base_dir = os.getcwd()
    absolute_path = os.path.join(base_dir, dir_path)
    domains = {}

    for file_path in glob.glob(os.path.join(absolute_path, '*.json')):
        domain_name = f"agent_{os.path.basename(file_path).replace('.json','')}"

        with open(file_path, 'r', encoding='utf-8') as f:
            domains[domain_name] = json.load(f)

    if "agent_General" not in domains:
        domains["agent_General"] = []

    logging.info(f"Successful load {len(domains)} domains from file {absolute_path}")

    return domains
