from __future__ import annotations
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String, ForeignKey, func, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base

class MatchRequest(Base):
    __tablename__ = "match_requests"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    sender_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    receiver_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    
    # pending, accepted, rejected
    status: Mapped[str] = mapped_column(String(32), default="pending")
    
    # Whether the sender paid a fee (so we can refund if rejected)
    fee_paid: Mapped[bool] = mapped_column(Boolean, default=False)
    fee_amount: Mapped[int] = mapped_column(BigInteger, default=0)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    match_request_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("match_requests.id", ondelete="CASCADE"), unique=True)
    
    user1_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    user2_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
