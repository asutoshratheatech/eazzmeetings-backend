from datetime import datetime
from typing import Optional
from beanie import Document, Link, PydanticObjectId
from pydantic import Field

from app.schemas import UserBase,DBMeta


class UserCollection(UserBase,DBMeta,Document):
    org_id: Optional[PydanticObjectId] = None
    
    
    class settings:
        name = "users"


class UserSecretsCollection(DBMeta,Document):
    user_id: PydanticObjectId
    password_hash: str 
    huggingface_api_key_hash: Optional[str]=Field(None)
    openai_api_key_hash: Optional[str]=Field(None)
    mistral_api_key_hash: Optional[str]=Field(None)
    groq_api_key_hash: Optional[str]=Field(None)
    gemini_api_key_hash: Optional[str]=Field(None)
    
    class settings:
        name = "user_secrets"
    

    