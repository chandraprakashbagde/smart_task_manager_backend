from pydantic import BaseModel, EmailStr, Field, model_validator
from enum import Enum
from utils.error_handler import custome_validation_error

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
    otp: str = Field(..., strict=True, min_length=6, max_length=6, pattern=r"^\d{6}$")
    purpose: OTPPurpose = Field(..., description="Purpose of OTP: REGISTRATION, FORGOT_PASSWORD, or LOGIN_VERIFICATION")

class VerifyOTPResponse(BaseModel):
    message: str
    email: str
    verified: bool

class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(..., strict=True)

class VerifyForgotPasswordOTPRequest(BaseModel):
    email: EmailStr = Field(..., strict=True)
    otp: str = Field(..., strict=True, min_length=6, max_length=6, pattern=r"^\d{6}$")

class ResetPasswordRequest(BaseModel):
    token: str = Field(..., strict=True)
    new_password: str = Field(..., strict=True, min_length=8)
    confirm_password: str = Field(..., strict=True, min_length=8)

    @model_validator(mode="after")
    def validate(cls, values):
        if values.confirm_password != values.new_password:
            raise custome_validation_error("confirm_password", "Passwords do not match")
        return values