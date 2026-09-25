from src.api.users.schemas import UserRegister
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from sqlalchemy import select
from src.db.models import users as models
from src.api.users.utils import hash_password





class UserService:
    async def get_user_byemail(self, email: str, db: AsyncSession):
        existing_email = await db.execute(
            select(models.User).where(models.User.email == email)
        )
        return existing_email.scalar_one_or_none()

    async def get_user_by_googleId(self,google_id:str,db:AsyncSession):
        result=await db.execute(
            select(models.User).where(models.User.google_id==google_id)
        )
        return result.scalar_one_or_none()

    async def get_user_by_githubID(self,github_id:str,db:AsyncSession):
            result=await db.execute(
                select(models.User).where(models.User.github_id==github_id)
            )
            return result.scalar_one_or_none()

    async def user_exist(self, email: str, db: AsyncSession):
        user = await self.get_user_byemail(email, db)

        return user is not None

    async def register_user(self, user_in: UserRegister, db: AsyncSession):
        # 1. Check if email already exists
        existing_user = await self.user_exist(user_in.email, db)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already registered",
            )

        # 3. Hash password and create user DB object
        new_user = models.User(
            name=user_in.name,
            email=user_in.email,
            hashed_password=hash_password(user_in.password),
            dob=user_in.dob,
            gender=user_in.gender,
            phone_number=user_in.phone_number,
        )

        # 4. Save to database asynchronously
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return new_user






