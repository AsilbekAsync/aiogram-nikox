from __future__ import annotations
from typing import Optional
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String, ForeignKey, func, Text
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    amount: Mapped[int] = mapped_column(BigInteger, nullable=False)  # positive for credit, negative for debit
    type: Mapped[str] = mapped_column(String(64), nullable=False)  # welcome_bonus, referral_bonus, deposit, etc.
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    before_balance: Mapped[int] = mapped_column(BigInteger, nullable=False)
    after_balance: Mapped[int] = mapped_column(BigInteger, nullable=False)
    reference_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
