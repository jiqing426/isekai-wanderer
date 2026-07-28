"""CR3-018: Fragment/Shard statistics and visualization API."""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.exceptions import AppException, ErrorCode
from app.api.v1.auth import get_current_user_id
from app.models.payment import Fragment, FragmentTransaction


router = APIRouter(prefix="/shards", tags=["shards"])


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────


# 交易类型中文映射
REASON_LABELS = {
    "daily_checkin": "每日签到",
    "streak_milestone": "连续签到奖励",
    "gift_send": "送礼支出",
    "gift_receive": "收到礼物",
    "gift": "送礼支出",
    "dialogue_quota_purchase": "碎片兑换对话",
    "shop_purchase": "商城购买",
    "shop_exchange": "碎片兑换商品",
    "refund": "退款",
    "admin_adjustment": "管理员调整",
    "system_reward": "系统奖励",
    "achievement_reward": "成就奖励",
    "achievement_unlock": "成就解锁奖励",
    "achievement_claim": "成就奖励",
    "recharge": "充值",
    "purchase": "碎片购买",
    "qa_test_topup": "测试充值",
}


def _get_reason_label(reason: str) -> str:
    """将交易类型映射为中文标签"""
    # 1. 精确匹配
    if reason in REASON_LABELS:
        return REASON_LABELS[reason]
    
    # 2. 提取基础类型（去除 : 后的参数）
    base_type = reason.split(":")[0] if ":" in reason else reason
    if base_type in REASON_LABELS:
        return REASON_LABELS[base_type]
    
    # 3. 前缀匹配（如 streak_milestone_day_3）
    for key, label in REASON_LABELS.items():
        if reason.startswith(key):
            return label
    
    # 4. 默认返回原始值
    return reason


def _transaction_to_entry(tx: FragmentTransaction) -> dict:
    return {
        "id": str(tx.id),
        "amount": tx.amount,
        "reason": tx.reason,
        "reason_label": _get_reason_label(tx.reason),
        "created_at": tx.created_at.isoformat() if tx.created_at else None,
    }


# ──────────────────────────────────────────────
# CR3-018: Fragment balance and transactions
# ──────────────────────────────────────────────


@router.get("/balance")
async def get_shard_balance(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    CR3-018 (AC-SHARD-001): Get current fragment balance.
    """
    uid = uuid.UUID(user_id)

    result = await db.execute(
        select(Fragment).where(Fragment.user_id == uid)
    )
    fragment = result.scalar_one_or_none()
    balance = fragment.balance if fragment else 0

    # Recent transaction count
    tx_count_result = await db.execute(
        select(func.count(FragmentTransaction.id)).where(
            FragmentTransaction.user_id == uid
        )
    )
    tx_count = tx_count_result.scalar() or 0

    # Total earned (positive amounts)
    earned_result = await db.execute(
        select(func.coalesce(func.sum(FragmentTransaction.amount), 0)).where(
            FragmentTransaction.user_id == uid,
            FragmentTransaction.amount > 0,
        )
    )
    lifetime_earned = int(earned_result.scalar() or 0)

    # Total spent (negative amounts)
    spent_result = await db.execute(
        select(func.coalesce(func.sum(func.abs(FragmentTransaction.amount)), 0)).where(
            FragmentTransaction.user_id == uid,
            FragmentTransaction.amount < 0,
        )
    )
    lifetime_spent = int(spent_result.scalar() or 0)

    return {
        "user_id": user_id,
        "balance": balance,
        "lifetime_earned": lifetime_earned,
        "lifetime_spent": lifetime_spent,
        "total_transactions": tx_count,
    }


@router.get("/transactions")
async def get_shard_transactions(
    limit: int = 50,
    offset: int = 0,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    CR3-018 (AC-SHARD-002): Get fragment transaction history.
    """
    uid = uuid.UUID(user_id)

    # Total count
    count_result = await db.execute(
        select(func.count(FragmentTransaction.id)).where(
            FragmentTransaction.user_id == uid
        )
    )
    total = count_result.scalar() or 0

    stmt = (
        select(FragmentTransaction)
        .where(FragmentTransaction.user_id == uid)
        .order_by(FragmentTransaction.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(stmt)
    transactions = list(result.scalars().all())

    return {
        "transactions": [_transaction_to_entry(tx) for tx in transactions],
        "total": total,
        "offset": offset,
        "limit": limit,
    }


@router.get("/summary")
async def get_shard_summary(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    CR3-018 (AC-SHARD-003): Get fragment earning/spending summary.
    """
    uid = uuid.UUID(user_id)

    # Current balance
    frag_result = await db.execute(
        select(Fragment).where(Fragment.user_id == uid)
    )
    fragment = frag_result.scalar_one_or_none()
    balance = fragment.balance if fragment else 0

    # Total earned (positive amounts)
    earned_result = await db.execute(
        select(func.coalesce(func.sum(FragmentTransaction.amount), 0)).where(
            FragmentTransaction.user_id == uid,
            FragmentTransaction.amount > 0,
        )
    )
    total_earned = earned_result.scalar() or 0

    # Total spent (negative amounts)
    spent_result = await db.execute(
        select(func.coalesce(func.sum(func.abs(FragmentTransaction.amount)), 0)).where(
            FragmentTransaction.user_id == uid,
            FragmentTransaction.amount < 0,
        )
    )
    total_spent = spent_result.scalar() or 0

    # Transaction count
    count_result = await db.execute(
        select(func.count(FragmentTransaction.id)).where(
            FragmentTransaction.user_id == uid
        )
    )
    tx_count = count_result.scalar() or 0

    # Breakdown by reason
    reason_result = await db.execute(
        select(FragmentTransaction.reason, func.sum(FragmentTransaction.amount))
        .where(FragmentTransaction.user_id == uid)
        .group_by(FragmentTransaction.reason)
    )
    by_reason = {r: (amt or 0) for r, amt in reason_result.all()}

    return {
        "balance": balance,
        "total_earned": int(total_earned),
        "total_spent": int(total_spent),
        "total_transactions": tx_count,
        "by_reason": by_reason,
    }
