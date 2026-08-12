from datetime import datetime
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from models.transaction import Transaction
from models.referral import Referral

from config import WELCOME_BONUS_UZS, REFERRAL_BONUS_UZS

async def verify_phone_and_give_bonus(session: AsyncSession, user: User, phone: str):
    # Idempotency check
    if user.status != "unverified_phone":
        return

    # Update user
    user.phone = phone
    user.status = "profile_incomplete"
    user.verified_at = datetime.now()
    
    # Add welcome bonus
    before_balance = user.balance
    after_balance = before_balance + WELCOME_BONUS_UZS
    user.balance = after_balance
    
    # Create transaction
    tx = Transaction(
        user_id=user.id,
        amount=WELCOME_BONUS_UZS,
        type="welcome_bonus",
        description="Yangi foydalanuvchi uchun bonus",
        before_balance=before_balance,
        after_balance=after_balance
    )
    session.add(tx)
    
    # Process referral if exists
    stmt = select(Referral).where(Referral.invited_id == user.id, Referral.status == "pending")
    result = await session.execute(stmt)
    referral = result.scalar_one_or_none()
    
    if referral:
        # Get inviter
        stmt = select(User).where(User.id == referral.inviter_id).with_for_update()
        inviter_res = await session.execute(stmt)
        inviter = inviter_res.scalar_one_or_none()
        
        if inviter:
            inv_before = inviter.balance
            inv_after = inv_before + REFERRAL_BONUS_UZS
            inviter.balance = inv_after
            
            ref_tx = Transaction(
                user_id=inviter.id,
                amount=REFERRAL_BONUS_UZS,
                type="referral_bonus",
                description="Do'stni taklif qilganlik uchun bonus",
                before_balance=inv_before,
                after_balance=inv_after,
                reference_id=str(user.id)
            )
            session.add(ref_tx)
            
            referral.status = "completed"
            referral.completed_at = datetime.now()
            referral.reward_amount = REFERRAL_BONUS_UZS
            
    await session.commit()
