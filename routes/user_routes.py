from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, Request, Query
from schemas.user_schema import CreateUser, UpdateUser
from services.user_service import get_all, create, update, fetch_profile, delete
from utils.dependancies import validate_user

router = APIRouter(
    prefix="/user",
    tags=["User Management"],
    dependencies=[Depends(validate_user)]
)

@router.get("/")
async def get_all_users(
    request:Request,
    searchColumns: List[str] = Query(default=[]),
    searchValue: str = "",
    limit: int = 10,
    offset: int = 0,
    sortByColumn: Optional[str] = "updated_at",
    order: Optional[str] = "desc"
):
    req = {
        **dict(request.query_params),
        "searchColumns": request.query_params.getlist("searchColumns")
    }
    return await get_all(req)

@router.get("/fetch_profile")
async def get_user(user: Dict = Depends(validate_user)):
    return await fetch_profile(user["userid"])

@router.post("/")
async def create_user(body: CreateUser):
    return await create(body)

@router.put("/{user_id}")
async def update_user(user_id:int, body: UpdateUser):
    return await update(user_id, body)

@router.delete("/{user_id}")
async def delete_user(user_id: int):
    return await delete(user_id)