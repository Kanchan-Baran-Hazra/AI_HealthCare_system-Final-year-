from pydantic import BaseModel, EmailStr, ConfigDict,Field
from datetime import datetime
import uuid
from enum import Enum
from datetime import date
from typing import Optional


class GenderEnum(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"

# Schema for incoming registration request
class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    dob: Optional[date] = None
    gender: Optional[GenderEnum] = None
    phone_number: Optional[str] = Field(default=None) # E.164 phone format validation


# Schema for returning user information (Hides sensitive fields)
class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    # username: str
    is_active: bool
    created_at: datetime

    # Config to support converting ORM/SQLAlchemy objects to Pydantic responses
    model_config = ConfigDict(from_attributes=True)




# Schema for incoming login request
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"