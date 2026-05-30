from pydantic import BaseModel, EmailStr, Field
from enum import Enum

class OTPPurpose(str, Enum):
    REGISTRATION = "REGISTRATION"
    FORGOT_PASSWORD = "FORGOT_PASSWORD"
    LOGIN_VERIFICATION = "LOGIN_VERIFICATION"

class Login(BaseModel):
    email: EmailStr = Field(..., strict=True)
    password: str = Field(..., strict=True, min_length=8)

class SendOTPRequest(BaseModel):
    email: EmailStr = Field(..., strict=True)
    purpose: OTPPurpose = Field(..., description="Purpose of OTP: REGISTRATION, FORGOT_PASSWORD, or LOGIN_VERIFICATION")

class SendOTPResponse(BaseModel):
    message: str
    email: str
    purpose: str

class VerifyOTPRequest(BaseModel):
    email: EmailStr = Field(..., strict=True)
    otp: str = Field(..., strict=True, min_length=6, max_length=6, pattern="^\d{6}$")
    purpose: OTPPurpose = Field(..., description="Purpose of OTP: REGISTRATION, FORGOT_PASSWORD, or LOGIN_VERIFICATION")

class VerifyOTPResponse(BaseModel):
    message: str
    email: str
    verified: bool