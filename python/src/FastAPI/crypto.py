import jwt
from config import JWT_PUBLIC_KEY

def verify_jwt_token(token):
    payload = jwt.decode(token, JWT_PUBLIC_KEY, algorithms=['RS256'])
    return payload
