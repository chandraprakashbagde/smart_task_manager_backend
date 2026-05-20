from pydantic import BaseModel, EmailStr, Field

class Login(BaseModel):
    email: EmailStr = Field(..., strict=True)
    password: str = Field(..., strict=True, min_length=8)