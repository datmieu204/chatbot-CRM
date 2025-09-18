# crm_chatbot/graph/state.py

from typing import TypedDict, Dict, Any

class ChatbotState(TypedDict):
    query: str
    domains: Dict[str, Any]
    action_map: Dict[str, Any]
    chosen_agent: str
    answer: str
