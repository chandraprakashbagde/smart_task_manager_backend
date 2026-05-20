from ..repositories.user_repository import get_user_by_email, create_user, update_user, get_all_users, get_user_by_id,delete_user
from ..utils.response_handler import SuccessResp, FieldErrorResp, ErrorResp
from ..utils.password_handler import pwd_cntxt

async def get_all(request):
    
    users = await get_all_users(request)

    return SuccessResp( data=users)

async def create(body):
    user = await get_user_by_email(body.email)
    
    if user is not None:
        return FieldErrorResp(
            field="email",
            message="Email already exists"
        )
    
    ## Hashing a password
    hashedpass = pwd_cntxt.hash(body.password)
    body.password = hashedpass
    lastrowid = await create_user(body) 

    return SuccessResp(
            data={"lastrowid":lastrowid},
            message="User created successfully"
        )

async def update(user_id,body):
    updatedUser = await update_user(user_id, body)
    updatedUser['created_at'] = updatedUser["created_at"].isoformat()
    updatedUser['updated_at'] = updatedUser["updated_at"].isoformat()

    del updatedUser["password"]
    return SuccessResp(
            data=updatedUser,
            message="User updated successfully."
        )

async def fetch_profile(user_id):
    user = await get_user_by_id(user_id)
    return SuccessResp(data=user)

async def delete(user_id):
    rouwcount =  await delete_user(user_id)

    if rouwcount == 0:
        return ErrorResp(
            message="User not found."
        )

    return SuccessResp(
        data=[],
        message="User deleted successfully."
    )