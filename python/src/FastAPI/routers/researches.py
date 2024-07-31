from typing import Annotated
from fastapi import Depends, status
from fastapi.responses import JSONResponse, Response
from fastapi.routing import APIRouter
from db_manager import DBM
from datetime import date

from exceptions import HTTPConflictException, HTTPForbiddenException, NoResearchException, HTTPNotFoundException, NoUserException
from schemas.researches import ApproveResearchRequest, CreateResearchRequest, DeclineResearchRequest, GetResearchRequest, ResearchBase, ResearchNewStatusResponse, ResearchRequest, ResearchResponse, SendResearchParticipantRequest, MyResearch
from schemas.common import TokenPayload
from utils import get_admin, get_current_user, get_volunteer_or_admin

from dependencies.identifiers_validators import research_identifier_validator_dependency

router = APIRouter(tags=['researches'])

@router.get('/researches', response_model=list[ResearchResponse])
def get_researches(token_payload: Annotated[TokenPayload, Depends(get_current_user)]):
    all_researches = list(DBM.researches.get_all().values())
    return JSONResponse(status_code=status.HTTP_200_OK, content=all_researches)

@router.get('/researches/{research_identifier}', response_model=ResearchResponse)
def get_research(research_identifier: Annotated[str, Depends(research_identifier_validator_dependency)], token_payload: Annotated[TokenPayload, Depends(get_current_user)]):
    try:
        dbm_research = DBM.researches.get_info(research_identifier)
    except NoResearchException:
        raise HTTPNotFoundException(detail=f'Research {research_identifier} not found')
    return JSONResponse(status_code=status.HTTP_200_OK, content=dbm_research)

@router.post('/researches/{research_identifier}/send_request')
def send_request(research_identifier: Annotated[str, Depends(research_identifier_validator_dependency)], 
                token_payload: Annotated[TokenPayload, Depends(get_volunteer_or_admin)]
                ):
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
    return JSONResponse(status_code=status.HTTP_200_OK, content=f"User {token_payload.id} sent request to research {research_identifier}")


@router.post('/researches/{research_identifier}/approve_request')
def approve_request(research_identifier: Annotated[str, Depends(research_identifier_validator_dependency)], approve_research_request: ApproveResearchRequest, token_payload: Annotated[TokenPayload, Depends(get_admin)]):
    candidate_identifier = approve_research_request.candidate_identifier
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
    return JSONResponse(status_code=status.HTTP_200_OK, content=f"User {candidate_id} approved request to research {research_identifier}")

@router.post('/researches/{research_identifier}/decline_request')
def decline_request(research_identifier: Annotated[str, Depends(research_identifier_validator_dependency)], decline_research_request: DeclineResearchRequest, token_payload: Annotated[TokenPayload, Depends(get_admin)]):
    candidate_identifier = decline_research_request.candidate_identifier
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
    return Response(status_code=status.HTTP_200_OK, 
                    content=f"User {candidate_id} declined request to research {research_identifier}")

@router.put('/researches/{research_identifier}/start', response_model=ResearchNewStatusResponse)
def set_research_start(
        research_identifier: Annotated[str, Depends(research_identifier_validator_dependency)],
        token_payload: Annotated[TokenPayload, Depends(get_admin)]
        ):
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
        raise HTTPConflictException(detail=f'Research {research_identifier} is cancelled')
    
    DBM.researches.change_status(research_identifier, new_status="ongoing", log=True)

    return JSONResponse(status_code=status.HTTP_200_OK, 
                        content={"research_identifier": research_identifier, 
                                 "status": "ongoing"})


