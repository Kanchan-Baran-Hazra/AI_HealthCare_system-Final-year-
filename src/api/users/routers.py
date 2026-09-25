from fastapi import APIRouter, status, Depends,HTTPException,BackgroundTasks
from src.db.main import get_db
from src.api.users.service import UserService
from src.api.users.dependancy import AccessTokenBearer,RefreshTokenBearer,RoleChecker
from src.db.models.users import UserRole
from src.api.users.schemas import (
    UserResponse,
    UserRegister,
    LoginRequest,
    AccessTokenResponse,
)
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse,RedirectResponse
from src.api.users.utils import verify_password,create_access_token,verify_token_serializer
from datetime import timedelta
from src.config import Config
from datetime import datetime,timezone
from src.api.users.dependancy import AccessTokenBearer,RefreshTokenBearer,get_current_user,RoleChecker
from src.worker.email_worker import dispatch_welcome_email
from src.db.redis import add_jti_to_blocklist


user_router = APIRouter()

user_service = UserService()

access_token_bearer=AccessTokenBearer()
refresh_token_bearer=RefreshTokenBearer()


# Handy pre-configured instances:
allow_admin = RoleChecker([UserRole.ADMIN])
allow_admin_or_moderator = RoleChecker([UserRole.ADMIN, UserRole.MODERATOR])

@user_router.get('/')
async def get_access(user_info=Depends(access_token_bearer)):
    return user_info


@user_router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(user_in: UserRegister, db: AsyncSession = Depends(get_db)):
    new_user = await user_service.register_user(user_in, db)
    dispatch_welcome_email.delay(new_user.email)
    return new_user



@user_router.post("/login")
async def login(credentials: LoginRequest, db: AsyncSession = Depends(get_db)):
    
    # 1. Fetch user from database
    user = await user_service.get_user_byemail(credentials.email, db)
    
    # 2. Check if user exists and password matches
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.is_verified==False:
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail="Email not verified..!!"
        )

    token_payload={
        'email':user.email,
        'id':str(user.id)
    }

    access_token = create_access_token(
        data=token_payload, 
        refresh=False
    )

    refresh_token = create_access_token(
        data=token_payload,
        expires_delta=timedelta(Config.REFRESH_TOKEN_EXPIRE_DAY),
        refresh=True
    )

    # 4. Return tokens
    return JSONResponse(
        content={
            "access_token":access_token,
            "refresh_token":refresh_token,
            "message":"Login Successfull",
            "user":{
                "email":user.email,
                "id":str(user.id)
            }
        }
    )




@user_router.post("/refresh-token", response_model=AccessTokenResponse)
async def get_new_access_token(
    token_details: dict = Depends(refresh_token_bearer),
):
    """
    Generates a new access token using a valid Refresh Token provided in the Authorization header.
    """
    # Check token expiration timestamp (safety fallback)
    exp = token_details.get("exp")
    if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract user identity/subject from payload
    user_data = token_details.get("user")
    if not user_data['email']:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    # Generate a fresh Access Token
    new_access_token = create_access_token(
        data=user_data,
        refresh=False,
    )

    return AccessTokenResponse(
        access_token=new_access_token,
        token_type="bearer",
    )



@user_router.get("/me")
async def get_my_profile(
    current_user= Depends(get_current_user)
):
    """
    Protected route: Returns profile info for the logged-in user.
    """
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "is_active": getattr(current_user, "is_active", True),
        "avatar":current_user.profile_picture,
        "name":current_user.name
    }




@user_router.post("/logout")
async def logout(
    token_details: dict = Depends(refresh_token_bearer)
):
    """
    Revokes the current access token by adding its JTI to Redis blocklist.
    """
    jti = token_details.get("jti")
    exp = token_details.get("exp")

    if not jti or not exp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token claims"
        )

    # Calculate remaining Time-To-Live (TTL) in seconds
    now = int(datetime.now(timezone.utc).timestamp())
    remaining_ttl = exp - now

    if remaining_ttl > 0:
        # Save to Redis with an expiration so it automatically drops when expired
        await add_jti_to_blocklist(jti, expiry_seconds=remaining_ttl)

    return {"message": "Successfully logged out and token revoked"}




@user_router.get('/verify-email/{token}')
async def verify_email(token:str,db:AsyncSession=Depends(get_db)):
    try:
        data=await verify_token_serializer(token)
        if data.get("purpose")!="email_verification":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification token..!!"
            )

        email=data.get("email")
        user= await user_service.get_user_byemail(email,db)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found..!!"
            )
        if user.is_verified:
            return {"message":"Email already verified..!"}
        user.is_verified=True
        await db.commit()
        return RedirectResponse(
            url=f"{Config.REACT_URI}/client/index.html"
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Somthing was wrong..!!"
        )










