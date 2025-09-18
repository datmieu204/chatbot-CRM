# crm_chatbot/core/http_client.py

from crm_chatbot.utils.config import ESPOCRM_CONFIG

import httpx

http_client = httpx.Client(
    base_url=ESPOCRM_CONFIG["base_url"],
    auth=(ESPOCRM_CONFIG["username"], ESPOCRM_CONFIG["password"]),
    headers={"Content-Type": "application/json"},
    timeout=25.0
)