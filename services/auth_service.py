from repositories.user_repository import get_user_by_email
from utils.response_handler import SuccessResp, FieldErrorResp
from utils.password_handler import pwd_cntxt
from utils.token import generate_token

async def userLogin(crendetials):
    
    user = await get_user_by_email(crendetials.email)

    if user == None:
        return FieldErrorResp(
            field="email",
            message="User not found with this email"
        )

    if pwd_cntxt.verify(crendetials.password, user["password"]) != True:
        return FieldErrorResp(
            field="password",
            message="Incorrect Password."
        )

    user['created_at'] = user["created_at"].isoformat()
    user['updated_at'] = user["updated_at"].isoformat()

    return SuccessResp(
            message="User logged in successfully.",
            data={ "token": generate_token(userid=user["user_id"], email=user["email"])}
        )