# phase2/sprint1/example_script.py

import logging

from phase2.sprint1.llm_client.openai_client import OpenAIClient
from phase2.sprint1.llm_client.gemini_client import GeminiClient
from phase2.sprint1.llm_client.apikey_manager import APIKeys

from phase2.sprint1.schema.schema import CreateLeadSchema, CreateAccountSchema
from phase2.sprint1.utils.file_helper import load_prompt, load_tools, load_schema

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

provider = "openai"
model = "gpt-4o-mini"

TOOL_SCHEMAS = {
    "create_lead": CreateLeadSchema,
    "create_account": CreateAccountSchema
}

if provider == "openai":
    key_manager = APIKeys("OPENAI_API_KEY")
    client = OpenAIClient(model=model, key_manager=key_manager)
else:
    key_manager = APIKeys("GEMINI_API_KEY")
    client = GeminiClient(model=model, key_manager=key_manager)

def mock_crm_api_call(tool_name: str, data: dict):
    print(f"Mock CRM API Call - Tool: {tool_name}, Data: {data}")
    return {"status": "success", "data": data}

def chatbot():
    tools = load_tools("phase2/sprint1/schema")

    tool_names = [tool["function"]["name"] for tool in tools]
    
    tool_schema_map = {
        "create_lead": TOOL_SCHEMAS["create_lead"],
        "create_account": TOOL_SCHEMAS["create_account"]
    }

    conversation_history = []

    while True:
        user_input = input("User: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        conversation_history.append({"role": "user", "content": user_input})

        try:
            response = client.generate(
                prompt=user_input,
                tools=tools
            )
            
            if isinstance(response, str) and not response.strip().startswith('{'):
                # Regular text response
                print("Assistant:", response)
                conversation_history.append({"role": "assistant", "content": response})
                continue
            
            tool_name = None
            try:
                import json
                import re
                
                match = re.search(r"\{.*\}", response, re.DOTALL)
                if match:
                    json_str = match.group(0)
                    response_data = json.loads(json_str)
                    tool_name = response_data.get("tool_name")
            except json.JSONDecodeError:
                print("Assistant:", response)
                conversation_history.append({"role": "assistant", "content": response})
                continue
                
            if tool_name and tool_name in tool_schema_map:
                validated_response = client.parse_and_validate(response, tool_schema_map[tool_name])
                
                if isinstance(validated_response, str):
                    print("Assistant:", validated_response)
                    conversation_history.append({"role": "assistant", "content": validated_response})
                else:
                    # Process the tool call with the correct schema
                    if tool_name in tool_names:
                        tool_data = validated_response.dict() if hasattr(validated_response, 'dict') else validated_response
                        api_response = mock_crm_api_call(tool_name, tool_data)
                        print("Assistant:", api_response)
                        conversation_history.append({"role": "assistant", "content": str(api_response)})
                    else:
                        print("Assistant: Invalid tool name provided.")
            else:
                # No tool name found or invalid tool, treat as text response
                print("Assistant:", response)
                conversation_history.append({"role": "assistant", "content": response})
                
        except Exception as e:
            print(f"Error: {e}")
            logger.error(f"Error during processing: {str(e)}", exc_info=True)

if __name__ == "__main__":
    chatbot()


