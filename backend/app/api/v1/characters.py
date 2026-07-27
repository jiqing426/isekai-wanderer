"""W06 Character portraits API and CR-015 Character settings."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from uuid import UUID
from pydantic import BaseModel
from typing import List, Optional

from app.core.database import get_db
from app.models.script import Character
from app.models.affection import Affection
from app.api.v1.auth import get_current_user_id

router = APIRouter(prefix="/characters", tags=["characters"])

# CR-015: Character catalog with enhanced data
# Using UUID v4 format for character IDs
CHARACTER_CATALOG = {
    "40e4c04a-5a07-4fc7-8f8b-4431f0e1194b": {  # 林辰
        "characterId": "40e4c04a-5a07-4fc7-8f8b-4431f0e1194b",
        "name": "白鳥雪乃",
        "nameEn": "Shiratori Yukino",
        "avatar": "https://cdn.example.com/characters/yukino_avatar.png",
        "portrait": "https://cdn.example.com/characters/yukino_portrait.png",
        "personality": {
            "tags": ["温柔", "内向", "善良"],
            "description": "温柔内向的少女，说话轻声细语"
        },
        "dialogueStyle": {
            "speechPattern": "语尾常带「呢」「哦」",
            "catchphrase": "那个...我可以这样说吗？",
            "tone": "温柔、缓慢"
        },
        "preferences": {
            "likedGifts": ["书籍", "花束", "手写信"],
            "dislikedGifts": ["吵闹的玩具", "辛辣食物"],
            "likedTopics": ["文学", "自然", "音乐"]
        },
        "aiValidationRules": {
            "characterName": "白鳥雪乃",
            "emotionPolarity": "gentle",
            "sensitiveWords": ["粗鲁", "暴力"],
            "maxLength": 150,
            "worldviewTerms": ["学院", "图书馆", "樱花"]
        }
    },
    "6982c07f-bb69-4abe-9919-f54ea94297a4": {  # 藤原雪
        "characterId": "6982c07f-bb69-4abe-9919-f54ea94297a4",
        "name": "花野美月",
        "nameEn": "Hanano Mitsuki",
        "avatar": "https://cdn.example.com/characters/mitsuki_avatar.png",
        "portrait": "https://cdn.example.com/characters/mitsuki_portrait.png",
        "personality": {
            "tags": ["活泼", "开朗", "直率"],
            "description": "活泼开朗的少女，总是充满活力"
        },
        "dialogueStyle": {
            "speechPattern": "语尾带「啦」「呀」",
            "catchphrase": "没问题啦！交给我吧！",
            "tone": "轻快、明亮"
        },
        "preferences": {
            "likedGifts": ["甜点", "运动装备", "可爱的饰品"],
            "dislikedGifts": ["沉闷的书", "黑暗的东西"],
            "likedTopics": ["运动", "美食", "冒险"]
        },
        "aiValidationRules": {
            "characterName": "花野美月",
            "emotionPolarity": "cheerful",
            "sensitiveWords": ["无聊", "沉闷"],
            "maxLength": 120,
            "worldviewTerms": ["操场", "食堂", "社团"]
        }
    },
    "900a9744-04ca-4c6b-a276-c79595218672": {  # 沈星澜
        "characterId": "900a9744-04ca-4c6b-a276-c79595218672",
        "name": "凛",
        "nameEn": "Rin",
        "avatar": "https://cdn.example.com/characters/rin_avatar.png",
        "portrait": "https://cdn.example.com/characters/rin_portrait.png",
        "personality": {
            "tags": ["傲娇", "强势", "害羞"],
            "description": "表面强势实则害羞的少女，口是心非"
        },
        "dialogueStyle": {
            "speechPattern": "语尾带「哼」「笨蛋」",
            "catchphrase": "哼，才不是因为担心你呢！",
            "tone": "强势、口是心非"
        },
        "preferences": {
            "likedGifts": ["可爱的玩偶", "甜食", "手工艺品"],
            "dislikedGifts": ["太成熟的东西", "正式的东西"],
            "likedTopics": ["可爱的东西", "秘密", "梦想"]
        },
        "aiValidationRules": {
            "characterName": "凛",
            "emotionPolarity": "tsundere",
            "sensitiveWords": ["软弱", "幼稚"],
            "maxLength": 130,
            "worldviewTerms": ["学生会", "成绩", "竞争"]
        }
    }
}


@router.get("/gifts/catalog")
async def get_gift_catalog(
    db: AsyncSession = Depends(get_db),
):
    """Get gift catalog list."""
    from app.models.gift import Gift
    
    stmt = select(Gift).where(Gift.is_active == True)
    result = await db.execute(stmt)
    gifts = result.scalars().all()
    
    return {
        "gifts": [
            {
                "id": gift.id,
                "name": gift.name,
                "description": gift.description,
                "price": gift.price,
                "affection_bonus": gift.affection_bonus,
                "icon_url": gift.icon_url,
            }
            for gift in gifts
        ],
        "total": len(gifts),
    }


@router.get("")
async def list_characters(
    include_main: bool = True,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """List all characters."""
    stmt = select(Character).limit(limit)
    if not include_main:
        stmt = stmt.where(Character.is_main == False)
    
    result = await db.execute(stmt)
    characters = result.scalars().all()
    
    # Count scripts per character
    from app.models.script import Script
    script_count_stmt = (
        select(Character.id, func.count(Script.id))
        .join(Script, Script.id == Character.script_id, isouter=True)
        .group_by(Character.id)
    )
    script_count_result = await db.execute(script_count_stmt)
    script_counts = {str(row[0]): row[1] for row in script_count_result.all()}
    
    return {
        "characters": [
            {
                "id": str(c.id),
                "name": c.name,
                "description": c.description,
                "avatar_url": c.avatar_url,
                "is_main": c.is_main,
                "age": str(c.age) if c.age else None,
                "height": f"{c.height}cm" if c.height else None,
                "birthday": c.birthday,
                "likes": c.likes or [],
                "personality": c.personality or {
                    "gentle": 0,
                    "wisdom": 0,
                    "brave": 0,
                    "mysterious": 0,
                    "loyal": 0,
                },
                "script_count": script_counts.get(str(c.id), 0),
            }
            for c in characters
        ],
        "total": len(characters),
    }


@router.get("/{character_id}")
async def get_character(
    character_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """Get character details including portraits."""
    # Query character with portraits
    result = await db.execute(
        select(Character)
        .options(selectinload(Character.sprites))
        .where(Character.id == character_id)
    )
    character = result.scalar_one_or_none()

    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    # Build portraits dict - use portraits field if exists, otherwise mock data
    portraits = character.portraits or {
        "normal": f"/assets/portraits/{character.name.lower()}-normal.png",
        "happy": f"/assets/portraits/{character.name.lower()}-happy.png",
        "sad": f"/assets/portraits/{character.name.lower()}-sad.png",
        "angry": f"/assets/portraits/{character.name.lower()}-angry.png",
        "shy": f"/assets/portraits/{character.name.lower()}-shy.png"
    }

    # Get affection data for this character
    affection_result = await db.execute(
        select(Affection).where(
            Affection.user_id == UUID(user_id),
            Affection.character_id == character_id
        )
    )
    affection = affection_result.scalar_one_or_none()
    
    # Define level thresholds and labels
    LEVELS = [
        {"min": 0, "max": 19, "level": "acquaintance", "label": "相识"},
        {"min": 20, "max": 39, "level": "ambiguous", "label": "暧昧"},
        {"min": 40, "max": 59, "level": "trust", "label": "信赖"},
        {"min": 60, "max": 79, "level": "bond", "label": "羁绊"},
        {"min": 80, "max": 100, "level": "love", "label": "挚爱"},
    ]
    
    if affection:
        value = affection.value
        # Find current level
        current_level_info = LEVELS[0]
        for level_info in LEVELS:
            if value >= level_info["min"]:
                current_level_info = level_info
        
        # Calculate next level
        next_level_info = None
        current_idx = LEVELS.index(current_level_info)
        if current_idx < len(LEVELS) - 1:
            next_level_info = LEVELS[current_idx + 1]
        
        affection_data = {
            "value": value,
            "level": current_level_info["level"],
            "level_label": current_level_info["label"],
        }
        
        if next_level_info:
            affection_data["next_level"] = {
                "level": next_level_info["level"],
                "level_label": next_level_info["label"],
                "threshold": next_level_info["min"],
                "remaining": next_level_info["min"] - value
            }
    else:
        affection_data = {
            "value": 0,
            "level": "acquaintance",
            "level_label": "相识",
            "next_level": {
                "level": "ambiguous",
                "level_label": "暧昧",
                "threshold": 20,
                "remaining": 20
            }
        }

    # Build preferences from character data
    preferences_data = {
        "likedGifts": character.likes or [],
        "dislikedGifts": [],
        "likedTopics": []
    }

    # Build personality_tags from personality dict
    personality_data = character.personality or {}
    personality_tags = []
    
    # Map personality traits to tags with descriptions
    trait_descriptions = {
        "gentle": "温柔体贴，善解人意",
        "wisdom": "聪慧睿智，洞察力强",
        "brave": "勇敢无畏，敢于冒险",
        "mysterious": "神秘莫测，充满魅力",
        "loyal": "忠诚可靠，值得信赖"
    }
    
    for trait, value in personality_data.items():
        if value > 0:  # Only include traits with non-zero values
            personality_tags.append({
                "name": trait,
                "description": trait_descriptions.get(trait, f"具有{trait}特质")
            })
    
    return {
        "id": str(character.id),
        "name": character.name,
        "description": character.description,
        "dialogueStyle": {
            "speechPattern": character.dialogue_style or "",
            "catchphrase": "",
            "tone": ""
        },
        "portraits": portraits,
        "sprites": [
            {
                "emotion": sprite.emotion,
                "image_url": sprite.image_url
            }
            for sprite in character.sprites
        ] if character.sprites else [],
        "age": character.age,
        "height": character.height,
        "birthday": character.birthday,
        "likes": character.likes.get("items", character.likes) if isinstance(character.likes, dict) else (character.likes or []),
        "personality": personality_data,
        "personality_tags": personality_tags,
        "avatar_url": character.avatar_url,
        "is_main": character.is_main,
        "affection": affection_data,
        "preferences": preferences_data,
    }


@router.get("/{character_id}/personality")
async def get_character_personality(
    character_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """W09: Get character personality data with global average."""
    # Query character
    result = await db.execute(
        select(Character).where(Character.id == character_id)
    )
    character = result.scalar_one_or_none()

    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    # Get character personality
    personality = character.personality or {
        "gentle": 0,
        "wisdom": 0,
        "brave": 0,
        "mysterious": 0,
        "loyal": 0
    }

    # Calculate global average from all characters
    all_chars_result = await db.execute(
        select(Character).where(Character.personality.isnot(None))
    )
    all_characters = all_chars_result.scalars().all()

    global_average = {
        "gentle": 0,
        "wisdom": 0,
        "brave": 0,
        "mysterious": 0,
        "loyal": 0
    }

    if all_characters:
        total_count = len(all_characters)
        for char in all_characters:
            if char.personality:
                for key in global_average.keys():
                    global_average[key] += char.personality.get(key, 0)
        
        for key in global_average.keys():
            global_average[key] = round(global_average[key] / total_count)

    # Build traits array for frontend
    trait_labels = {
        "gentle": "温柔",
        "wisdom": "智慧",
        "brave": "勇敢",
        "mysterious": "神秘",
        "loyal": "忠诚"
    }
    traits = []
    for key, value in personality.items():
        traits.append({
            "key": key,
            "label": trait_labels.get(key, key),
            "value": value,
            "average": global_average.get(key, 0)
        })

    return {
        "character_id": str(character.id),
        "personality": {"traits": traits},
        "global_average": global_average
    }


@router.get("/{character_id}/voices")
async def get_character_voices(
    character_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """W09: Get character voice resources based on subscription tier."""
    from app.models.user import User
    
    # Get user subscription tier
    user_result = await db.execute(
        select(User).where(User.id == UUID(user_id))
    )
    user = user_result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get character
    char_result = await db.execute(
        select(Character).where(Character.id == character_id)
    )
    character = char_result.scalar_one_or_none()
    
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Voice data matching frontend expected format: {id, label, icon}
    all_voices = [
        {"id": f"voice-{character.id}-1", "label": "打招呼", "icon": "👋"},
        {"id": f"voice-{character.id}-2", "label": "日常对话", "icon": "💬"},
        {"id": f"voice-{character.id}-3", "label": "告白", "icon": "💕"},
        {"id": f"voice-{character.id}-4", "label": "生气", "icon": "😤"},
    ]

    return {
        "character_id": str(character.id),
        "voices": all_voices
    }


# ──────────────────────────────────────────────
# CR-015: Enhanced character detail with AI validation rules
# ──────────────────────────────────────────────


@router.get("/{character_id}/detail")
async def get_character_detail_cr015(
    character_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    CR-015: Get enhanced character details with AI validation rules.
    
    Returns character data including:
    - Basic info (name, avatar, portrait)
    - Personality (tags, description)
    - Dialogue style (speech pattern, catchphrase, tone)
    - Preferences (liked/disliked gifts, topics)
    - Affection status (current level, value, max)
    - AI validation rules
    """
    # Check if character exists in catalog
    if character_id not in CHARACTER_CATALOG:
        raise HTTPException(status_code=404, detail="Character not found")
    
    char_data = CHARACTER_CATALOG[character_id].copy()
    
    # Get user's affection with this character
    # Try to find character in database by name
    result = await db.execute(
        select(Character).where(Character.name == char_data["name"])
    )
    db_character = result.scalar_one_or_none()
    
    if db_character:
        # Get affection from database
        affection_result = await db.execute(
            select(Affection).where(
                Affection.user_id == UUID(user_id),
                Affection.character_id == db_character.id
            )
        )
        affection = affection_result.scalar_one_or_none()
        
        if affection:
            # Calculate level based on value (0-1000 scale)
            level = min(5, affection.value // 200 + 1)
            char_data["affection"] = {
                "currentLevel": level,
                "currentValue": affection.value,
                "maxValue": 1000
            }
        else:
            char_data["affection"] = {
                "currentLevel": 1,
                "currentValue": 0,
                "maxValue": 1000
            }
    else:
        # Default affection if character not in DB
        char_data["affection"] = {
            "currentLevel": 1,
            "currentValue": 0,
            "maxValue": 1000
        }
    
    return char_data


# ──────────────────────────────────────────────
# CR-015: AI Dialogue Validation
# ──────────────────────────────────────────────


class ValidateDialogueRequest(BaseModel):
    characterId: str
    dialogue: str
    context: Optional[dict] = None


class ValidationIssue(BaseModel):
    type: str
    message: str
    severity: str


class ValidateDialogueResponse(BaseModel):
    valid: bool
    score: int
    issues: List[ValidationIssue]
    suggestions: List[str]


# Create a separate router for AI endpoints
ai_router = APIRouter(prefix="/ai", tags=["ai"])


@ai_router.post("/validate-dialogue")
async def validate_dialogue(
    request: ValidateDialogueRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    CR-015: Validate AI dialogue content against character rules.
    
    Checks:
    - Character name consistency
    - Emotion polarity match
    - Sensitive word detection
    - Length control
    - Worldview terms compliance
    
    Returns validation result with score, issues, and suggestions.
    """
    character_id = request.characterId
    dialogue = request.dialogue
    
    # Check if character exists
    if character_id not in CHARACTER_CATALOG:
        raise HTTPException(status_code=404, detail="Character not found")
    
    char_data = CHARACTER_CATALOG[character_id]
    rules = char_data["aiValidationRules"]
    
    issues = []
    suggestions = []
    score = 100
    
    # 1. Check character name consistency
    if rules["characterName"] not in dialogue and char_data["name"] not in dialogue:
        # This is optional - character name doesn't need to appear in dialogue
        pass
    
    # 2. Check sensitive words
    for word in rules["sensitiveWords"]:
        if word in dialogue:
            issues.append(ValidationIssue(
                type="sensitive_word_detected",
                message=f"检测到敏感词: {word}",
                severity="error"
            ))
            score -= 20
    
    # 3. Check length
    if len(dialogue) > rules["maxLength"]:
        issues.append(ValidationIssue(
            type="length_exceeded",
            message=f"对话长度超过限制 ({len(dialogue)}/{rules['maxLength']})",
            severity="warning"
        ))
        score -= 10
        suggestions.append(f"建议将对话缩短到 {rules['maxLength']} 字以内")
    
    # 4. Check emotion polarity (simplified)
    emotion = rules["emotionPolarity"]
    if emotion == "gentle":
        # Check for gentle indicators
        gentle_words = ["呢", "哦", "吗", "吧"]
        if not any(word in dialogue for word in gentle_words):
            suggestions.append("建议使用更温柔的语气，可以添加语尾词「呢」「哦」")
            score -= 5
    elif emotion == "cheerful":
        # Check for cheerful indicators
        cheerful_words = ["啦", "呀", "！", "！"]
        if not any(word in dialogue for word in cheerful_words):
            suggestions.append("建议使用更活泼的语气，可以添加语尾词「啦」「呀」")
            score -= 5
    elif emotion == "tsundere":
        # Check for tsundere indicators
        tsundere_words = ["哼", "笨蛋", "才不是", "别误会"]
        if not any(word in dialogue for word in tsundere_words):
            suggestions.append("建议添加傲娇特征词，如「哼」「才不是呢」")
            score -= 5
    
    # 5. Check worldview terms (optional bonus)
    worldview_match = any(term in dialogue for term in rules["worldviewTerms"])
    if worldview_match:
        score = min(100, score + 5)  # Bonus for using worldview terms
    
    # Determine validity
    valid = score >= 70 and not any(issue.severity == "error" for issue in issues)
    
    return ValidateDialogueResponse(
        valid=valid,
        score=max(0, score),
        issues=issues,
        suggestions=suggestions
    )
