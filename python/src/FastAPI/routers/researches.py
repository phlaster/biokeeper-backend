from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from db_manager import DBM
from datetime import date
from exceptions import HTTPConflictException, NoResearchException, HTTPNotFoundException
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

@router.post('/researches')
def create_research(
    research_name: str,
    day_start: date,
    token_payload: Annotated[TokenPayload, Depends(get_admin)],
    research_comment: str | None = None,
    approval_required: bool = True
    ):
    
    user_id = token_payload.user_id

    try:
        DBM.researches.has(research_name)
    except NoResearchException:
        pass
    else:
        raise HTTPConflictException(details=f'Research {research_name} already exists')

    return DBM.researches.new(research_name=research_name, 
                              user_id=user_id, 
                              day_start=day_start, 
                              research_comment=research_comment, 
                              log=False, 
                              approval_required=approval_required)


