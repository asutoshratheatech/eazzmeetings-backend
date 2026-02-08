from beanie import Document
from app.schemas.common_schema import DBMeta
from pydantic import BaseModel

class IdentityBase(BaseModel):
    pass

class IdentityCollection(IdentityBase, DBMeta,Document):
    
    class settings:
        name = "identities"

class IdentityEmbeddingCollection(DBMeta,Document):
    
    class settings:
        name = "identity_embeddings"
