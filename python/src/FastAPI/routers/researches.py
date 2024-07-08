from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from db_manager import DBM
from datetime import date
from exceptions import HTTPConflictException, HTTPForbiddenException, NoResearchException, HTTPNotFoundException, NoUserException
from schemas import Identifier, TokenPayload
from utils import get_admin, get_current_user, get_volunteer_or_admin

router = APIRouter()

@router.get('/researches')
def get_researches(token_payload: Annotated[TokenPayload, Depends(get_current_user)]):
    return DBM.researches.get_all()

@router.get('/researches/{research_identifier}')
def get_research(research_identifier: str, token_payload: Annotated[TokenPayload, Depends(get_current_user)]):
    research_identifier = Identifier(identifier=research_identifier).identifier
    try:
        dbm_research = DBM.researches.get_info(research_identifier)
    except NoResearchException:
        raise HTTPNotFoundException(detail=f'Research {research_identifier} not found')
    return dbm_research

@router.post('researches/{research_identifier}/send_request')
def send_request(research_identifier: str, token_payload: Annotated[TokenPayload, Depends(get_volunteer_or_admin)]):
    research_identifier = Identifier(identifier=research_identifier).identifier
    try:
        dbm_research = DBM.researches.get_info(research_identifier)
    except NoResearchException:
        raise HTTPNotFoundException(detail=f'Research {research_identifier} not found')
    
    if not dbm_research['approval_required']:
        raise HTTPConflictException(detail=f'Research {research_identifier} approval is not required')

    if dbm_research['status'] in ['ended', 'canceled']:
        raise HTTPConflictException(detail=f'Research {research_identifier} already ended')
    
    participants = DBM.researches.get_participants(dbm_research['id'])
    if token_payload.id in participants:
        raise HTTPConflictException(detail=f'User {token_payload.id} already participate in research {research_identifier}')
    
    candidates = DBM.researches.get_candidates(dbm_research['id'])
    if token_payload.id in candidates:
        raise HTTPConflictException(detail=f'User {token_payload.id} already sent request to research {research_identifier}')

    DBM.researches.send_request(dbm_research['id'], token_payload.id, log=False)


@router.post('researches/{research_identifier}/approve_request')
def approve_request(research_identifier: str, candidate_identifier : str, token_payload: Annotated[TokenPayload, Depends(get_admin)]):
    research_identifier = Identifier(identifier=research_identifier).identifier
    candidate_identifier = Identifier(identifier=candidate_identifier).identifier
    try:
        dbm_research = DBM.researches.get_info(research_identifier)
    except NoResearchException:
        raise HTTPNotFoundException(detail=f'Research {research_identifier} not found')
    
    if not dbm_research['created_by'] == token_payload.id:
        raise HTTPForbiddenException(detail=f'User {token_payload.id} is not creator of research {research_identifier}')

    if not dbm_research['approval_required']:
        raise HTTPConflictException(detail=f'Research {research_identifier} approval is not required')

    if dbm_research['status'] in ['ended', 'canceled']:
        raise HTTPConflictException(detail=f'Research {research_identifier} already ended')
    
    try:
        candidate_info = DBM.users.get_info(candidate_identifier)
    except NoUserException:
        raise HTTPNotFoundException(detail=f'User {candidate_identifier} not found')
    
    candidate_id = candidate_info['id']
    research_id = dbm_research['id']
    participants = DBM.researches.get_participants(research_id)
    if candidate_id in participants:
        raise HTTPConflictException(detail=f'User {candidate_id} already participate in research {research_identifier}')
    
    candidates = DBM.researches.get_candidates(research_id)
    if candidate_id not in candidates:
        raise HTTPConflictException(detail=f'User {candidate_id} not sent request to research {research_identifier}')

    DBM.researches.approve_request(research_id, candidate_id, log=False)

@router.post('researches/{research_identifier}/decline_request')
def decline_request(research_identifier: str, candidate_identifier : str, token_payload: Annotated[TokenPayload, Depends(get_admin)]):
    research_identifier = Identifier(identifier=research_identifier).identifier
    candidate_identifier = Identifier(identifier=candidate_identifier).identifier
    try:
        dbm_research = DBM.researches.get_info(research_identifier)
    except NoResearchException:
        raise HTTPNotFoundException(detail=f'Research {research_identifier} not found')
    
    if not dbm_research['created_by'] == token_payload.id:
        raise HTTPForbiddenException(detail=f'User {token_payload.id} is not creator of research {research_identifier}')

    if not dbm_research['approval_required']:
        raise HTTPConflictException(detail=f'Research {research_identifier} approval is not required')

    if dbm_research['status'] in ['ended', 'canceled']:
        raise HTTPConflictException(detail=f'Research {research_identifier} already ended')
    
    try:
        candidate_info = DBM.users.get_info(candidate_identifier)
    except NoUserException:
        raise HTTPNotFoundException(detail=f'User {candidate_identifier} not found')
    
    candidate_id = candidate_info['id']
    research_id = dbm_research['id']
    participants = DBM.researches.get_participants(research_id)
    if candidate_id in participants:
        raise HTTPConflictException(detail=f'User {candidate_id} already participate in research {research_identifier}')
    
    candidates = DBM.researches.get_candidates(research_id)
    if candidate_id not in candidates:
        raise HTTPConflictException(detail=f'User {candidate_id} not sent request to research {research_identifier}')

    DBM.researches.decline_request(research_id, candidate_id, log=False)
    

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


