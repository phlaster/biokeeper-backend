from pydantic import BaseModel
import datetime

class Role(BaseModel):
    id  : int
    name: str
    info: str

class TokenPayload(BaseModel):
    username: str
    role : Role
    exp: datetime.datetime