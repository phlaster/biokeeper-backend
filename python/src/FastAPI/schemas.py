from pydantic import BaseModel, Field
import datetime

class Role(BaseModel):
    id  : int
    name: str
    info: str

class TokenPayload(BaseModel):
    id: int
    username: str
    role : Role
    exp: datetime.datetime

from pydantic import BaseModel, validator, ValidationError
from typing import Union

class Identifier(BaseModel):
    identifier: int | str

    @validator('identifier', pre=True)
    def validate_identifier(cls, v):
        if isinstance(v, int):
            return v
        elif isinstance(v, str):
            if v.isdigit():
                return int(v)
            else:
                return v
        raise ValueError('Identifier must be either an integer or a string')