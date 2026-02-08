from langchain_groq import ChatGroq
from langchain_mistralai import ChatMistralAI

from app.env_settings import env

class LLMService:
    def __init__(self):
        self.groq_client = ChatGroq(api_key=env.GROQ_API_KEY)
        self.mistral_client = ChatMistralAI(api_key=env.MISTRAL_API_KEY)
    