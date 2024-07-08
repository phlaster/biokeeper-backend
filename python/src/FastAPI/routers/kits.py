from typing import Annotated
from fastapi import Depends, Body, status
from fastapi.routing import APIRouter
from db_manager import DBM
from exceptions import NoKitException, HTTPNotFoundException,HTTPForbiddenException,HTTPConflictException, NoUserException
from schemas import Identifier, TokenPayload
from utils import get_admin, get_current_user, get_volunteer_or_admin
from fastapi.responses import JSONResponse
from schemas import TokenPayload
from utils import get_current_user

router = APIRouter()

@router.get('/kits')
def get_kits(token_payload: Annotated[TokenPayload, Depends(get_current_user)]):
    return DBM.kits.get_all()

@router.get('/kits/{kit_identifier}')
def get_kit(kit_identifier: str, token_payload: Annotated[TokenPayload, Depends(get_current_user)]):
    validated_kit_identifier = Identifier(identifier=kit_identifier).identifier
    try:
        dbm_kit = DBM.kits.get_info(validated_kit_identifier)
    except NoKitException:
        raise HTTPNotFoundException(detail=f'Kit {validated_kit_identifier} not found')
    return dbm_kit

@router.put('/kits/{kit_identifier}/send')
def update_owner(
    kit_identifier: str,
    token_payload: Annotated[TokenPayload, Depends(get_admin)],
    new_owner_id: int
    
):
    validated_kit_identifier = Identifier(identifier=kit_identifier).identifier
    try:
        kit_info = DBM.kits.get_info(validated_kit_identifier)
    except NoKitException:
        raise HTTPNotFoundException(detail=f'Kit {validated_kit_identifier} not found')     

    try:
        new_owner_info = DBM.users.get_info(new_owner_id)
    except NoUserException:
        raise HTTPNotFoundException(detail=f'User {new_owner_id} not found')
    
    if new_owner_info['status'] != 'volunteer' and new_owner_info['status'] != 'admin':
        raise HTTPForbiddenException(detail=f'User {new_owner_id} is not volunteer or admin')

    if kit_info['creator_id']!= token_payload.id:
        raise HTTPForbiddenException(detail=f'User {token_payload.id} is not creator of kit {validated_kit_identifier}')
    
    if kit_info['owner_id'] is not None:
        raise HTTPConflictException(detail=f'Kit {validated_kit_identifier} already has owner')
    
    if kit_info['status'] == 'sent':
        raise HTTPConflictException(detail=f'Kit {validated_kit_identifier} already sent')
    
    DBM.kits.send_kit(kit_info['id'], new_owner_id, log=True)
    return JSONResponse(status_code=status.HTTP_200_OK, content=f"Kit {validated_kit_identifier} owner changed to {new_owner_id}")
    
@router.put('/kits/{kit_identifier}/activate')
def activate_kit(
    kit_identifier: str,
    token_payload: Annotated[TokenPayload, Depends(get_volunteer_or_admin)]
    
):
    validated_kit_identifier = Identifier(identifier=kit_identifier).identifier
    try:
        kit_info = DBM.kits.get_info(validated_kit_identifier)
    except NoKitException:
        raise HTTPNotFoundException(detail=f'Kit {validated_kit_identifier} not found')
    
    if kit_info['owner_id'] != token_payload.id:
        raise HTTPConflictException(detail=f'User {token_payload.id} is not an owner of kit {validated_kit_identifier}')
    
    if kit_info['status'] == 'activated':
        raise HTTPConflictException(detail=f'Kit {validated_kit_identifier} already activated')
    
    DBM.kits.activate(kit_info['id'], log=True)

    return JSONResponse(status_code=status.HTTP_200_OK, content=f"Kit {validated_kit_identifier} is activated")
    
@router.post('/kits')
def create_kit(n_qrs: int, token_payload: Annotated[TokenPayload, Depends(get_admin)]):
    return DBM.kits.new(n_qrs, token_payload.id, log=True)