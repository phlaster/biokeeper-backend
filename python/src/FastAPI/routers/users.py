
from fastapi.routing import APIRouter
from db_manager import DBM
from fastapi import Body, Depends, status
from typing import Annotated, Any
from fastapi.responses import JSONResponse
from exceptions import NoUserException, HTTPNotFoundException
from schemas import Identifier, TokenPayload
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
def get_user_by_identifier(user_identifier: str, token_payload: Annotated[TokenPayload, Depends(get_current_user)]):
    validated_user_identifier = Identifier(identifier=user_identifier).identifier
    """
    Returns user information for the specified user_id.
    """
    try:
        dbm_user = DBM.users.get_info(validated_user_identifier)
    except NoUserException:
        raise HTTPNotFoundException(detail=f'User {validated_user_identifier} not found')
    return dbm_user

