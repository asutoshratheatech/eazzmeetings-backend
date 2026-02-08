from typing import Optional, Tuple
from beanie import PydanticObjectId
from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    username: str
    full_name: Optional[str ]= Field(None)
    email: Optional[EmailStr]= Field(None)
    phone: Optional[Tuple[int, Optional[int]]]= Field(None)
    
    is_active: bool= Field(True)

class UserInDB(UserBase):
    password: str

class UserOut(UserBase):
    id: PydanticObjectId


class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str

