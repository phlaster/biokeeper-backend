
from fastapi.routing import APIRouter
from db_manager import DBM
from fastapi import Body, Depends, status
from typing import Annotated, Any
from fastapi.responses import JSONResponse
from exceptions import NoUserException, HTTPNotFoundException
from schemas.common import TokenPayload
from schemas.users import GetUserRequest, UserResponse
from utils import get_current_user

router = APIRouter()

@router.get('/users', response_model=list[UserResponse])
def get_users(token_payload: Annotated[TokenPayload, Depends(get_current_user)]):
    users = content=DBM.users.get_all()
    return JSONResponse(status_code=status.HTTP_200_OK, content=users)

@router.get('/users/{user_identifier}', response_model=UserResponse)
def get_user_by_identifier(get_user_request: GetUserRequest, token_payload: Annotated[TokenPayload, Depends(get_current_user)]):
    user_identifier = get_user_request.user_identifier
    """
    Returns user information for the specified user_id.
    """
    try:
        dbm_user = DBM.users.get_info(user_identifier)
    except NoUserException:
        raise HTTPNotFoundException(detail=f'User {user_identifier} not found')
    return JSONResponse(status_code=status.HTTP_200_OK, content=dbm_user)