@router.put('/researches/{research_identifier}/pause', response_model=ResearchNewStatusResponse)
def set_research_paused(
            research_identifier: Annotated[str, Depends(research_identifier_validator_dependency)],
            token_payload: Annotated[TokenPayload, Depends(get_admin)]
        ):
    try:
        research_info = DBM.researches.get_info(research_identifier)
    except NoResearchException:
        raise HTTPNotFoundException(detail=f'Research {research_identifier} not found')
    
    if token_payload.id != research_info['created_by']:
        raise HTTPForbiddenException(detail=f'Research owner differs from autorized user')
    
    if  research_info['status'] == 'pending':
        raise HTTPConflictException(detail=f'Research {research_identifier} not started yet')

    if  research_info['status'] == 'paused':
        raise HTTPConflictException(detail=f'Research {research_identifier} already paused')
    
    if research_info['status'] == 'ended':
        raise HTTPConflictException(detail=f'Research {research_identifier} already ended')
    
    if research_info['status'] == 'cancelled':
        raise HTTPConflictException(detail=f'Research {research_identifier} is cancelled')

    DBM.researches.change_status(research_identifier, new_status="paused", log=True)

    return JSONResponse(status_code=status.HTTP_200_OK, 
                        content={"research_identifier": research_identifier, 
                                 "status": "paused"})


@router.put('/researches/{research_identifier}/end', response_model=ResearchNewStatusResponse)
def set_research_ended(
        research_identifier: Annotated[str, Depends(research_identifier_validator_dependency)],
        token_payload: Annotated[TokenPayload, Depends(get_admin)]
    ):
    try:
        research_info = DBM.researches.get_info(research_identifier)
    except NoResearchException:
        raise HTTPNotFoundException(detail=f'Research {research_identifier} not found')
    
    if token_payload.id != research_info['created_by']:
        raise HTTPForbiddenException(detail=f'Research owner differs from autorized user')
    
    if  research_info['status'] == 'pending':
        raise HTTPConflictException(detail=f'Research {research_identifier} not started yet')

    if research_info['status'] == 'ended':
        raise HTTPConflictException(detail=f'Research {research_identifier} already ended')
    
    if research_info['status'] == 'cancelled':
        raise HTTPConflictException(detail=f'Research {research_identifier} is cancelled')
    
    DBM.researches.change_status(research_identifier, new_status="ended", log=True)
    
    return JSONResponse(status_code=status.HTTP_200_OK, 
                        content={"research_identifier": research_identifier, 
                                 "status": "ended"})


@router.put('/researches/{research_identifier}/cancel', response_model=ResearchNewStatusResponse)
def set_research_cancelled(
    research_identifier: Annotated[str, Depends(research_identifier_validator_dependency)],
    token_payload: Annotated[TokenPayload, Depends(get_admin)]
):
    try:
        research_info = DBM.researches.get_info(research_identifier)
    except NoResearchException:
        raise HTTPNotFoundException(detail=f'Research {research_identifier} not found')
    
    if token_payload.id != research_info['created_by']:
        raise HTTPForbiddenException(detail=f'Research owner differs from autorized user')
    
    if research_info['status'] == 'cancelled':
        raise HTTPConflictException(detail=f'Research {research_identifier} already cancelled')
    
    if research_info['status'] == 'ended':
        raise HTTPConflictException(detail=f'Research {research_identifier} already ended')
    
    DBM.researches.change_status(research_identifier, new_status="cancelled", log=True)
    
    return JSONResponse(status_code=status.HTTP_200_OK, 
                        content={"research_identifier": research_identifier, 
                                 "status": "cancelled"})


@router.post('/researches', response_model=ResearchBase)
def create_research(
    token_payload: Annotated[TokenPayload, Depends(get_admin)],
    create_research_request : CreateResearchRequest
    ):
    
    user_id = token_payload.id
    research_name = create_research_request.research_name

    try:
        DBM.researches.has(research_name)
    except NoResearchException:
        pass
    else:
        raise HTTPConflictException(detail=f'Research {research_name} already exists')

    new_research_id = DBM.researches.new(research_name=research_name, 
                              user_id=user_id, 
                              day_start=create_research_request.day_start, 
                              research_comment=create_research_request.research_comment, 
                              log=False, 
                              approval_required=create_research_request.approval_required)
    
    return JSONResponse(status_code=status.HTTP_201_CREATED, 
                        content={'id': new_research_id, 'name': research_name}
                        )

