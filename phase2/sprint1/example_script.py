# phase2/sprint1/example_script.py

import re
import logging
import json

from phase2.sprint1.llm_client.openai_client import OpenAIClient
from phase2.sprint1.llm_client.gemini_client import GeminiClient
from phase2.sprint1.llm_client.apikey_manager import APIKeys
from phase2.sprint1.schemas.schema import CreateLeadSchema, CreateAccountSchema
from phase2.sprint1.utils.file_helper import load_prompt, load_tools

logging.basicConfig(level=logging.INFO,
format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

provider = "openai"
model = "gpt-4o-mini"

if provider == "openai":
    key_manager = APIKeys("OPENAI_API_KEY")
    client = OpenAIClient(model=model, key_manager=key_manager)
else:
    key_manager = APIKeys("GEMINI_API_KEY")
    client = GeminiClient(model=model, key_manager=key_manager)

def mock_crm_api_call(tool_name: str, data: dict):
    print(f"Mock CRM API Call - Tool: {tool_name}, Data: {data}")
    return {"status": "success", "data": data}

def extract_json(text: str):
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
    return None

def chatbot():
    tools = load_tools("phase2/sprint1/schemas/lead")

    tool_schema_map = {
        "create_lead": CreateLeadSchema,
        "create_account": CreateAccountSchema
    }

    create_lead_prompt = load_prompt("phase2/sprint1/prompts/lead/prompt_create_lead.md")

    conversation_state = {
        "tool_name": "create_lead",   
        "data": {},
        "status": "incomplete"       
    }

    conversation_history = []

    while True:
        user_input = input("User: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        conversation_history.append({"role": "user", "content": user_input})

        try:
            full_prompt = f"""{create_lead_prompt}
                Current state: {conversation_state}
                User input: {user_input}"""

            response = client.generate(
                prompt=full_prompt,
                tools=tools
            )

            response_data = extract_json(response)

            if not response_data:
                # fallback:
                print("Assistant:", response)
                conversation_history.append({"role": "assistant", "content": response})
                continue

            tool_name = response_data.get("tool_name", conversation_state["tool_name"])
            status = response_data.get("status", "incomplete")
            data = response_data.get("data", {})

            conversation_state["tool_name"] = tool_name
            conversation_state["data"].update({k: v for k, v in data.items() if v})
            conversation_state["status"] = status

            if status == "incomplete":
                missing = response_data.get("missing_fields", [])
                print(f"Assistant: I still need {', '.join(missing)}. Can you provide?")
                continue

            elif status == "asking_optional":
                optional = response_data.get("optional_fields", [])
                print(f"Assistant: Do you want to add {', '.join(optional)}? (yes/no)")
                continue

            elif status == "ready":
                schema_cls = tool_schema_map.get(tool_name)
                if not schema_cls:
                    print("Assistant: Unknown tool, cannot proceed.")
                    continue

                try:
                    validated = schema_cls(**conversation_state["data"])
                except Exception as e:
                    print(f"Assistant: Validation failed: {e}")
                    continue

                api_response = mock_crm_api_call(tool_name, validated.model_dump())
                print("Assistant:", api_response)

                conversation_state = {
                    "tool_name": "create_lead",
                    "data": {},
                    "status": "incomplete"
                }

            else:
                print("Assistant:", response)

        except Exception as e:
            print(f"Error: {e}")
            logger.error(f"Error during processing: {str(e)}", exc_info=True)


if __name__ == "__main__":
    chatbot()
