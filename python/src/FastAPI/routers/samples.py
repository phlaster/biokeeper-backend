from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from db_manager import DBM
from datetime import datetime
from exceptions import HTTPNotFoundException, NoSampleException
from schemas import TokenPayload
from utils import get_current_user

router = APIRouter()


@router.get('/samples')
def get_samples(token_payload: Annotated[TokenPayload, Depends(get_current_user)]):
    return DBM.samples.get_all()

@router.get('/samples/{sample_id}')
def get_sample(sample_id, token_payload: Annotated[TokenPayload, Depends(get_current_user)]):
    try:
        dbm_sample = DBM.samples.get_info(sample_id)
    except NoSampleException:
        raise HTTPNotFoundException(f'Sample {sample_id} not found')
    return dbm_sample

@router.post('/samples')
def create_sample(
    token_payload: Annotated[TokenPayload, Depends(get_current_user)],
    qr_hex: str,
    research_name: str,
    collected_at: datetime,
    gps: str,#tuple[float, float],
    weather: str = None,
    user_comment: str = None,
    photo_hex: str = None
):
    return DBM.samples.new(bytes.fromhex(qr_hex), research_name, collected_at, gps, weather, user_comment, bytes.fromhex(photo_hex))