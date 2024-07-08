from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from db_manager import DBM
from datetime import datetime
from exceptions import HTTPConflictException, HTTPNotFoundException, NoSampleException, HTTPForbiddenException, NoResearchException, NoQrCodeException
from schemas import TokenPayload
from utils import get_current_user, get_volunteer_or_admin, is_admin, is_observer

router = APIRouter()


@router.get('/samples')
def get_samples(token_payload: Annotated[TokenPayload, Depends(get_current_user)]):
    # TODO: return not all information about sample, hide something.
    # Is this endpoint really needed?
    return DBM.samples.get_all()

@router.get('/samples/{sample_id}')
def get_sample(sample_id: int, token_payload: Annotated[TokenPayload, Depends(get_current_user)]):
    try:
        dbm_sample = DBM.samples.get_info(sample_id)
    except NoSampleException:
        raise HTTPNotFoundException(detail=f'Sample {sample_id} not found')
    if not is_admin(token_payload) and dbm_sample['owner_id'] != token_payload.id or is_observer(token_payload):
        raise HTTPForbiddenException(detail=f'Sample owner differs from autorized user')
    return dbm_sample

@router.post('/samples')
def create_sample(
    token_payload: Annotated[TokenPayload, Depends(get_volunteer_or_admin)],
    qr_hex: str,
    research_id: int,
    collected_at: datetime,
    gps: str,
    weather: str = None,
    user_comment: str = None,
    photo_hex_string: str = None
):
    try:
        dbm_research = DBM.researches.get_info(research_id)
    except NoResearchException:
        raise HTTPNotFoundException(detail=f'Research with id {research_id} not found')
    
    if dbm_research['approval_required']:
        user_researches = DBM.users.get_user_participated_researches(token_payload.id)
        if not dbm_research['id'] in user_researches:
            raise HTTPForbiddenException(detail=f"User {token_payload.id} does not participate in research {dbm_research['name']}")
        
    if not dbm_research['status'] != 'ongoing':
        raise HTTPConflictException(detail=f"Research {dbm_research['name']} is not in \"ongoing\" status.")

    try:
        dbm_qr_info = DBM.samples.get_qr_info(qr_hex)
    except NoQrCodeException:
        raise HTTPNotFoundException(detail=f'Qr {qr_hex} not found')

    if dbm_qr_info['is_used']:
        raise HTTPConflictException(detail=f'Qr {qr_hex} is already used')
    
    if not dbm_qr_info['kit_id']:
        raise HTTPConflictException(detail=f'Qr {qr_hex} is not assigned to any kit')
    
    try:
        dbm_kit = DBM.kits.get_info(dbm_qr_info['kit_id'])
    except NoQrCodeException:
        raise HTTPNotFoundException(detail=f'No kit with id {dbm_qr_info["kit_id"]} found (very strange).')
    
    if not dbm_kit['owner']:
        raise HTTPForbiddenException(detail=f'Kit {dbm_qr_info["kit_id"]} is not assigned to any user')
    
    if not dbm_kit['owner']['id'] == token_payload.id:
        raise HTTPForbiddenException(detail=f"User {token_payload.id} does not own kit {dbm_kit['id']}")
    
    if not dbm_kit['status'] == 'activated':
        raise HTTPConflictException(detail=f'Kit {dbm_kit["id"]} hasn\'t been activated')


    dbm_new_sample_id = DBM.samples.new(qr_id=int(dbm_qr_info['id']), 
                        research_id=int(dbm_research['id']), 
                        owner_id = int(token_payload.id),
                        collected_at=collected_at,
                        gps=gps,
                        weather=weather, 
                        user_comment=user_comment,
                        photo_hex_string = photo_hex_string,
                        log = False)
    return dbm_new_sample_id
        
    