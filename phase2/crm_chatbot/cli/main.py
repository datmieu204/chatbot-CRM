# crm_chatbot/cli/main.py

from crm_chatbot.core.config_loader import load_action_map, load_all_domains
from crm_chatbot.graph.builder import build_workflow

def run_cli():
    domains = load_all_domains()
    action_map = load_action_map()
    workflow = build_workflow(domains, action_map)

    print("=== CRM Chatbot CLI ===")
    while True:
        query = input("User: ")
        if query.lower() in ["exit", "quit"]:
            break
        state = workflow.invoke({"query": query, "domains": domains, "action_map": action_map})
        print(f"Bot ({state['chosen_agent']}): {state['answer']}")

if __name__ == "__main__":
    run_cli()