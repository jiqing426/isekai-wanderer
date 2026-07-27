"""UGC (User Generated Content) API endpoints."""

from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel
from typing import Optional, List

from app.core.database import get_db
from app.core.exceptions import AppException, ErrorCode
from app.api.v1.auth import get_current_user_id
from app.models.ugc import Post, Comment

router = APIRouter(prefix="/ugc", tags=["ugc"])

# 基础关键词过滤
FORBIDDEN_WORDS = ["色情", "暴力", "政治", "赌博", "毒品"]


def filter_content(text: str) -> bool:
    """Check if content contains forbidden words."""
    for word in FORBIDDEN_WORDS:
        if word in text:
            return False
    return True


class PostCreate(BaseModel):
    title: str
    content: str
    image_urls: Optional[List[str]] = None


class CommentCreate(BaseModel):
    content: str


@router.post("/posts")
async def create_post(
    post: PostCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Create a new UGC post."""
    # 内容过滤
    if not filter_content(post.title) or not filter_content(post.content):
        raise AppException(ErrorCode.UGC_FORBIDDEN_CONTENT, 400, "Content contains forbidden words")

    new_post = Post(
        user_id=UUID(user_id),
        title=post.title,
        content=post.content,
        image_urls=",".join(post.image_urls) if post.image_urls else None,
    )
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)

    return {
        "id": str(new_post.id),
        "user_id": str(new_post.user_id),
        "title": new_post.title,
        "content": new_post.content,
        "image_urls": new_post.image_urls,
        "created_at": new_post.created_at.isoformat(),
    }


@router.get("/posts")
async def list_posts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List UGC posts with pagination."""
    offset = (page - 1) * page_size

    # Count total
    from sqlalchemy import func
    count_stmt = select(func.count()).select_from(Post).where(Post.is_deleted == False)
    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    stmt = (
        select(Post)
        .where(Post.is_deleted == False)
        .order_by(desc(Post.created_at))
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    posts = list(result.scalars().all())

    return {
        "posts": [
            {
                "id": str(p.id),
                "user_id": str(p.user_id),
                "title": p.title,
                "content": p.content,
                "image_urls": p.image_urls,
                "like_count": p.like_count,
                "comment_count": p.comment_count,
                "created_at": p.created_at.isoformat(),
            }
            for p in posts
        ],
        "page": page,
        "page_size": page_size,
        "total": total,
    }


@router.get("/posts/{post_id}")
async def get_post(
    post_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a single UGC post."""
    try:
        post_uuid = UUID(post_id)
    except ValueError:
        raise AppException(ErrorCode.VALIDATION_ERROR, 400, "Invalid post_id format: must be UUID")
    
    stmt = select(Post).where(Post.id == post_uuid, Post.is_deleted == False)
    result = await db.execute(stmt)
    post = result.scalar_one_or_none()

    if not post:
        raise AppException(ErrorCode.UGC_POST_NOT_FOUND, 404, "Post not found")

    return {
        "id": str(post.id),
        "user_id": str(post.user_id),
        "title": post.title,
        "content": post.content,
        "image_urls": post.image_urls,
        "like_count": post.like_count,
        "comment_count": post.comment_count,
        "created_at": post.created_at.isoformat(),
    }


@router.post("/posts/{post_id}/view")
async def increment_view_count(
    post_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Increment post view count (BE-BUG-016)."""
    try:
        post_uuid = UUID(post_id)
    except ValueError:
        raise AppException(ErrorCode.VALIDATION_ERROR, 400, "Invalid post_id format: must be UUID")
    
    stmt = select(Post).where(Post.id == post_uuid, Post.is_deleted == False)
    result = await db.execute(stmt)
    post = result.scalar_one_or_none()

    if not post:
        raise AppException(ErrorCode.UGC_POST_NOT_FOUND, 404, "Post not found")

    # Atomic increment using SQL
    from sqlalchemy import update
    await db.execute(
        update(Post)
        .where(Post.id == post_uuid)
        .values(views_count=Post.views_count + 1)
    )
    await db.commit()

    # Refresh to get updated value
    await db.refresh(post)

    return {
        "id": str(post.id),
        "view_count": post.views_count,
        "status": "success",
    }


@router.post("/posts/{post_id}/comments")
async def create_comment(
    post_id: str,
    comment: CommentCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Create a comment on a post."""
    try:
        post_uuid = UUID(post_id)
    except ValueError:
        raise AppException(ErrorCode.VALIDATION_ERROR, 400, "Invalid post_id format: must be UUID")
    
    # 检查帖子是否存在
    stmt = select(Post).where(Post.id == post_uuid, Post.is_deleted == False)
    result = await db.execute(stmt)
    post = result.scalar_one_or_none()

    if not post:
        raise AppException(ErrorCode.UGC_POST_NOT_FOUND, 404, "Post not found")

    # 内容过滤
    if not filter_content(comment.content):
        raise AppException(ErrorCode.UGC_FORBIDDEN_CONTENT, 400, "Content contains forbidden words")

    new_comment = Comment(
        post_id=post_uuid,
        user_id=UUID(user_id),
        content=comment.content,
    )
    db.add(new_comment)

    # 更新评论计数
    post.comment_count += 1

    await db.commit()
    await db.refresh(new_comment)

    return {
        "id": str(new_comment.id),
        "post_id": str(new_comment.post_id),
        "user_id": str(new_comment.user_id),
        "content": new_comment.content,
        "created_at": new_comment.created_at.isoformat(),
    }


@router.get("/posts/{post_id}/comments")
async def list_comments(
    post_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List comments for a post."""
    try:
        post_uuid = UUID(post_id)
    except ValueError:
        raise AppException(ErrorCode.VALIDATION_ERROR, 400, "Invalid post_id format: must be UUID")
    
    # 检查帖子是否存在
    stmt = select(Post).where(Post.id == post_uuid, Post.is_deleted == False)
    result = await db.execute(stmt)
    post = result.scalar_one_or_none()

    if not post:
        raise AppException(ErrorCode.UGC_POST_NOT_FOUND, 404, "Post not found")

    offset = (page - 1) * page_size

    stmt = (
        select(Comment)
        .where(Comment.post_id == post_uuid, Comment.is_deleted == False)
        .order_by(desc(Comment.created_at))
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    comments = list(result.scalars().all())

    return {
        "comments": [
            {
                "id": str(c.id),
                "post_id": str(c.post_id),
                "user_id": str(c.user_id),
                "content": c.content,
                "created_at": c.created_at.isoformat(),
            }
            for c in comments
        ],
        "page": page,
        "page_size": page_size,
    }
