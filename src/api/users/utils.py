from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import jwt
from src.config import Config
import uuid
import logging
from fastapi import HTTPException,status
from itsdangerous import URLSafeTimedSerializer,SignatureExpired,BadSignature


# Configure Passlib with bcrypt
# deprecated="auto" ensures older hashes are marked as deprecated if you update schemes
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Helper functions
def hash_password(password: str) -> str:
    """Hashes a plain-text password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain-text password against the stored hash."""
    return pwd_context.verify(plain_password, hashed_password)



def create_access_token(data: dict, expires_delta: timedelta | None = None,refresh:bool=False) -> str:
    # to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload={}
    payload['user']=data
    payload['exp']=expire
    payload['jti']=str(uuid.uuid4())

    payload['refresh']=refresh

    token=jwt.encode(
        payload=payload,
        key=Config.SECRET_KEY,
        algorithm=Config.ALGORITHM
    )

    return token


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            key=Config.SECRET_KEY,
            algorithms=[Config.ALGORITHM]
        )
        return payload
    
    # # 2. Invalid Signature / Wrong Secret / Tampered Token
    # except jwt.InvalidSignatureError:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Invalid token signature",
    #         headers={"WWW-Authenticate": "Bearer"},
    #     )
    except jwt.PyJWTError as e:
        logging.warning(e)
        return None



serializer=URLSafeTimedSerializer(
    Config.SECRET_KEY,
    salt=Config.SALT
)


async def create_token_serializer(email:str):
    token=serializer.dumps({
        "email":email,
        "purpose":"email_verification"
    })

    return token


async def verify_token_serializer(token:str):
    try:
        data=serializer.loads(
            token,
            max_age=1800
        )

        return data

    except SignatureExpired:
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail="Verification link has expired..!!"
        )
    except BadSignature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification link..!!"
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Somthing was wrong..!!"
        )









