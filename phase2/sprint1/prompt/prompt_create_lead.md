# Prompt: Create Lead

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

### Example:
User: create a new lead with name John and email john@example.com and phone 123456  
Assistant:  
{
  "name": "John",
  "email": "john@example.com",
  "phone": "123456",
  "company": null,
  "notes": null
}