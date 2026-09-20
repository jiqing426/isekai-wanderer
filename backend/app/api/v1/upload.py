"""图片上传接口"""

import os
import uuid
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/upload", tags=["upload"])

# 图片存储根目录
UPLOAD_DIR = Path("/app/static/images")


def get_category(filename: str) -> str:
    """根据文件名判断图片分类"""
    filename_lower = filename.lower()
    
    # 剧本大厅相关
    if any(kw in filename_lower for kw in ["剧本大厅", "大厅", "hall", "discover"]):
        return "scripts/hall"
    
    # 剧本封面
    if any(kw in filename_lower for kw in ["封面", "cover", "script"]):
        return "scripts/covers"
    
    # 角色头像
    if any(kw in filename_lower for kw in ["头像", "avatar", "character"]):
        return "characters/avatars"
    
    # 碎片商城
    if any(kw in filename_lower for kw in ["碎片", "fragment", "shard", "商城"]):
        return "shards"
    
    # 默认分类
    return "others"


@router.post("/image")
async def upload_image(file: UploadFile = File(...)):
    """
    上传图片接口
    
    根据文件名自动分类：
    - 包含"剧本大厅"/"大厅"/"hall" → scripts/hall/
    - 包含"封面"/"cover"/"script" → scripts/covers/
    - 包含"头像"/"avatar"/"character" → characters/avatars/
    - 包含"碎片"/"fragment"/"shard"/"商城" → shards/
    - 其他 → others/
    
    返回格式：
    {
        "success": true,
        "url": "http://47.107.174.176:8000/static/images/scripts/covers/xxx.jpg",
        "path": "/static/images/scripts/covers/xxx.jpg",
        "category": "scripts/covers",
        "filename": "xxx.jpg"
    }
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    # 检查文件类型
    allowed_types = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_types)}"
        )
    
    # 确定分类目录
    category = get_category(file.filename)
    target_dir = UPLOAD_DIR / category
    
    # 创建目录
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成唯一文件名（保留原扩展名）
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    target_path = target_dir / unique_filename
    
    # 保存文件
    try:
        with target_path.open("wb") as buffer:
            content = await file.read()
            buffer.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # 生成访问 URL
    relative_path = target_path.relative_to(UPLOAD_DIR)
    url_path = f"/static/images/{relative_path}"
    full_url = f"http://47.107.174.176:8000{url_path}"
    
    return JSONResponse({
        "success": True,
        "url": full_url,
        "path": url_path,
        "category": category,
        "filename": unique_filename,
        "original_filename": file.filename
    })


@router.get("/list")
async def list_uploaded_images():
    """列出所有已上传的图片"""
    images = []
    
    if UPLOAD_DIR.exists():
        for category_dir in UPLOAD_DIR.iterdir():
            if category_dir.is_dir():
                for image_file in category_dir.iterdir():
                    if image_file.is_file() and image_file.suffix.lower() in {".jpg", ".jpeg", ".png", ".gif", ".webp"}:
                        relative_path = image_file.relative_to(UPLOAD_DIR)
                        url_path = f"/static/images/{relative_path}"
                        images.append({
                            "url": f"http://47.107.174.176:8000{url_path}",
                            "path": url_path,
                            "category": category_dir.name,
                            "filename": image_file.name,
                            "size": image_file.stat().st_size
                        })
    
    return {
        "success": True,
        "images": images,
        "total": len(images)
    }
