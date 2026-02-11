from langchain_groq import ChatGroq
from langchain_mistralai import ChatMistralAI

from app.env_settings import env

class LLMService:
    def __init__(self):
        # Centralized Model Setting
        self.model_name = "llama-3.3-70b-versatile" 
        # self.model_name = "meta-llama/llama-4-maverick-17b-128e-instruct"
        
        self.groq_client = ChatGroq(api_key=env.GROQ_API_KEY, model=self.model_name)
        # self.mistral_client = ChatMistralAI(api_key=env.MISTRAL_API_KEY, model="mistral-large-latest")
    
