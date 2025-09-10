# crm_chatbot/core/llm_client.py

import itertools
from typing import List, Optional, Tuple

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from crm_chatbot.utils.config import PROVIDER_CONFIG

class MultiLLMs:
   def __init__(self, provider: str, **kwargs):
      provider = provider.lower()  
      if provider not in PROVIDER_CONFIG:
         raise ValueError(f"Unsupported provider: {provider}")
      
      config = PROVIDER_CONFIG[provider]

      self.provider = provider
      self.api_keys = config["api_keys"]
      self.model = config["model"]
      self.embed_model = config["embed_model"]
      self.kwargs = kwargs
      self.key_cycle = itertools.cycle(self.api_keys)

   def get_llm_instance(self):
      api_key = next(self.key_cycle)
      if self.provider == "google":
         return ChatGoogleGenerativeAI(
            model=self.model, 
            api_key=api_key, 
            **self.kwargs
         )
      elif self.provider == "openai":
         return ChatOpenAI(
            model=self.model, 
            openai_api_key=api_key, 
            **self.kwargs
         )
      else:
         raise ValueError(f"Unsupported provider: {self.provider}")
      
   def get_embedding_instance(self):
      api_key = next(self.key_cycle)
      if self.provider == "google":
         return GoogleGenerativeAIEmbeddings(
            model=self.embed_model or "models/gemini-embedding-001",
            google_api_key=api_key
         )
      elif self.provider == "openai":
         return OpenAIEmbeddings(
            model=self.embed_model or "text-embedding-3-small",
            api_key=api_key
         )
      else:
         raise ValueError(f"Unsupported provider: {self.provider}")

   def invoke(self, messages: List[BaseMessage], **kwargs):
      llm = self.get_llm_instance()
      return llm.invoke(messages, **kwargs)

   async def ainvoke(self, messages: List[BaseMessage], **kwargs):
      llm = self.get_llm_instance()
      return await llm.ainvoke(messages, **kwargs)


class LLMClient:
   def __init__(self, provider: str = "google", temperature: float = 0.0, top_p: float = 0.9, **kwargs):
      self.multi_llms = MultiLLMs(provider, temperature=temperature, top_p=top_p, **kwargs)

   def invoke(
      self,
      user_message: str,
      system_message: str,
      chat_history: Optional[List[Tuple[str, str]]] = None,
   ) -> str:
      messages = []

      if system_message:
         messages.append(SystemMessage(content=system_message))

      if chat_history:
         for role, content in chat_history[-10:]:  
            if role == "user":
               messages.append(HumanMessage(content=content))
            elif role == "assistant":
               messages.append(AIMessage(content=content))

      messages.append(HumanMessage(content=user_message))

      response = self.multi_llms.invoke(messages=messages)

      return response.content
   
   def generate_response(
      self,
      user_message: str,
      system_prompt: str,
      chat_history: Optional[List[Tuple[str, str]]] = None,
   ) -> str:
      return self.invoke(
         user_message=user_message,
         system_message=system_prompt,
         chat_history=chat_history
      )

   def embed_query(self, text: str) -> List[float]:
      embedder = self.multi_llms.get_embedding_instance()
      return embedder.embed_query(text)
   
   def embed_documents(self, texts: List[str]) -> List[List[float]]:
      embedder = self.multi_llms.get_embedding_instance()
      return embedder.embed_documents(texts)
   

if __name__ == "__main__":
   # test chat
   llm_client = LLMClient(provider="openai", temperature=0.7)
   response = llm_client.generate_response(
      user_message="Hello, how are you?",
      system_prompt="You are a helpful assistant."
   )
   print(response)

   # test embedding
   emb = llm_client.embed_query("Tạo account mới cho VinGroup")
   print(f"Embedding vector length: {len(emb)}")


# Global instance
llm_client = LLMClient(provider="google", temperature=0.0, top_p=0.9)