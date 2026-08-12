from typing import Optional
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, String, Text, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class FSMState(Base):
    __tablename__ = "fsm_states"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    bot_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    destiny: Mapped[str] = mapped_column(String(32), default="default")
    state: Mapped[str] = mapped_column(String(255), nullable=True)
    data: Mapped[str] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("bot_id", "chat_id", "user_id", "destiny", name="uq_fsm_key"),
    )
