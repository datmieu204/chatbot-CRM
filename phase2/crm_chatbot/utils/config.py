# crm_chatbot/utils/config.py

import os
from dotenv import load_dotenv
load_dotenv()

GOOGLE_API_KEYS = [key for key in (
    os.environ.get("GOOGLEAI_API_KEY"),
    os.environ.get("GOOGLEAI_API_KEY_1"),
    os.environ.get("GOOGLEAI_API_KEY_2"),
    os.environ.get("GOOGLEAI_API_KEY_3"),
    os.environ.get("GOOGLEAI_API_KEY_4"),
) if key]

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

PROVIDER_CONFIG = {
    "google": {
        "api_keys": GOOGLE_API_KEYS,       
        "model": "gemini-1.5-flash",
        "embed_model": "models/gemini-embedding-001"       
    },
    "openai": {
        "api_keys": [OPENAI_API_KEY],       
        "model": "gpt-4o-mini",
        "embed_model": "text-embedding-3-large"   
    }
}

ESPOCRM_CONFIG = {
    "base_url": os.environ.get("ESPOCRM_URL"),
    "username": os.environ.get("ESPOCRM_USERNAME"),
    "password": os.environ.get("ESPOCRM_PASSWORD"),
}