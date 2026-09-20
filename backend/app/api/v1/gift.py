"""Gift API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from typing import List

from app.core.database import get_db
from app.api.v1.dependencies import get_current_user
from app.models.gift_record import GiftRecord
from app.models.affection import Affection
from app.models.script import Character
from app.models.payment import Fragment, FragmentTransaction
from app.schemas.gift import GiftRequest, GiftResponse, GiftRecordResponse

router = APIRouter(prefix="/game", tags=["gift"])

# 角色聊天页面的送礼 API（不需要 session_id）
gift_router = APIRouter(prefix="/gifts", tags=["gifts"])


@router.post("/{session_id}/gift", response_model=GiftResponse)
async def send_gift(
    session_id: UUID,
    gift_request: GiftRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Send a gift to a character"""
    # 验证角色存在
    try:
        character_uuid = UUID(gift_request.character_id)
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid character_id format: {gift_request.character_id}"
        )
    
    character = await db.get(Character, character_uuid)
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )
    
    # 验证礼物存在
    from app.models.gift import Gift
    gift = await db.get(Gift, gift_request.gift_id)
    if not gift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gift not found"
        )
    
    # 检查用户碎片是否足够 — FIX T-001: query by user_id, not PK
    result = await db.execute(
        select(Fragment).where(Fragment.user_id == current_user.id)
    )
    user_fragments = result.scalar_one_or_none()
    
    if not user_fragments or user_fragments.balance < gift.price:
        current_balance = user_fragments.balance if user_fragments else 0
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient fragments. Need {gift.price}, have {current_balance}"
        )
    
    # 扣除碎片
    user_fragments.balance -= gift.price
    
    # 记录碎片交易
    txn = FragmentTransaction(
        user_id=current_user.id,
        amount=-gift.price,
        reason=f"gift:{gift_request.gift_id}",
    )
    db.add(txn)
    
    # 增加好感度
    affection = await db.execute(
        select(Affection).where(
            Affection.user_id == current_user.id,
            Affection.character_id == character_uuid
        )
    )
    affection_record = affection.scalar_one_or_none()
    
    if not affection_record:
        affection_record = Affection(
            user_id=current_user.id,
            character_id=character_uuid,
            value=gift.affection_bonus
        )
        db.add(affection_record)
    else:
        affection_record.value += gift.affection_bonus
    
    # 记录送礼历史
    gift_record = GiftRecord(
        user_id=current_user.id,
        session_id=session_id,
        character_id=character_uuid,
        gift_id=gift_request.gift_id,
        gift_name=gift.name,
        quantity=gift_request.quantity,
        affection_delta=gift.affection_bonus
    )
    db.add(gift_record)
    
    await db.commit()
    
    return GiftResponse(
        status="success",
        message=f"Successfully sent {gift.name} to {character.name}",
        affection_delta=gift.affection_bonus,
        new_affection=affection_record.value,
        fragments_spent=gift.price,
        remaining_fragments=user_fragments.balance
    )


