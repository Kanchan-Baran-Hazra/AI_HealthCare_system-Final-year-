from fastapi import APIRouter, Request, HTTPException, status,Depends
from fastapi.responses import RedirectResponse,HTMLResponse
from authlib.integrations.starlette_client import OAuth
from src.config import Config
from datetime import timedelta,datetime
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.main import get_db
from src.api.users.service import UserService
from src.db.models.users import User
from src.api.users.utils import create_access_token
import logging
import os







oauth_route = APIRouter()

oauth = OAuth()


user_service=UserService()


# google
oauth.register(
    name="google",
    client_id=Config.GOOGLE_CLIENT_ID,
    client_secret=Config.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)



# github
oauth.register(
    name="github",
    client_id=Config.GITHUB_CLIENT_ID,
    client_secret=Config.GITHUB_CLIENT_SECRET,
    access_token_url="https://github.com/login/oauth/access_token",
    authorize_url="https://github.com/login/oauth/authorize",
    api_base_url="https://api.github.com/",
    client_kwargs={"scope": "read:user user:email"},
)




# disable later and add to react
@oauth_route.get("/auth/callback", response_class=HTMLResponse)
async def serve_callback_page():
    # Path to your HTML file
    file_path = os.path.join("client", "callback.html") 
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()




# google setup
@oauth_route.get("/auth/google")
async def google_login(request: Request):
    redirect_uri = Config.GOOGLE_REDIRECT_URI
    try:
        # authorize_redirect returns a RedirectResponse, do not await it
        return await oauth.google.authorize_redirect(request, redirect_uri)
    except Exception as e:
        # Print or log the real error to debug easily
        logging.error(f"Google OAuth redirect failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth initialization failed: {str(e)}",
        )



@oauth_route.get("/auth/google/callback")
async def google_callback(request: Request,db:AsyncSession=Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
    
        user_info = token["userinfo"]
        # print(user_info)
        # return user_info
    
        # 1. Fetch user from database
        user = await user_service.get_user_byemail(user_info.email, db)
    
        # # new account
        if not user:
            user=User(
                name=user_info.get("name"),
                email=user_info.get("email"),
                hashed_password=None,
                google_id=user_info.get("sub"),
                profile_picture=user_info.get("picture"),
                auth_provider="google",
                is_verified=True
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
    
            token_payload={
                'email':user.email,
                'id':str(user.id)
            }
        else:
            # new google id
            if not user_service.get_user_by_googleId(user_info['sub'],db):
                user.google_id=user_info['sub']
                user.profile_picture=user_info['picture']
    
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
    
        return RedirectResponse(
            url=(f"{Config.BACKEND_URI}/api/v1/oauth/auth/callback" f"?access_token={access_token}" f"&refresh_token={refresh_token}")
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{e}"
        )




# github setup
@oauth_route.get("/auth/github")
async def github_login(request: Request):
    try:
        redirect_uri = Config.GITHUB_REDIRECT_URI

        return await oauth.github.authorize_redirect(request, redirect_uri)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail=f"{e}",
        )




@oauth_route.get("/auth/github/callback")
async def github_callback(request: Request,db:AsyncSession=Depends(get_db)):
    try:
        token = await oauth.github.authorize_access_token(request)
        
        responce = await oauth.github.get("user", token=token)
        github_user = responce.json()

        # return github_user

        email=github_user.get("email")
        name=github_user.get("name")
        github_id=github_user.get("node_id")
        avatar_url=github_user.get("avatar_url")

        # 1. Fetch user from database
        user = await user_service.get_user_byemail(email, db)
    
        # new account
        if not user:
            user=User(
                name=name,
                email=email,
                hashed_password=None,
                github_id=github_id,
                profile_picture=avatar_url,
                auth_provider="github",
                is_verified=True
            )

            db.add(user)
            await db.commit()
            await db.refresh(user)
    
            token_payload={
                'email':user.email,
                'id':str(user.id)
            }
        else:
            # new github id
            if not user_service.get_user_by_githubID(github_id,db):
                user.github_id=github_id
                user.profile_picture=avatar_url
    
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
    
        return RedirectResponse(
            url=(f"{Config.BACKEND_URI}/api/v1/oauth/auth/callback" f"?access_token={access_token}" f"&refresh_token={refresh_token}")
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{e}"
        )


