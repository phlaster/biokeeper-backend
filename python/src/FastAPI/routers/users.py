
from fastapi.routing import APIRouter
from pydantic import ValidationError
from db_manager import DBM
from fastapi import Body, Depends, HTTPException, Path, status
from typing import Annotated, Any
from fastapi.responses import JSONResponse
from exceptions import NoUserException, HTTPNotFoundException
from schemas.common import TokenPayload
from schemas.users import GetUserRequest, UserResponse
from schemas.kits import MyKit
from schemas.samples import MySample
from schemas.researches import MyResearch
from utils import get_current_user

from dependencies.identifiers_validators import user_identifier_validator_dependency

router = APIRouter(tags=['users'])

@router.get('/users', response_model=list[UserResponse])
def get_users(token_payload: Annotated[TokenPayload, Depends(get_current_user)]):
    users = list(DBM.users.get_all().values())
    return JSONResponse(status_code=status.HTTP_200_OK, content=users)


    

@router.get('/users/{user_identifier}', response_model=UserResponse)
def get_user_by_identifier(token_payload: Annotated[TokenPayload, Depends(get_current_user)], user_identifier: Annotated[str, Depends(user_identifier_validator_dependency)]):
    """
    Returns user information for the specified user_id.
    """
    try:
        dbm_user = DBM.users.get_info(user_identifier)
    except NoUserException:
        raise HTTPNotFoundException(detail=f"User {user_identifier} not found")
    return JSONResponse(status_code=status.HTTP_200_OK, content=dbm_user)

@router.get('/users/me/kits', response_model=list[MyKit])
def get_user_kits(token_payload: Annotated[TokenPayload, Depends(get_current_user)]):
    return JSONResponse(status_code=status.HTTP_200_OK, 
                        content=DBM.kits.get_kits_by_user_identifier(token_payload.id))

@router.get('/users/me/samples', response_model=list[MySample])
def get_user_samples(token_payload: Annotated[TokenPayload, Depends(get_current_user)]):
    return JSONResponse(status_code=status.HTTP_200_OK, 
                        content=DBM.samples.get_samples_by_user_identifier(token_payload.id))

@router.get('/users/me/researches', response_model=list[MyResearch])
def get_user_researches(token_payload: Annotated[TokenPayload, Depends(get_current_user)]):
    return JSONResponse(status_code=status.HTTP_200_OK, 
                        content=DBM.researches.get_researches_by_user_identifier(token_payload.id))

