from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from db_manager import DBM
from datetime import date
from exceptions import HTTPConflictException, NoResearchException, HTTPNotFoundException,NoUserException,HTTPForbiddenException
from schemas import Identifier, TokenPayload
from utils import get_admin, get_current_user

router = APIRouter()

@router.get('/researches')
def get_researches(token_payload: Annotated[TokenPayload, Depends(get_current_user)]):
    return DBM.researches.get_all()

@router.get('/researches/{research_identifier}')
def get_research(research_identifier, token_payload: Annotated[TokenPayload, Depends(get_current_user)]):
    research_identifier = Identifier(identifier=research_identifier).identifier
    try:
        dbm_research = DBM.researches.get_info(research_identifier)
    except NoResearchException:
        raise HTTPNotFoundException(detail=f'Research {research_identifier} not found')
    return dbm_research

@router.put('/researches/{research_identifier}/start')
def set_research_start(
    research_identifier: str,
    token_payload: Annotated[TokenPayload, Depends(get_admin)]
):
    research_identifier = Identifier(identifier=research_identifier).identifier
    try:
        research_info = DBM.researches.get_info(research_identifier)
    except NoResearchException:
        raise HTTPNotFoundException(detail=f'Research {research_identifier} not found')
    if token_payload.id != research_info['created_by']:
        raise HTTPForbiddenException(detail=f'Research owner differs from autorized user')
    if  research_info['status'] == 'ongoing':
        raise HTTPConflictException(detail=f'Research {research_identifier} already ongoing')
    if research_info['status'] == 'ended':
        raise HTTPConflictException(detail=f'Research {research_identifier} already ended')
    if research_info['status'] == 'cancelled':
        raise HTTPConflictException(detail=f'Research {research_identifier} already cancelled')
    try:
        DBM.researches.change_status(research_identifier, new_status=2, log=True)
    except NoResearchException:
        raise HTTPNotFoundException(detail=f'Research {research_identifier} not found')
    return {"research_id": research_identifier, "new_status": "ongoing"}

@router.put('/researches/{research_identifier}/paused')
def set_research_paused(
    research_identifier: str,
    token_payload: Annotated[TokenPayload, Depends(get_admin)]
):
    research_identifier = Identifier(identifier=research_identifier).identifier
    try:
        research_info = DBM.researches.get_info(research_identifier)
    except NoResearchException:
        raise HTTPNotFoundException(detail=f'Research {research_identifier} not found')
    if token_payload.id != research_info['created_by']:
        raise HTTPForbiddenException(detail=f'Research owner differs from autorized user')
    if  research_info['status'] == 'paused':
        raise HTTPConflictException(detail=f'Research {research_identifier} already paused')
    if research_info['status'] == 'ended':
        raise HTTPConflictException(detail=f'Research {research_identifier} already ended')
    if research_info['status'] == 'cancelled':
        raise HTTPConflictException(detail=f'Research {research_identifier} already cancelled')
    try:
        DBM.researches.change_status(research_identifier, new_status=3, log=True)
    except NoResearchException:
        raise HTTPNotFoundException(detail=f'Research {research_identifier} not found')
    return {"research_id": research_identifier, "new_status": "paused"}

@router.put('/researches/{research_identifier}/end')
def set_research_ended(
    research_identifier: str,
    token_payload: Annotated[TokenPayload, Depends(get_admin)]
):
    research_identifier = Identifier(identifier=research_identifier).identifier
    try:
        research_info = DBM.researches.get_info(research_identifier)
    except NoResearchException:
        raise HTTPNotFoundException(detail=f'Research {research_identifier} not found')
    if token_payload.id != research_info['created_by']:
        raise HTTPForbiddenException(detail=f'Research owner differs from autorized user')
    if  research_info['status'] == 'paused':
        raise HTTPConflictException(detail=f'Research {research_identifier} already paused')
    if research_info['status'] == 'ended':
        raise HTTPConflictException(detail=f'Research {research_identifier} already ended')
    if research_info['status'] == 'cancelled':
        raise HTTPConflictException(detail=f'Research {research_identifier} already cancelled')
    if research_info['status'] == 'ongoing':
        raise HTTPConflictException(detail=f'Research {research_identifier} already ongoing')
    try:
        DBM.researches.change_status(research_identifier, new_status=4, log=True)
    except NoResearchException:
        raise HTTPNotFoundException(detail=f'Research {research_identifier} not found')
    return {"research_id": research_identifier, "new_status": "ended"}

@router.put('/researches/{research_identifier}/cancel')
def set_research_cancelled(
    research_identifier: str,
    token_payload: Annotated[TokenPayload, Depends(get_admin)]
):
    research_identifier = Identifier(identifier=research_identifier).identifier
    try:
        research_info = DBM.researches.get_info(research_identifier)
    except NoResearchException:
        raise HTTPNotFoundException(detail=f'Research {research_identifier} not found')
    if token_payload.id != research_info['created_by']:
        raise HTTPForbiddenException(detail=f'Research owner differs from autorized user')
    if  research_info['status'] == 'paused':
        raise HTTPConflictException(detail=f'Research {research_identifier} already paused')
    if research_info['status'] == 'ended':
        raise HTTPConflictException(detail=f'Research {research_identifier} already ended')
    if research_info['status'] == 'cancelled':
        raise HTTPConflictException(detail=f'Research {research_identifier} already cancelled')
    if research_info['status'] == 'ongoing':
        raise HTTPConflictException(detail=f'Research {research_identifier} already ongoing')
    try:
        DBM.researches.change_status(research_identifier, new_status=5, log=True)
    except NoResearchException:
        raise HTTPNotFoundException(detail=f'Research {research_identifier} not found')
    return {"research_id": research_identifier, "new_status": "cancelled"}

@router.post('/researches')
def create_research(
    research_name: str,
    day_start: date,
    token_payload: Annotated[TokenPayload, Depends(get_admin)],
    research_comment: str | None = None,
    approval_required: bool = True
    ):
    
    user_id = token_payload.id

    try:
        DBM.researches.has(research_name)
    except NoResearchException:
        pass
    else:
        raise HTTPConflictException(detail=f'Research {research_name} already exists')

    return DBM.researches.new(research_name=research_name, 
                              user_id=user_id, 
                              day_start=day_start, 
                              research_comment=research_comment, 
                              log=False, 
                              approval_required=approval_required)


