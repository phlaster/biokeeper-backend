from typing import Annotated
from fastapi import Depends, Body, status
from fastapi.routing import APIRouter
from db_manager import DBM
from exceptions import NoKitException, HTTPNotFoundException,HTTPForbiddenException
from schemas import Identifier, TokenPayload
from utils import get_admin, get_current_user
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

@router.put('/kits/{kit_identifier}/set_owner')
def update_owner(
    kit_identifier: str,
    token_payload: Annotated[TokenPayload, Depends(get_admin)],
    new_owner_id: int = Body(...)
    
):
    validated_kit_identifier = Identifier(identifier=kit_identifier).identifier
    try:
        kit_info = DBM.kits.get_info(validated_kit_identifier)
    except NoKitException:
        raise HTTPNotFoundException(detail=f'Kit {validated_kit_identifier} not found')     
    if kit_info['creator_id']!= token_payload.id:
        raise HTTPForbiddenException(detail=f'User {token_payload.id} is not creator of kit {validated_kit_identifier}')
    
    if kit_info['owner_id'] is not None:
        raise HTTPForbiddenException(detail=f'Kit {validated_kit_identifier} already has owner')
    DBM.kits.change_owner(kit_info['id'], new_owner_id, log=True)
    return JSONResponse(status_code=status.HTTP_200_OK, content=f"Kit {validated_kit_identifier} owner changed to {new_owner_id}")
    


@router.post('/kits')
def create_kit(n_qrs: int, token_payload: Annotated[TokenPayload, Depends(get_admin)]):
    return DBM.kits.new(n_qrs)