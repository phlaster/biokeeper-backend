from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from db_manager import DBM
from exceptions import NoKitException, HTTPNotFoundException
from schemas import Identifier, TokenPayload
from utils import get_admin, get_current_user

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

@router.post('/kits')
def create_kit(n_qrs: int, token_payload: Annotated[TokenPayload, Depends(get_admin)]):
    return DBM.kits.new(n_qrs)