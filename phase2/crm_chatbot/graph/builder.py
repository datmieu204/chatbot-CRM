# crm_chatbot/graph/builder.py

from typing import Dict, Any, List
from langgraph.graph import StateGraph, END

from crm_chatbot.graph.state import ChatbotState
from crm_chatbot.graph.nodes import router_node, domain_node

def create_domain_agent_node(domain_name: str):
    def domain_agent_node(state: ChatbotState) -> Dict[str, Any]:
        return domain_node({**state, "chosen_agent": domain_name})
    return domain_agent_node

def build_workflow(domains, action_map):
    if domains:
        workflow = StateGraph(ChatbotState)
        workflow.add_node("router", router_node)

        domain_node_map = {}

        for name in domains.keys():
            workflow.add_node(name, create_domain_agent_node(name))
            domain_node_map[name] = name

        workflow.set_entry_point("router")
        workflow.add_conditional_edges("router", lambda state: state["chosen_agent"], domain_node_map)

        for name in domains.keys():
            workflow.add_edge(name, END)

        return workflow.compile()
