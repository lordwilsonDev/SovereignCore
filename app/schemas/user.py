from pydantic import BaseModel, EmailStr, ConfigDict

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    
    # V2 Config: 'orm_mode' is renamed to 'from_attributes'
    model_config = ConfigDict(from_attributes=True)
