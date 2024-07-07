from typing import Annotated
from exceptions import NotFoundException
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from schemas import TokenPayload
from db_manager import DBM
from crypto import verify_jwt_token
from exceptions import NoUserException
import jwt


external_token_url = "http://127.0.0.1:8000/token"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=external_token_url)

NotEnoughPermissionsException = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not enough permissions",
        headers={"WWW-Authenticate": "Bearer"},
    )

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> TokenPayload:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    expired_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Access token expired",
        headers={"WWW-Authenticate": "Bearer"},
    )
    no_user_in_db_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User not found",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = verify_jwt_token(token)
        if not payload:
            raise credentials_exception
        username: str = payload.get("username")
        if username is None:
            raise credentials_exception
        DBM.users.has(username)
    except jwt.ExpiredSignatureError:
        raise expired_exception
    except jwt.InvalidTokenError as error:
        print(error)
        raise credentials_exception
    except NoUserException:
        print("User not found")
        raise no_user_in_db_exception
    return TokenPayload(**payload)

async def get_admin(token: Annotated[TokenPayload, Depends(get_current_user)]) -> TokenPayload:
    if token.role.name != "admin":
        raise NotEnoughPermissionsException
    return token

async def get_volunteer(token: Annotated[TokenPayload, Depends(get_current_user)]) -> TokenPayload:
    if token.role.name != "volunteer":
        raise NotEnoughPermissionsException
    return token

async def get_observer(token: Annotated[TokenPayload, Depends(get_current_user)]) -> TokenPayload:
    if token.role.name != "observer":
        raise NotEnoughPermissionsException
    return token

def validate_return_from_db(data,
                      search_param_name,
                      search_param_value,
                      logger=None,
                      exception=NotFoundException):
    key,value = data.items()[0]
    if not value:
        if logger:
            logger.log(f"Error: Can't find {key} using {search_param_name} with {search_param_value}.", 0)
        raise exception
    return value
