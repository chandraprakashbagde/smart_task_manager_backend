from fastapi import APIRouter
from schemas.auth_schema import Login, SendOTPRequest, VerifyOTPRequest
from services.auth_service import userLogin, send_otp_service, verify_otp_service

router = APIRouter(
    prefix="/auth", 
    tags=["Authentication"]
)

@router.post("/login")
async def user_login(login: Login):
    """
    User login endpoint.
    Returns JWT token on successful authentication.
    """
    return await userLogin(login)

@router.post("/send-otp")
async def send_otp(request: SendOTPRequest):
    return await send_otp_service(request)

@router.post("/verify-otp")
async def verify_otp(request: VerifyOTPRequest):
    return await verify_otp_service(request)
    