@router.get("/{session_id}/gift-history")
async def get_gift_history(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Get gift history for a session.
    
    FIX: 不再按 session_id 过滤，返回该用户的所有送礼记录。
    送礼记录应该跟角色绑定，不跟 session 绑定。
    """
    result = await db.execute(
        select(GiftRecord)
        .where(
            GiftRecord.user_id == current_user.id
        )
        .order_by(GiftRecord.created_at.desc())
    )
    records = result.scalars().all()
    
    # 批量查询角色名称
    character_ids = [record.character_id for record in records]
    if character_ids:
        char_result = await db.execute(
            select(Character).where(Character.id.in_(character_ids))
        )
        char_map = {str(c.id): c.name for c in char_result.scalars().all()}
    else:
        char_map = {}
    
    gifts = [
        GiftRecordResponse(
            id=str(record.id),
            character_id=str(record.character_id),
            character_name=char_map.get(str(record.character_id), "未知角色"),
            gift_id=record.gift_id,
            gift_name=record.gift_name,
            quantity=record.quantity,
            affection_delta=record.affection_delta,
            created_at=record.created_at.isoformat()
        )
        for record in records
    ]
    
    return {
        "gifts": gifts,
        "total": len(gifts)
    }


# 角色聊天页面的送礼 API（不需要 session_id）
@gift_router.get("/available")
async def get_available_gifts(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Get available gifts for character chat"""
    from app.models.gift import Gift
    
    result = await db.execute(
        select(Gift).order_by(Gift.price)
    )
    gifts = result.scalars().all()
    
    return {
        "gifts": [
            {
                "id": str(gift.id),
                "name": gift.name,
                "description": gift.description,
                "price": gift.price,
                "affection_bonus": gift.affection_bonus,
                "icon": gift.icon_url or "🎁"
            }
            for gift in gifts
        ]
    }


@gift_router.post("/send")
async def send_gift_to_character(
    gift_request: GiftRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Send a gift to a character (for character chat, no session_id needed)"""
    # 验证角色存在
    try:
        character_uuid = UUID(gift_request.character_id)
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid character_id format: {gift_request.character_id}"
        )
    
    character = await db.get(Character, character_uuid)
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )
    
    # 验证礼物存在
    from app.models.gift import Gift
    gift = await db.get(Gift, gift_request.gift_id)
    if not gift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gift not found"
        )
    
    # 检查用户碎片是否足够
    result = await db.execute(
        select(Fragment).where(Fragment.user_id == current_user.id)
    )
    user_fragments = result.scalar_one_or_none()
    
    if not user_fragments or user_fragments.balance < gift.price:
        current_balance = user_fragments.balance if user_fragments else 0
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient fragments. Need {gift.price}, have {current_balance}"
        )
    
    # 扣除碎片
    user_fragments.balance -= gift.price
    
    # 记录碎片交易
    txn = FragmentTransaction(
        user_id=current_user.id,
        amount=-gift.price,
        reason=f"gift:{gift_request.gift_id}",
    )
    db.add(txn)
    
    # 增加好感度
    affection = await db.execute(
        select(Affection).where(
            Affection.user_id == current_user.id,
            Affection.character_id == character_uuid
        )
    )
    affection_record = affection.scalar_one_or_none()
    
    if not affection_record:
        affection_record = Affection(
            user_id=current_user.id,
            character_id=character_uuid,
            value=gift.affection_bonus
        )
        db.add(affection_record)
    else:
        affection_record.value += gift.affection_bonus
    
    # 记录送礼历史（session_id 设为 None）
    gift_record = GiftRecord(
        user_id=current_user.id,
        session_id=None,  # 角色聊天不需要 session_id
        character_id=character_uuid,
        gift_id=gift_request.gift_id,
        gift_name=gift.name,
        quantity=gift_request.quantity,
        affection_delta=gift.affection_bonus
    )
    db.add(gift_record)
    
    await db.commit()
    
    return {
        "status": "success",
        "message": f"Successfully sent {gift.name} to {character.name}",
        "new_affection_value": affection_record.value,
        "remaining_shards": user_fragments.balance
    }


@gift_router.get("/history")
async def get_all_gift_history(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Get gift history for all characters (BUG-029-003 fix)"""
    result = await db.execute(
        select(GiftRecord)
        .where(GiftRecord.user_id == current_user.id)
        .order_by(GiftRecord.created_at.desc())
    )
    records = result.scalars().all()

    # Batch query character names
    character_ids = list(set(str(r.character_id) for r in records))
    char_map = {}
    if character_ids:
        char_result = await db.execute(
            select(Character).where(Character.id.in_([UUID(cid) for cid in character_ids]))
        )
        char_map = {str(c.id): c.name for c in char_result.scalars().all()}

    return {
        "history": [
            {
                "id": str(record.id),
                "character_name": char_map.get(str(record.character_id), "未知角色"),
                "gift_name": record.gift_name,
                "gift_icon": "🎁",
                "affection_change": record.affection_delta,
                "created_at": record.created_at.isoformat()
            }
            for record in records
        ]
    }


@gift_router.get("/history/{character_id}")
async def get_character_gift_history(
    character_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Get gift history for a specific character"""
    result = await db.execute(
        select(GiftRecord)
        .where(
            GiftRecord.user_id == current_user.id,
            GiftRecord.character_id == character_id
        )
        .order_by(GiftRecord.created_at.desc())
    )
    records = result.scalars().all()
    
    return {
        "history": [
            {
                "id": str(record.id),
                "gift_name": record.gift_name,
                "gift_icon": "🎁",  # 默认图标
                "affection_change": record.affection_delta,
                "created_at": record.created_at.isoformat()
            }
            for record in records
        ]
    }
