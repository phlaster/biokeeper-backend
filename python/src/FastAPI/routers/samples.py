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
def get_sample(sample_id, token_payload: Annotated[TokenPayload, Depends(get_current_user)]):
    try:
        dbm_sample = DBM.samples.get_info(sample_id)
    except NoSampleException:
        raise HTTPNotFoundException(details=f'Sample {sample_id} not found')
    if not is_admin(token_payload) and dbm_sample['owner_id'] != token_payload.id or is_observer(token_payload):
        raise HTTPForbiddenException(details=f'Sample owner differs from autorized user')
    return dbm_sample

@router.post('/samples')
def create_sample(
    token_payload: Annotated[TokenPayload, Depends(get_volunteer_or_admin)],
    qr_hex: str,
    research_name: str,
    collected_at: datetime,
    gps: str,
    weather: str = None,
    user_comment: str = None,
    photo_hex_string: str = None
):
    try:
        dbm_research = DBM.researches.get_info(research_name)
    except NoResearchException:
        raise HTTPNotFoundException(details=f'Research {research_name} not found')
    
    if dbm_research['approval_required']:
        user_researches = DBM.users.get_user_participated_researches(token_payload.id)
        if not dbm_research['id'] in user_researches:
            raise HTTPForbiddenException(details=f'User {token_payload.id} does not participate in research {research_name}')
        
    if not dbm_research['status'] != 'ongoing':
        raise HTTPConflictException(details=f'Research {research_name} is not in "ongoing" status.')

    try:
        dbm_qr_info = DBM.samples.get_qr_info(qr_hex)
    except NoQrCodeException:
        raise HTTPNotFoundException(details=f'Qr {qr_hex} not found')

    if dbm_qr_info['is_used']:
        raise HTTPConflictException(details=f'Qr {qr_hex} is already used')
    
    if dbm_qr_info['kit_id']:
        raise HTTPConflictException(details=f'Qr {qr_hex} is not assigned to any kit')
    
    try:
        dbm_kit = DBM.kits.get_info(dbm_qr_info['kit_id'])
    except NoQrCodeException:
        raise HTTPNotFoundException(details=f'No kit with id {dbm_qr_info["kit_id"]} found (very strange).')
    
    if not dbm_kit['owner']:
        raise HTTPForbiddenException(details=f'Kit {dbm_qr_info["kit_id"]} is not assigned to any user')
    
    if not dbm_kit['owner']['id'] == token_payload.id:
        raise HTTPForbiddenException(details=f'User {token_payload.id} does not own kit {dbm_kit["id"]}')
    
    if not dbm_kit['status'] == 'activated':
        raise HTTPConflictException(details=f'Kit {dbm_kit["id"]} hasn\'t been activated')



    dbm_new_sample_id = DBM.samples.new(qr_id=dbm_qr_info['id'], 
                        research_id=dbm_research['id'], 
                        owner_id = token_payload.id,
                        collected_at=collected_at,
                            gps=gps,
                            weather=weather, 
                            user_comment=user_comment,
                            photo_hex_string = photo_hex_string)
    return dbm_new_sample_id
        
    