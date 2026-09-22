"""Fragment billing service — replaces dialogue quota with direct fragment deduction (CR-044)."""

import logging
import uuid
import math
from datetime import datetime, timezone, date, timedelta
from typing import Optional
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.payment import Fragment, FragmentTransaction
from app.models.user import User

logger = logging.getLogger(__name__)


class FragmentBillingService:
    """Direct fragment deduction for dialogue and narrative generation."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def _get_fragment_record(self, user_id: uuid.UUID, for_update: bool = False) -> Optional[Fragment]:
        """Get or create fragment record for a user."""
        stmt = select(Fragment).where(Fragment.user_id == user_id)
        if for_update:
            stmt = stmt.with_for_update()
        result = await self.db.execute(stmt)
        frag = result.scalar_one_or_none()
        if not frag:
            frag = Fragment(user_id=user_id, balance=0)
            self.db.add(frag)
            await self.db.flush()
        return frag

    async def get_balance(self, user_id: uuid.UUID) -> int:
        """Get current fragment balance."""
        frag = await self._get_fragment_record(user_id)
        return frag.balance if frag else 0

    async def get_daily_free_remaining(self, user_id: uuid.UUID) -> int:
        """Get remaining free dialogues for today.
        
        Free dialogues are tracked per-day, reset at UTC midnight.
        Uses fragment_transactions with reason 'daily_free' to count today's usage.
        """
        today_start = datetime.combine(date.today(), datetime.min.time(), tzinfo=timezone.utc)
        
        result = await self.db.execute(
            select(func.count()).select_from(FragmentTransaction).where(
                FragmentTransaction.user_id == user_id,
                FragmentTransaction.reason == "daily_free_dialogue",
                FragmentTransaction.created_at >= today_start,
            )
        )
        used_today = result.scalar() or 0
        daily_limit = settings.daily_free_dialogues
        return max(0, daily_limit - used_today)

    async def check_and_deduct_dialogue(self, user_id: uuid.UUID) -> dict:
        """Check and deduct fragments for a normal dialogue.
        
        Logic:
        1. Check if user has free dialogues remaining today
        2. If yes, use free dialogue (no deduction)
        3. If no, deduct dialogue_fragment_cost from balance
        4. If balance insufficient, return error
        
        Returns:
            {"success": bool, "cost": int, "source": "free"|"fragment", "remaining_balance": int, "message": str}
        """
        # 1. Check free dialogues
        free_remaining = await self.get_daily_free_remaining(user_id)
        if free_remaining > 0:
            # Record free dialogue usage
            txn = FragmentTransaction(
                user_id=user_id,
                amount=0,
                reason="daily_free_dialogue",
            )
            self.db.add(txn)
            await self.db.flush()
            balance = await self.get_balance(user_id)
            return {
                "success": True,
                "cost": 0,
                "source": "free",
                "remaining_balance": balance,
                "free_remaining": free_remaining - 1,
                "message": f"免费对话（今日剩余 {free_remaining - 1} 次）",
            }

        # 2. Deduct fragments
        cost = settings.dialogue_fragment_cost
        frag = await self._get_fragment_record(user_id, for_update=True)
        
        if frag.balance < cost:
            return {
                "success": False,
                "cost": cost,
                "source": "fragment",
                "remaining_balance": frag.balance,
                "message": f"碎片不足，需要 {cost} 碎片，当前余额 {frag.balance}",
            }

        frag.balance -= cost
        txn = FragmentTransaction(
            user_id=user_id,
            amount=-cost,
            reason="dialogue_cost",
        )
        self.db.add(txn)
        await self.db.flush()

        return {
            "success": True,
            "cost": cost,
            "source": "fragment",
            "remaining_balance": frag.balance,
            "free_remaining": 0,
            "message": f"扣除 {cost} 碎片，剩余 {frag.balance} 碎片",
        }

    async def check_dialogue_allowed(self, user_id: uuid.UUID) -> dict:
        """Pre-check: can the user send a dialogue right now?
        
        Returns:
            {"allowed": bool, "reason": str, "balance": int, "free_remaining": int}
        """
        balance = await self.get_balance(user_id)
        free_remaining = await self.get_daily_free_remaining(user_id)
        
        if free_remaining > 0:
            return {
                "allowed": True,
                "reason": "free_dialogue",
                "balance": balance,
                "free_remaining": free_remaining,
                "cost_preview": 0,
            }
        
        cost = settings.dialogue_fragment_cost
        if balance >= cost:
            return {
                "allowed": True,
                "reason": "fragment_sufficient",
                "balance": balance,
                "free_remaining": 0,
                "cost_preview": cost,
            }
        
        return {
            "allowed": False,
            "reason": "insufficient_fragments",
            "balance": balance,
            "free_remaining": 0,
            "cost_preview": cost,
        }

    async def deduct_narrative_cost(self, user_id: uuid.UUID, response_char_length: int) -> dict:
        """Deduct fragments for narrative engine response based on character length.
        
        Formula:
            billable_chars = max(0, response_char_length - narrative_free_chars)
            billing_units = ceil(billable_chars / narrative_billing_step)
            cost = billing_units * narrative_cost_per_step
        
        Returns:
            {"success": bool, "cost": int, "billing_units": int, "remaining_balance": int, "message": str}
        """
        free_chars = settings.narrative_free_chars
        billing_step = settings.narrative_billing_step
        cost_per_step = settings.narrative_cost_per_step

        billable = max(0, response_char_length - free_chars)
        billing_units = math.ceil(billable / billing_step) if billing_step > 0 else 0
        cost = billing_units * cost_per_step

        if cost == 0:
            balance = await self.get_balance(user_id)
            return {
                "success": True,
                "cost": 0,
                "billing_units": 0,
                "remaining_balance": balance,
                "message": f"叙事内容 {response_char_length} 字，在免费额度内",
            }

        frag = await self._get_fragment_record(user_id, for_update=True)
        
        if frag.balance < cost:
            return {
                "success": False,
                "cost": cost,
                "billing_units": billing_units,
                "remaining_balance": frag.balance,
                "message": f"碎片不足，叙事内容 {response_char_length} 字需 {cost} 碎片，当前余额 {frag.balance}",
            }

        frag.balance -= cost
        txn = FragmentTransaction(
            user_id=user_id,
            amount=-cost,
            reason=f"narrative_cost:{response_char_length}chars",
        )
        self.db.add(txn)
        await self.db.flush()

        return {
            "success": True,
            "cost": cost,
            "billing_units": billing_units,
            "remaining_balance": frag.balance,
            "message": f"叙事内容 {response_char_length} 字，扣除 {cost} 碎片，剩余 {frag.balance}",
        }

    async def refund(self, user_id: uuid.UUID, amount: int, reason: str) -> None:
        """Refund fragments (e.g., when dialogue generation fails)."""
        frag = await self._get_fragment_record(user_id, for_update=True)
        frag.balance += amount
        txn = FragmentTransaction(
            user_id=user_id,
            amount=amount,
            reason=f"refund:{reason}",
        )
        self.db.add(txn)
        await self.db.flush()
