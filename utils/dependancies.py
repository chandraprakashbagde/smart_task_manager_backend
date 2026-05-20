
from utils.token import verify_token
from fastapi import HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from utils.response_handler import FieldErrorResp

security = HTTPBearer(auto_error=False)

async def validate_user(credentials: HTTPAuthorizationCredentials = Depends(security)):

    if credentials is None:
        
        raise HTTPException(
            status_code=422,
            detail=FieldErrorResp(
                field="missing_token",
                message="Authentication required.",
                jsnorsp=False
            )
        )               
    
    try:

        token = credentials.credentials

        userinfo = verify_token(token)

        if userinfo is None:
            raise HTTPException(
                status_code=422,
                detail=FieldErrorResp(
                    field="token_expired",
                    message="Session Expired!",
                    jsnorsp=False
                )
            )

        return userinfo
        
    except HTTPException as e:
        raise e

    except Exception:
        raise HTTPException(
            status_code=422,
            detail="Authentication failed"
        )