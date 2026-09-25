from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from typing import Optional,List,Any
from fastapi import Request,HTTPException,status,Depends
from src.api.users.service import UserService
from src.api.users.utils import decode_token
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.main import get_db
from src.db.models.users import UserRole,User
from src.db.redis import is_jti_blocklisted

user_service=UserService()



class TokenBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)


    async def __call__(
        self, request: Request
    ) -> Optional[dict]:
        # 1. Get credentials from header using HTTPBearer's parent method
        credentials: Optional[HTTPAuthorizationCredentials] = await super().__call__(request)

        if not credentials:
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or missing authorization scheme.",
                )
            return None

        # 2. Ensure scheme is Bearer
        if credentials.scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme. Must be Bearer.",
            )

        token=credentials.credentials
        # print(token)
        if not self.token_valid(token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token or token time expired..!!"
            )
        
        token_datails=decode_token(token)

        self.verify_token_data(token_datails)

        # 3. Check if JTI is revoked in Redis
        jti = token_datails.get("jti")
        if not jti or await is_jti_blocklisted(jti):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked or logged out",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return token_datails

    def token_valid(self,token:str)->bool:
        token_data=decode_token(token)

        return True if token_data is not None else False

    def verify_token_data(self,token_data:dict):
        raise NotImplementedError("Please call the child class method...")


class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data:dict) ->None:
        # Override to check that refresh IS True
        if token_data and token_data['refresh']:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Please provide a valid access token.",
            )

class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data:dict) ->None:
        # Override to check that refresh IS True
        if token_data and not token_data['refresh']:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Please provide a valid refresh token.",
            )
        



async def get_current_user(
    token_details: dict = Depends(AccessTokenBearer()),
    db: AsyncSession = Depends(get_db),
):
    """
    Dependency that decodes the access token, checks for user existence in DB,
    and returns the SQLAlchemy User object.
    """
    # 1. Extract user identifier from payload (sub usually holds user email or ID)
    user_email: str | None = token_details['user']['email']

    if user_email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload is invalid (missing 'user' claim)",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. Query user from database
    user=await user_service.get_user_byemail(user_email,db)

    # 3. Verify user exists
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User associated with this token no longer exists",
        )

    return user


class RoleChecker:
    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> Any:
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )
        return True











