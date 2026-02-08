
from datetime import datetime
from typing import Optional, TypedDict
from beanie import PydanticObjectId
from pydantic import BaseModel


class DBMeta(BaseModel):
    org_id: PydanticObjectId
    created_on: datetime = datetime.now()
    updated_on: datetime = datetime.now()
    updated_by: Optional[PydanticObjectId]=None
    updated_by: Optional[PydanticObjectId]=None

class UserJWT(TypedDict):
    """
    sub is UserCollection._id

    exp is the token expiry time
    
    ...everything else is self explanatory
    """
    sub:Optional[str]=None 
    user_name:Optional[str]=None
    user_email:Optional[str]=None
    role_name:Optional[str]=None
    org_id:Optional[str]=None
    exp:Optional[int]=None
