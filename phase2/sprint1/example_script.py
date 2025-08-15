# phase2/sprint1/example_script.py

from phase2.sprint1.llm_client.openai_client import OpenAIClient
from phase2.sprint1.llm_client.gemini_client import GeminiClient
from phase2.sprint1.llm_client.apikey_manager import APIKeys

from phase2.sprint1.schema.schema import CreateLeadSchema

provider = "openai"
model = "gpt-4o-mini"

schema_function = {
    "name": "create_lead",
    "description": "Any new lead that is created in the CRM",
    "parameters": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "The name of the lead"
            },
            "email": {
                "type": "string",
                "format": "email",
                "description": "The email address of the lead"  
            },
            "phone": {
                "type": ["string", "null"],
                "description": "The phone number of the lead"
            },
            "company": {
                "type": ["string", "null"],
                "description": "The company of the lead"
            },
            "notes": {
                "type": ["string", "null"],
                "description": "Any additional notes about the lead"
            }
        },
        "required": ["name", "email", "phone", "company", "notes"], 
        "additionalProperties": False
    },
    "strict": True
}

prompt = """
You are an assistant of a CRM system. Your task is to help users create new leads by providing the necessary information and guidance.
Return a JSON following the lead_schema, do not include any additional information or context.
If the user provides all the required information, create the lead. If any information is missing, prompt the user to provide the missing information.
"""

user_input = input("Please provide the lead information in JSON format: ")

prompt = prompt + "\n" + user_input

if provider == "openai":
    key_manager = APIKeys("OPENAI_API_KEY")
    client = OpenAIClient(model=model, key_manager=key_manager, schema=CreateLeadSchema)
else:
    key_manager = APIKeys("GEMINI_API_KEY")
    client = GeminiClient(model=model, key_manager=key_manager, schema=CreateLeadSchema)

result = client.run_with_retry(prompt=prompt, schema=schema_function)

if __name__ == "__main__":
    print(result)
    # Mock API Test
