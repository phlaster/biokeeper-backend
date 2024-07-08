from typing import Annotated
from fastapi import Depends, Body, status
from fastapi.routing import APIRouter
from db_manager import DBM
from exceptions import NoKitException, HTTPNotFoundException,HTTPForbiddenException,HTTPConflictException, NoUserException
from schemas.common import Identifier, TokenPayload
from schemas.kits import CreateKitRequest, KitInfo, KitRequest, SendKitRequest
from utils import get_admin, get_current_user, get_volunteer_or_admin
from fastapi.responses import JSONResponse, Response
from schemas.common import TokenPayload
from utils import get_current_user

router = APIRouter()

@router.get('/kits', response_model=list[KitInfo])
def get_kits(token_payload: Annotated[TokenPayload, Depends(get_current_user)]):
    return JSONResponse(status_code=status.HTTP_200_OK, content=DBM.kits.get_all())

@router.get('/kits/{kit_identifier}', response_model=KitInfo)
def get_kit(kit_request: KitRequest, token_payload: Annotated[TokenPayload, Depends(get_current_user)]):
    kit_identifier = kit_request.kit_identifier
    try:
        dbm_kit = DBM.kits.get_info(kit_identifier)
    except NoKitException:
        raise HTTPNotFoundException(detail=f'Kit {kit_identifier} not found')
    return JSONResponse(status_code=status.HTTP_200_OK, content=dbm_kit)

@router.put('/kits/{kit_identifier}/send')
def update_owner(
    token_payload: Annotated[TokenPayload, Depends(get_admin)],
    send_kit_request: SendKitRequest
    ):
    kit_identifier = send_kit_request.kit_identifier
    new_owner_identifier = send_kit_request.new_owner_identifier
    try:
        kit_info = DBM.kits.get_info(kit_identifier)
    except NoKitException:
        raise HTTPNotFoundException(detail=f'Kit {kit_identifier} not found')     

    try:
        new_owner_info = DBM.users.get_info(new_owner_identifier)
    except NoUserException:
        raise HTTPNotFoundException(detail=f'User {new_owner_identifier} not found')
    
    new_owner_id = new_owner_info['id']
    
    if new_owner_info['status'] != 'volunteer' and new_owner_info['status'] != 'admin':
        raise HTTPForbiddenException(detail=f'User {new_owner_id} is not volunteer or admin')

    if kit_info['creator_id']!= token_payload.id:
        raise HTTPForbiddenException(detail=f'User {token_payload.id} is not creator of kit {kit_identifier}')
    
    if kit_info['owner_id'] is not None:
        raise HTTPConflictException(detail=f'Kit {kit_identifier} already has owner')
    
    if kit_info['status'] == 'sent':
        raise HTTPConflictException(detail=f'Kit {kit_identifier} already sent')
    
    DBM.kits.send_kit(kit_info['id'], new_owner_id, log=True)
    return Response(status_code=status.HTTP_200_OK, content=f"Kit {kit_identifier} owner changed to {new_owner_id}")
    
@router.put('/kits/{kit_identifier}/activate')
def activate_kit(
    kit_request: KitRequest,
    token_payload: Annotated[TokenPayload, Depends(get_volunteer_or_admin)]
    ):
    kit_identifier = kit_request.kit_identifier
    try:
        kit_info = DBM.kits.get_info(kit_identifier)
    except NoKitException:
        raise HTTPNotFoundException(detail=f'Kit {kit_identifier} not found')
    
    if kit_info['owner_id'] != token_payload.id:
        raise HTTPConflictException(detail=f'User {token_payload.id} is not an owner of kit {kit_identifier}')
    
    if kit_info['status'] == 'activated':
        raise HTTPConflictException(detail=f'Kit {kit_identifier} already activated')
    
    DBM.kits.activate(kit_info['id'], log=True)

    return Response(status_code=status.HTTP_200_OK, content=f"Kit {kit_identifier} is activated")
    
@router.post('/kits', response_model=KitInfo)
def create_kit(create_kit_request: CreateKitRequest, token_payload: Annotated[TokenPayload, Depends(get_admin)]):
    kit_id = DBM.kits.new(create_kit_request.n_qrs, token_payload.id, log=True)
    kit_info = DBM.kits.get_info(kit_id)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=kit_info)