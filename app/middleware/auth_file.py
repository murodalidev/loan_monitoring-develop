import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from ..db.connect_db import SessionManager
from ..models.users.users import Users
class AuthHandler():
    security = HTTPBearer()
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    secret = 'SECRET'

    def get_password_hash(self, password):
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def encode_token(self, username):
        payload = {
            'exp': datetime.now() + timedelta(days=0, minutes=480),
            'iat': datetime.now(),
            'username': username
        }
        return jwt.encode(
            payload,
            self.secret,
            algorithm='HS256'
        )

    def decode_token(self, token):
        try:
            payload = jwt.decode(token, self.secret, algorithms=['HS256'])
            if 'username' not in payload:
                raise HTTPException(status_code=401, detail={'status':'Signature has expired'})
            
            with SessionManager() as db_session:
                get_user = db_session.query(Users).filter(Users.username == payload['username']).first()
            if get_user.token != token:
                raise HTTPException(status_code=401, detail='Invalid token!')
            if (get_user is None):
                raise HTTPException(status_code=401, detail='Not authenticated!')
            return get_user
        
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail={'status':'Signature has expired. ReLogin please.'})
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=401, detail={'status':'Invalid token'})

    def auth_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security)):
        return self.decode_token(auth.credentials)      
