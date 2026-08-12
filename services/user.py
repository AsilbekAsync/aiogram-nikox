import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from models.referral import Referral

async def get_user_by_tg_id(session: AsyncSession, telegram_id: int) -> Optional[User]:
    stmt = select(User).where(User.telegram_id == telegram_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

async def get_user_by_referral_code(session: AsyncSession, code: str) -> Optional[User]:
    stmt = select(User).where(User.referral_code == code)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

async def create_user(
    session: AsyncSession, 
    telegram_id: int, 
    full_name: str, 
    username: Optional[str] = None
) -> User:
    new_ref_code = str(uuid.uuid4().hex)[:10].upper()
    user = User(
        telegram_id=telegram_id,
        full_name=full_name,
        username=username,
        referral_code=new_ref_code,
        status="unverified_phone"
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

async def register_referral(session: AsyncSession, inviter_id: int, invited_id: int) -> None:
    # Check if referral already exists
    stmt = select(Referral).where(Referral.invited_id == invited_id)
    result = await session.execute(stmt)
    existing = result.scalar_one_or_none()
    
    if not existing:
        referral = Referral(
            inviter_id=inviter_id,
            invited_id=invited_id,
            status="pending"
        )
        session.add(referral)
        await session.commit()
