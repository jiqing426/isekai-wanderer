"""Community API endpoints."""

from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.api.v1.auth import get_current_user_id, get_current_user_id_optional
from app.models.ugc import Post, PostLike, Comment
from app.models.user import User
from pydantic import BaseModel

router = APIRouter(prefix="/community/posts", tags=["community"])


class PostCreate(BaseModel):
    title: str
    content: str
    image_urls: Optional[str] = None


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    image_urls: Optional[str] = None


class CommentCreate(BaseModel):
    content: str


@router.get("")
async def list_posts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    tab: str = Query("latest", regex="^(recommend|latest|hot|mine)$"),
    user_id: Optional[str] = Depends(get_current_user_id_optional),
    db: AsyncSession = Depends(get_db),
):
    """List all posts with pagination and tab-based sorting."""
    offset = (page - 1) * page_size
    
    # Base query
    base_query = select(Post).where(Post.is_deleted == False)
    
    # Apply tab-specific filters and ordering
    if tab == "mine":
        if not user_id:
            return {"posts": [], "total": 0, "page": page, "page_size": page_size, "has_more": False}
        base_query = base_query.where(Post.user_id == UUID(user_id))
        order_by = desc(Post.created_at)
    elif tab == "hot":
        # Hot posts: order by views_count + like_count * 10 + comment_count * 5
        order_by = desc(Post.views_count + Post.like_count * 10 + Post.comment_count * 5)
    elif tab == "recommend":
        # Recommend: order by like_count (most liked)
        order_by = desc(Post.like_count)
    else:  # latest
        order_by = desc(Post.created_at)
    
    # Get total count
    count_stmt = select(func.count()).select_from(base_query.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar()
    
    # Get posts with author info
    stmt = base_query.order_by(order_by).offset(offset).limit(page_size)
    result = await db.execute(stmt)
    posts = result.scalars().all()
    
    # Fetch author info for all posts
    user_ids = list(set(str(post.user_id) for post in posts))
    users_stmt = select(User).where(User.id.in_(user_ids))
    users_result = await db.execute(users_stmt)
    users = {str(u.id): u for u in users_result.scalars().all()}
    
    # Fetch user's likes for all posts
    user_liked_posts = set()
    if user_id:
        post_ids = [post.id for post in posts]
        if post_ids:
            likes_stmt = select(PostLike.post_id).where(
                PostLike.user_id == UUID(user_id),
                PostLike.post_id.in_(post_ids)
            )
            likes_result = await db.execute(likes_stmt)
            user_liked_posts = {str(post_id) for post_id in likes_result.scalars().all()}
    
    return {
        "posts": [
            {
                "id": str(post.id),
                "user_id": str(post.user_id),
                "author": {
                    "id": str(post.user_id),
                    "name": users.get(str(post.user_id)).display_name or users.get(str(post.user_id)).email.split('@')[0] if users.get(str(post.user_id)) else "Unknown",
                    "avatar": users.get(str(post.user_id)).avatar_url if users.get(str(post.user_id)) else None,
                },
                "title": post.title,
                "content": post.content,
                "image_urls": post.image_urls,
                "like_count": post.like_count,
                "comment_count": post.comment_count,
                "views_count": post.views_count,
                "is_liked": str(post.id) in user_liked_posts,
                "created_at": post.created_at.isoformat(),
                "updated_at": post.updated_at.isoformat() if post.updated_at else None,
            }
            for post in posts
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "has_more": offset + page_size < total,
    }


@router.get("/{post_id}")
async def get_post(
    post_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a single post by ID."""
    stmt = select(Post).where(Post.id == post_id, Post.is_deleted == False)
    result = await db.execute(stmt)
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Increment views count
    post.views_count += 1
    await db.commit()
    
    return {
        "id": str(post.id),
        "user_id": str(post.user_id),
        "title": post.title,
        "content": post.content,
        "image_urls": post.image_urls,
        "like_count": post.like_count,
        "comment_count": post.comment_count,
        "views_count": post.views_count,
        "created_at": post.created_at.isoformat(),
        "updated_at": post.updated_at.isoformat() if post.updated_at else None,
    }


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: PostCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Create a new post."""
    post = Post(
        user_id=UUID(user_id),
        title=post_data.title,
        content=post_data.content,
        image_urls=post_data.image_urls,
    )
    db.add(post)
    await db.commit()
    await db.refresh(post)
    
    return {
        "id": str(post.id),
        "user_id": str(post.user_id),
        "title": post.title,
        "content": post.content,
        "image_urls": post.image_urls,
        "like_count": post.like_count,
        "comment_count": post.comment_count,
        "views_count": post.views_count,
        "created_at": post.created_at.isoformat(),
        "updated_at": post.updated_at.isoformat() if post.updated_at else None,
    }


@router.put("/{post_id}")
async def update_post(
    post_id: UUID,
    post_data: PostUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Update a post (only owner can update)."""
    stmt = select(Post).where(Post.id == post_id, Post.is_deleted == False)
    result = await db.execute(stmt)
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    if str(post.user_id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own posts"
        )
    
    if post_data.title is not None:
        post.title = post_data.title
    if post_data.content is not None:
        post.content = post_data.content
    if post_data.image_urls is not None:
        post.image_urls = post_data.image_urls
    
    await db.commit()
    await db.refresh(post)
    
    return {
        "id": str(post.id),
        "user_id": str(post.user_id),
        "title": post.title,
        "content": post.content,
        "image_urls": post.image_urls,
        "like_count": post.like_count,
        "comment_count": post.comment_count,
        "views_count": post.views_count,
        "created_at": post.created_at.isoformat(),
        "updated_at": post.updated_at.isoformat() if post.updated_at else None,
    }


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Soft delete a post (only owner can delete)."""
    stmt = select(Post).where(Post.id == post_id, Post.is_deleted == False)
    result = await db.execute(stmt)
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    if str(post.user_id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own posts"
        )
    
    post.is_deleted = True
    await db.commit()
    
    return None


@router.post("/{post_id}/like", status_code=status.HTTP_201_CREATED)
async def like_post(
    post_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Like a post."""
    # Check if post exists
    stmt = select(Post).where(Post.id == post_id, Post.is_deleted == False)
    result = await db.execute(stmt)
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Check if already liked
    like_stmt = select(PostLike).where(
        PostLike.user_id == UUID(user_id),
        PostLike.post_id == post_id
    )
    like_result = await db.execute(like_stmt)
    existing_like = like_result.scalar_one_or_none()
    
    if existing_like:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post already liked"
        )
    
    # Create like
    like = PostLike(
        user_id=UUID(user_id),
        post_id=post_id
    )
    db.add(like)
    
    # Increment like count
    post.like_count += 1
    await db.commit()
    
    return {
        "message": "Post liked successfully",
        "likes_count": post.like_count
    }


@router.delete("/{post_id}/like")
async def unlike_post(
    post_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Unlike a post."""
    # Check if post exists
    stmt = select(Post).where(Post.id == post_id, Post.is_deleted == False)
    result = await db.execute(stmt)
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Check if liked
    like_stmt = select(PostLike).where(
        PostLike.user_id == UUID(user_id),
        PostLike.post_id == post_id
    )
    like_result = await db.execute(like_stmt)
    like = like_result.scalar_one_or_none()
    
    if not like:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post not liked"
        )
    
    # Delete like
    await db.delete(like)
    
    # Decrement like count
    post.like_count = max(0, post.like_count - 1)
    await db.commit()
    
    return {
        "message": "Post unliked successfully",
        "likes_count": post.like_count
    }


@router.get("/{post_id}/likes")
async def get_post_likes(
    post_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Get users who liked a post."""
    offset = (page - 1) * page_size
    
    # Get total count
    count_stmt = select(func.count()).select_from(PostLike).where(PostLike.post_id == post_id)
    total_result = await db.execute(count_stmt)
    total = total_result.scalar()
    
    # Get likes with user info
    stmt = (
        select(PostLike, User)
        .join(User, PostLike.user_id == User.id)
        .where(PostLike.post_id == post_id)
        .order_by(desc(PostLike.created_at))
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    likes = result.all()
    
    return {
        "likes": [
            {
                "user_id": str(like.user_id),
                "username": user.username,
                "created_at": like.created_at.isoformat(),
            }
            for like, user in likes
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


# ========== Comment Endpoints ==========

@router.get("/{post_id}/comments")
async def get_post_comments(
    post_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Get comments for a post."""
    # Check if post exists
    post_stmt = select(Post).where(Post.id == post_id, Post.is_deleted == False)
    post_result = await db.execute(post_stmt)
    post = post_result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    offset = (page - 1) * page_size
    
    # Get total count
    count_stmt = select(func.count()).select_from(Comment).where(
        Comment.post_id == post_id,
        Comment.is_deleted == False
    )
    total_result = await db.execute(count_stmt)
    total = total_result.scalar()
    
    # Get comments with author info
    stmt = (
        select(Comment, User)
        .join(User, Comment.user_id == User.id)
        .where(Comment.post_id == post_id, Comment.is_deleted == False)
        .order_by(desc(Comment.created_at))
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    comments = result.all()
    
    return {
        "comments": [
            {
                "id": str(comment.id),
                "post_id": str(comment.post_id),
                "user_id": str(comment.user_id),
                "author_name": user.display_name or user.email.split('@')[0],
                "author_avatar": user.avatar_url,
                "content": comment.content,
                "created_at": comment.created_at.isoformat(),
            }
            for comment, user in comments
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("/{post_id}/comments", status_code=status.HTTP_201_CREATED)
async def create_comment(
    post_id: UUID,
    comment_data: CommentCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Create a comment on a post."""
    # Check if post exists
    post_stmt = select(Post).where(Post.id == post_id, Post.is_deleted == False)
    post_result = await db.execute(post_stmt)
    post = post_result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Create comment
    comment = Comment(
        post_id=post_id,
        user_id=UUID(user_id),
        content=comment_data.content,
    )
    db.add(comment)
    
    # Increment comment count
    post.comment_count += 1
    
    await db.commit()
    await db.refresh(comment)
    
    # Fetch user info
    user_stmt = select(User).where(User.id == UUID(user_id))
    user_result = await db.execute(user_stmt)
    user = user_result.scalar_one()
    
    return {
        "id": str(comment.id),
        "post_id": str(comment.post_id),
        "user_id": str(comment.user_id),
        "author_name": user.display_name or user.email.split('@')[0],
        "author_avatar": user.avatar_url,
        "content": comment.content,
        "created_at": comment.created_at.isoformat(),
    }


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Delete a comment (only owner can delete)."""
    # Get comment
    comment_stmt = select(Comment).where(
        Comment.id == comment_id,
        Comment.is_deleted == False
    )
    comment_result = await db.execute(comment_stmt)
    comment = comment_result.scalar_one_or_none()
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    # Check ownership
    if str(comment.user_id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own comments"
        )
    
    # Soft delete
    comment.is_deleted = True
    
    # Decrement post comment count
    post_stmt = select(Post).where(Post.id == comment.post_id)
    post_result = await db.execute(post_stmt)
    post = post_result.scalar_one()
    post.comment_count = max(0, post.comment_count - 1)
    
    await db.commit()
    
    return None
