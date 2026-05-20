from fastapi import APIRouter
from ..schemas.auth_schema import Login
from ..services.auth_service import userLogin

router = APIRouter(
    prefix="/login", 
    tags=["User Authentication"]
)

@router.post("/")
async def user_login(login: Login):
    return await userLogin(login)
    