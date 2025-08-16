# phase2/sprint1/example_script.py

from phase2.sprint1.llm_client.openai_client import OpenAIClient
from phase2.sprint1.llm_client.gemini_client import GeminiClient
from phase2.sprint1.llm_client.apikey_manager import APIKeys

from phase2.sprint1.schema.schema import CreateLeadSchema
from phase2.sprint1.utils.file_helper import load_prompt, load_schema

provider = "openai"
model = "gpt-4o-mini"

schema_function = load_schema("phase2/sprint1/schema/schema_create_lead.json")

prompt = load_prompt("phase2/sprint1/prompt/prompt_create_lead.md")

user_input = input("User: ")

prompt = prompt + "\n" + user_input

if provider == "openai":
    key_manager = APIKeys("OPENAI_API_KEY")
    client = OpenAIClient(model=model, key_manager=key_manager, schema=CreateLeadSchema)
else:
    key_manager = APIKeys("GEMINI_API_KEY")
    client = GeminiClient(model=model, key_manager=key_manager, schema=CreateLeadSchema)

result = client.run_with_retry(prompt=prompt, schema=schema_function)

if __name__ == "__main__":
    # print(result)
    # Mock API Test
    conversation = prompt
    lead = None

    while True:
        user_input = input("User: ")

        if user_input.lower() in ["exit", "quit"]:
            break

        conversation += "\nUser: " + user_input

        result = client.run_with_retry(prompt=conversation, schema=schema_function)

        print("Assistant:", result)

        lead = result




