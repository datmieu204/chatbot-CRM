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
                "type": ["string"],
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
You are an AI CRM assistant.  
Your task is to collect and validate lead information step by step.  

### Rules:
1. Always return a valid JSON object strictly following the schema.
2. Required fields: name, email, phone.
3. Optional fields: company, notes.
4. If a required field is missing → ask user for it.
5. If required fields are complete but optional fields are missing → politely ask if the user wants to add them.
6. If user says "yes", update the JSON with their input in the correct field.
7. If user says "no", finalize the JSON.
8. Do not include any text outside the JSON object. Return only the JSON object.
  
### Schema:
{
  "name": string | null,
  "email": string | null,
  "phone": string | null,
  "company": string | null,
  "notes": string | null
}
"""

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




