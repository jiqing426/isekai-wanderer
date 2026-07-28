"""Fragment mall API endpoints."""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID
from typing import Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.core.exceptions import AppException, ErrorCode
from app.api.v1.auth import get_current_user_id
from app.models.shop_goods import ShopGoods
from app.models.user_goods import UserGoods
from app.models.payment import Fragment, FragmentTransaction

router = APIRouter(prefix="/fragment", tags=["fragment"])


class ExchangeRequest(BaseModel):
    goods_id: str
    quantity: int = 1


@router.get("/shop/goods")
async def get_shop_goods(
    category: Optional[str] = Query(None, description="Filter by category: cg/voice/skin/item"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Get shop goods list."""
    # Build query
    query = select(ShopGoods).where(ShopGoods.is_active == True)
    
    if category:
        query = query.where(ShopGoods.category == category)
    
    # Get total count
    count_query = select(func.count()).select_from(ShopGoods).where(ShopGoods.is_active == True)
    if category:
        count_query = count_query.where(ShopGoods.category == category)
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Apply pagination
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    goods_list = result.scalars().all()
    
    # Get user's owned goods
    owned_query = select(UserGoods).where(UserGoods.user_id == UUID(user_id))
    owned_result = await db.execute(owned_query)
    owned_goods = {ug.goods_id: ug.quantity for ug in owned_result.scalars().all()}
    
    # Get user's balance
    balance_query = select(Fragment).where(Fragment.user_id == UUID(user_id))
    balance_result = await db.execute(balance_query)
    fragment = balance_result.scalar_one_or_none()
    user_balance = fragment.balance if fragment else 0
    
    # Build response
    goods_response = []
    for goods in goods_list:
        owned_quantity = owned_goods.get(goods.id, 0)
        owned = owned_quantity > 0
        
        # Check availability
        is_available = True
        if goods.stock != -1 and goods.stock <= 0:
            is_available = False
        if goods.limit_per_user > 0 and owned_quantity >= goods.limit_per_user:
            is_available = False
        if user_balance < goods.price:
            is_available = False
        
        goods_response.append({
            "id": str(goods.id),
            "name": goods.name,
            "description": goods.description,
            "category": goods.category,
            "icon_url": goods.icon_url,
            "price": goods.price,
            "stock": goods.stock,
            "limit_per_user": goods.limit_per_user,
            "owned": owned,
            "is_available": is_available,
        })
    
    return {
        "goods": goods_response,
        "total": total,
        "page": page,
        "page_size": page_size,
        "user_balance": user_balance,
    }


@router.post("/exchange")
async def exchange_goods(
    request: ExchangeRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Exchange goods with fragments."""
    # Validate UUID format
    try:
        goods_id = UUID(request.goods_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid goods ID format")
    
    quantity = request.quantity
    
    # 1. Check goods exists and is active
    goods_query = select(ShopGoods).where(ShopGoods.id == goods_id, ShopGoods.is_active == True)
    goods_result = await db.execute(goods_query)
    goods = goods_result.scalar_one_or_none()
    
    if not goods:
        raise AppException(
            error_code=ErrorCode.GOODS_NOT_FOUND,
            status_code=404,
            message="Goods not found"
        )
    
    # 2. Check stock
    if goods.stock != -1 and goods.stock < quantity:
        raise AppException(
            error_code=ErrorCode.GOODS_OUT_OF_STOCK,
            status_code=409,
            message="Insufficient stock"
        )
    
    # 3. Check limit per user
    owned_query = select(UserGoods).where(
        UserGoods.user_id == UUID(user_id),
        UserGoods.goods_id == goods_id
    )
    owned_result = await db.execute(owned_query)
    owned_goods = owned_result.scalar_one_or_none()
    owned_quantity = owned_goods.quantity if owned_goods else 0
    
    if goods.limit_per_user > 0 and owned_quantity + quantity > goods.limit_per_user:
        raise AppException(
            error_code=ErrorCode.GOODS_LIMIT_REACHED,
            status_code=409,
            message="Purchase limit reached"
        )
    
    # 4. Check balance
    total_price = goods.price * quantity
    balance_query = select(Fragment).where(Fragment.user_id == UUID(user_id))
    balance_result = await db.execute(balance_query)
    fragment = balance_result.scalar_one_or_none()
    
    current_balance = fragment.balance if fragment else 0
    if current_balance < total_price:
        raise AppException(
            error_code=ErrorCode.INSUFFICIENT_BALANCE,
            status_code=402,
            message="Insufficient balance"
        )
    
    # 5. Deduct fragments (create Fragment record if not exists)
    if not fragment:
        fragment = Fragment(user_id=UUID(user_id), balance=0)
        db.add(fragment)
    fragment.balance -= total_price
    
    # 6. Record transaction
    transaction = FragmentTransaction(
        user_id=UUID(user_id),
        amount=-total_price,
        reason=f"shop_exchange:{goods_id}",
    )
    db.add(transaction)
    
    # 7. Record purchase
    if owned_goods:
        owned_goods.quantity += quantity
    else:
        new_owned = UserGoods(
            user_id=UUID(user_id),
            goods_id=goods_id,
            quantity=quantity,
        )
        db.add(new_owned)
    
    # 8. Deduct stock
    if goods.stock != -1:
        goods.stock -= quantity
    
    await db.commit()
    
    return {
        "status": "ok",
        "goods_id": str(goods_id),
        "goods_name": goods.name,
        "price": total_price,
        "quantity": quantity,
        "new_balance": fragment.balance,
        "message": "Exchange successful",
    }


@router.get("/transactions")
async def get_transactions(
    type: Optional[str] = Query(None, description="Filter by type: income/expense"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Get fragment transactions."""
    # Build query
    query = select(FragmentTransaction).where(FragmentTransaction.user_id == UUID(user_id))
    
    if type == "income":
        query = query.where(FragmentTransaction.amount > 0)
    elif type == "expense":
        query = query.where(FragmentTransaction.amount < 0)
    
    # Get total count
    count_query = select(func.count()).select_from(FragmentTransaction).where(
        FragmentTransaction.user_id == UUID(user_id)
    )
    if type == "income":
        count_query = count_query.where(FragmentTransaction.amount > 0)
    elif type == "expense":
        count_query = count_query.where(FragmentTransaction.amount < 0)
    
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Apply pagination and ordering
    query = query.order_by(FragmentTransaction.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    transactions = result.scalars().all()
    
    # 交易类型中文映射（支持精确匹配和前缀匹配）
    reason_labels = {
        'daily_checkin': '每日签到',
        'streak_milestone': '连续签到奖励',
        'gift_send': '送礼支出',
        'gift_receive': '收到礼物',
        'gift': '送礼支出',
        'dialogue_quota_purchase': '碎片兑换对话',
        'shop_purchase': '商城购买',
        'refund': '退款',
        'admin_adjustment': '管理员调整',
        'system_reward': '系统奖励',
        'achievement_reward': '成就奖励',
        'achievement_unlock': '成就解锁奖励',
        'recharge': '充值',
        'purchase': '碎片购买',
        'qa_test_topup': '测试充值',
    }
    
    # Build response with description mapping
    transactions_response = []
    for tx in transactions:
        # Generate human-readable description
        description = tx.reason
        reason_label = tx.reason
        
        if tx.reason.startswith("shop_exchange:"):
            # Try to get goods name
            goods_id_str = tx.reason.split(":", 1)[1]
            try:
                goods_query = select(ShopGoods).where(ShopGoods.id == UUID(goods_id_str))
                goods_result = await db.execute(goods_query)
                goods = goods_result.scalar_one_or_none()
                if goods:
                    description = f"兑换：{goods.name}"
                    reason_label = f"兑换：{goods.name}"
            except:
                pass
        elif tx.reason in reason_labels:
            description = reason_labels[tx.reason]
            reason_label = reason_labels[tx.reason]
        elif tx.reason.startswith("achievement_claim:"):
            description = "成就奖励"
            reason_label = "成就奖励"
        elif tx.reason.startswith("streak_milestone_"):
            description = "连续签到奖励"
            reason_label = "连续签到奖励"
        elif tx.reason == "fragment_purchase":
            description = "碎片购买"
            reason_label = "碎片购买"
        else:
            # 前缀匹配：提取冒号前的 key，查找映射
            reason_key = tx.reason.split(':')[0] if ':' in tx.reason else tx.reason
            if reason_key in reason_labels:
                description = reason_labels[reason_key]
                reason_label = reason_labels[reason_key]
        
        transactions_response.append({
            "id": str(tx.id),
            "amount": tx.amount,
            "type": "income" if tx.amount > 0 else "expense",
            "reason": tx.reason,
            "reason_label": reason_label,
            "description": description,
            "created_at": tx.created_at.isoformat(),
        })
    
    return {
        "transactions": transactions_response,
        "total": total,
        "page": page,
        "page_size": page_size,
    }
