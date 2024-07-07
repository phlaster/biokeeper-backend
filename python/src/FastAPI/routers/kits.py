from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from db_manager import DBM
from exceptions import NoKitException, HTTPNotFoundException
from schemas import TokenPayload
from utils import get_current_user

from schemas import TokenPayload
from utils import get_current_user

router = APIRouter()

@router.get('/kits')
def get_kits(token_payload: Annotated[TokenPayload, Depends(get_current_user)]):
    return DBM.kits.get_all()

@router.get('/kits/{kit_id}')
def get_kit(kit_id, token_payload: Annotated[TokenPayload, Depends(get_current_user)]):
    try:
        dbm_kit = DBM.kits.get_info(kit_id)
    except NoKitException:
        raise HTTPNotFoundException(f'Kit {kit_id} not found')
    return dbm_kit

@router.post('/kits')
def create_kit(n_qrs: int, token_payload: Annotated[TokenPayload, Depends(get_current_user)]):
    return DBM.kits.new(n_qrs)