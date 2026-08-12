from __future__ import annotations
from typing import Optional
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String, ForeignKey, func, Text, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base

class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Generated short ID like #12345
    anketa_number: Mapped[str] = mapped_column(String(16), unique=True, index=True, nullable=False)
    
    # Common fields
    gender: Mapped[str] = mapped_column(String(16), nullable=False) # 'erkak', 'ayol'
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    height: Mapped[int] = mapped_column(Integer, nullable=False)
    weight: Mapped[int] = mapped_column(Integer, nullable=False)
    nationality: Mapped[str] = mapped_column(String(64), nullable=False)
    marital_status: Mapped[str] = mapped_column(String(64), nullable=False)
    location: Mapped[str] = mapped_column(String(128), nullable=False)
    original_location: Mapped[str] = mapped_column(String(128), nullable=False)
    religion: Mapped[str] = mapped_column(String(128), nullable=False)
    languages_count: Mapped[int] = mapped_column(Integer, nullable=False)
    bio: Mapped[str] = mapped_column(Text, nullable=False)
    partner_requirements: Mapped[str] = mapped_column(Text, nullable=False)
    filled_by: Mapped[str] = mapped_column(String(32), nullable=False) # 'ozi', 'vakili'
    
    # Female specific fields
    children_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    hijab: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    relocation: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    second_wife: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    
    # Visibility and Status
    visibility: Mapped[str] = mapped_column(String(32), default="private") # private, public, vip_only
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
