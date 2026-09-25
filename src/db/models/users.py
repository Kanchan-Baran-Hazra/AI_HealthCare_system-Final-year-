from src.db.main import Base
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime,date
from sqlalchemy import String, DateTime, func, UUID, Text,Date,Enum
import uuid
from sqlalchemy import Enum as SQLEnum
import enum
from typing import Optional


# 1. Define valid roles
class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"


# Optional: Define an Enum for Gender to enforce clean data
class GenderEnum(str, enum.Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,  # Auto-generates a UUID v4
    )
    name: Mapped[str] = mapped_column(String(225), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    # Added fields
    dob: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    gender: Mapped[Optional[GenderEnum]] = mapped_column(
        Enum(GenderEnum, native_enum=True), nullable=True
    )
    phone_number: Mapped[Optional[str]] = mapped_column(
        String(20), unique=True, index=True, nullable=True
    )
    # username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    google_id: Mapped[str | None] = mapped_column(
        String(255), unique=True, nullable=True
    )
    github_id: Mapped[str | None] = mapped_column(
        String(255), unique=True, nullable=True
    )
    facebook_id: Mapped[str | None] = mapped_column(
        String(255), unique=True, nullable=True
    )
    profile_picture: Mapped[str | None] = mapped_column(Text, nullable=True)
    auth_provider: Mapped[str] = mapped_column(
        String(50), default="local", nullable=True
    )
    is_verified: Mapped[bool] = mapped_column(default=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    # Role field with default value
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, native_enum=False),
        default=UserRole.USER,
        nullable=False,
    )

    def __repr__(self):
        return f"User:-->> {self.email} || Name:-->{self.name}"