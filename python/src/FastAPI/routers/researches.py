from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from db_manager import DBM
from datetime import date
from exceptions import NoResearchException, HTTPNotFoundException
from schemas import TokenPayload
from utils import get_current_user

router = APIRouter()

@router.get('/researches')
def get_researches(token_payload: Annotated[TokenPayload, Depends(get_current_user)]):
    return DBM.researches.get_all()

@router.get('/researches/{research_identifier}')
def get_research(research_identifier, token_payload: Annotated[TokenPayload, Depends(get_current_user)]):
    try:
        dbm_research = DBM.researches.get_info(research_identifier)
    except NoResearchException:
        raise HTTPNotFoundException(details=f'Research {research_identifier} not found')
    return dbm_research
    

@router.post('/researches')
def create_research(
    research_name: str,
    user_name: str,
    day_start: date,
    token_payload: Annotated[TokenPayload, Depends(get_current_user)]
    ):
    return DBM.researches.new(research_name, user_name, day_start)

#- рудименты
# начать делать проверку у юзера есть доступ смотреть инфу

