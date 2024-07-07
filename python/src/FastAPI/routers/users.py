
from fastapi.routing import APIRouter
from db_manager import DBM
from fastapi import Body, Depends, status
from typing import Annotated, Any
from fastapi.responses import JSONResponse
from exceptions import NoUserException, HTTPNotFoundException
from schemas import TokenPayload
from utils import get_current_user


router = APIRouter()

@router.get('/users')
def get_users(token_payload: Annotated[TokenPayload, Depends(get_current_user)]):
    """
    Retrieves all users.
    Returns a dictionary containing information about all users.
    """
    # TODO: return not all information about user, hide something.
    return DBM.users.get_all()

@router.get('/users/{user_identifier}')
def get_user_by_id(user_identifier, token_payload: Annotated[TokenPayload, Depends(get_current_user)]):
    """
    Returns user information for the specified user_id.
    """
    try:
        dbm_user = DBM.users.get_info_by_id(user_identifier)
    except NoUserException:
        raise HTTPNotFoundException(details=f'User {user_identifier} not found')
    return dbm_user

