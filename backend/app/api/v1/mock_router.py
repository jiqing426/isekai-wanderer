"""Mock 数据路由 — 让所有页面都有数据展示，不依赖数据库。"""

from fastapi import APIRouter, Query, Request
from datetime import datetime, timedelta, timezone

now_str = datetime.now(timezone.utc).isoformat()
yesterday_str = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
two_days_ago = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()

# ── Discover mock ──

MOCK_DISCOVER_CARDS = [
    {"id": "11111111-1111-1111-1111-111111111111", "slug": "starry-vow", "title": "星辰之约", "description": "在星光璀璨的夜晚，你与温柔的占星师林辰相遇。命运的齿轮开始转动...", "genre": "romance", "cover_image_url": "/assets/covers/starry-vow.jpg", "route_count": 5, "tags": ["恋爱", "奇幻", "治愈"], "play_count_7d": 1280, "created_at": "2026-07-01T00:00:00Z"},
    {"id": "a1111111-1111-1111-1111-111111111111", "slug": "cherry-blossom-romance", "title": "樱花恋曲", "description": "在樱花盛开的季节，你与温柔的文学教授藤原雪相遇...", "genre": "romance", "cover_image_url": "/assets/covers/cherry-blossom-romance.jpg", "route_count": 4, "tags": ["恋爱", "校园", "文艺"], "play_count_7d": 956, "created_at": "2026-07-05T00:00:00Z"},
    {"id": "66666666-6666-6666-6666-666666666666", "slug": "star-moon-fate", "title": "星月奇缘", "description": "在神秘的月夜下，你与天才天文学家沈星澜相遇...", "genre": "fantasy", "cover_image_url": "/assets/covers/star-moon-fate.jpg", "route_count": 6, "tags": ["奇幻", "冒险", "神秘"], "play_count_7d": 2100, "created_at": "2026-06-28T00:00:00Z"},
    {"id": "b2222222-2222-2222-2222-222222222222", "slug": "cyber-dream", "title": "赛博之梦", "description": "在霓虹闪烁的未来都市，你与黑客少女 Zero 邂逅...", "genre": "scifi", "cover_image_url": "/assets/covers/cyber-dream.jpg", "route_count": 7, "tags": ["科幻", "悬疑", "赛博朋克"], "play_count_7d": 1540, "created_at": "2026-07-10T00:00:00Z"},
    {"id": "c3333333-3333-3333-3333-333333333333", "slug": "ancient-kingdom", "title": "古国王都", "description": "穿越到古代王都，你与冷峻的将军韩墨相识...", "genre": "historical", "cover_image_url": "/assets/covers/ancient-kingdom.jpg", "route_count": 8, "tags": ["古风", "权谋", "冒险"], "play_count_7d": 890, "created_at": "2026-07-12T00:00:00Z"},
    {"id": "d4444444-4444-4444-4444-444444444444", "slug": "midnight-cafe", "title": "深夜咖啡馆", "description": "雨夜的街角咖啡馆，你遇到了神秘的咖啡师苏暖...", "genre": "slice-of-life", "cover_image_url": "/assets/covers/midnight-cafe.jpg", "route_count": 3, "tags": ["日常", "治愈", "温馨"], "play_count_7d": 670, "created_at": "2026-07-15T00:00:00Z"},
]

MOCK_CATEGORIES = [
    {"id": "cat-001", "name": "恋爱", "description": "甜蜜爱情故事", "icon": "💕", "script_count": 12},
    {"id": "cat-002", "name": "奇幻", "description": "魔法与冒险世界", "icon": "✨", "script_count": 8},
    {"id": "cat-003", "name": "悬疑", "description": "推理与解谜之旅", "icon": "🔍", "script_count": 6},
    {"id": "cat-004", "name": "科幻", "description": "未来与星际探索", "icon": "🚀", "script_count": 5},
    {"id": "cat-005", "name": "古风", "description": "古代江湖与宫廷", "icon": "🏯", "script_count": 9},
    {"id": "cat-006", "name": "日常", "description": "温馨治愈的生活", "icon": "☕", "script_count": 7},
]

MOCK_TAGS = [
    {"id": "tag-001", "name": "恋爱", "group": "genre", "script_count": 12},
    {"id": "tag-002", "name": "奇幻", "group": "genre", "script_count": 8},
    {"id": "tag-003", "name": "悬疑", "group": "genre", "script_count": 6},
    {"id": "tag-004", "name": "科幻", "group": "genre", "script_count": 5},
    {"id": "tag-005", "name": "治愈", "group": "mood", "script_count": 10},
    {"id": "tag-006", "name": "冒险", "group": "mood", "script_count": 7},
    {"id": "tag-007", "name": "校园", "group": "setting", "script_count": 4},
    {"id": "tag-008", "name": "权谋", "group": "mood", "script_count": 3},
    {"id": "tag-009", "name": "赛博朋克", "group": "setting", "script_count": 2},
    {"id": "tag-010", "name": "古风", "group": "setting", "script_count": 9},
]

MOCK_ACHIEVEMENTS_V2 = [
    {"id": "ach-001", "name": "初见", "description": "完成第一次对话", "icon": "🎭", "unlocked": True, "unlocked_at": "2026-07-15T10:00:00Z", "claimed": True},
    {"id": "ach-002", "name": "羁绊", "description": "好感度达到60", "icon": "💕", "unlocked": True, "unlocked_at": "2026-07-16T14:30:00Z", "claimed": True},
    {"id": "ach-003", "name": "探索者", "description": "完成3个剧本", "icon": "🗺️", "unlocked": True, "unlocked_at": "2026-07-17T08:00:00Z", "claimed": False},
    {"id": "ach-004", "name": "收藏家", "description": "收集10个CG", "icon": "📸", "unlocked": True, "unlocked_at": "2026-07-17T12:00:00Z", "claimed": False},
    {"id": "ach-005", "name": "完美结局", "description": "达成所有 Good Ending", "icon": "🌟", "unlocked": False, "unlocked_at": None, "claimed": False},
    {"id": "ach-006", "name": "全勤", "description": "连续登录30天", "icon": "📅", "unlocked": False, "unlocked_at": None, "claimed": False},
    {"id": "ach-007", "name": "真爱", "description": "好感度达到100", "icon": "❤️", "unlocked": False, "unlocked_at": None, "claimed": False},
    {"id": "ach-008", "name": "大师", "description": "解锁所有成就", "icon": "👑", "unlocked": False, "unlocked_at": None, "claimed": False},
    {"id": "ach-009", "name": "选择困难", "description": "累计做出100次选择", "icon": "🤔", "unlocked": True, "unlocked_at": "2026-07-18T09:00:00Z", "claimed": True},
    {"id": "ach-010", "name": "碎片猎人", "description": "累计获得1000碎片", "icon": "💎", "unlocked": True, "unlocked_at": "2026-07-18T15:00:00Z", "claimed": False},
    {"id": "ach-011", "name": "社交达人", "description": "发布10条帖子", "icon": "📝", "unlocked": False, "unlocked_at": None, "claimed": False},
    {"id": "ach-012", "name": "回忆录", "description": "完成5个结局", "icon": "📖", "unlocked": False, "unlocked_at": None, "claimed": False},
]

MOCK_ACTIVITY = {
    "current_score": 350,
    "max_score": 1000,
    "milestones": [
        {"threshold": 100, "reward": 50, "claimed": True},
        {"threshold": 250, "reward": 100, "claimed": True},
        {"threshold": 500, "reward": 200, "claimed": False},
        {"threshold": 750, "reward": 350, "claimed": False},
        {"threshold": 1000, "reward": 500, "claimed": False},
    ],
}

MOCK_SAVES = [
    {"session_id": "sess-001", "script_id": "11111111-1111-1111-1111-111111111111", "script_title": "星辰之约", "route_name": "星光路线", "current_node_name": "第三章·月下告白", "progress_percent": 65, "status": "active", "name": "我的第一次冒险", "last_played_at": now_str, "created_at": two_days_ago},
    {"session_id": "sess-002", "script_id": "a1111111-1111-1111-1111-111111111111", "script_title": "樱花恋曲", "route_name": "文学社路线", "current_node_name": "第五章·樱花树下", "progress_percent": 85, "status": "active", "name": "雪的故事", "last_played_at": yesterday_str, "created_at": two_days_ago},
    {"session_id": "sess-003", "script_id": "66666666-6666-6666-6666-666666666666", "script_title": "星月奇缘", "route_name": "月夜路线", "current_node_name": "结局·永恒之约", "progress_percent": 100, "status": "completed", "name": "完美结局", "last_played_at": two_days_ago, "created_at": two_days_ago, "ending_name": "永恒之约（Good Ending）"},
    {"session_id": "sess-004", "script_id": "b2222222-2222-2222-2222-222222222222", "script_title": "赛博之梦", "route_name": "黑客路线", "current_node_name": "第一章·霓虹雨夜", "progress_percent": 15, "status": "paused", "name": "Zero", "last_played_at": two_days_ago, "created_at": two_days_ago},
]

MOCK_POSTS = [
    {"id": "post-001", "user_id": "bd7f90f9-f543-4fb0-98eb-b9c2a42410a2", "title": "星辰之约的隐藏结局太感人了！", "content": "终于打出了星辰之约的隐藏结局，林辰最后说的那段话真的让我哭了。关键选择在第4章要选'相信他'，然后在第6章选'一起看星星'！", "image_urls": None, "like_count": 42, "comment_count": 8, "created_at": now_str},
    {"id": "post-002", "user_id": "c4444a36-cfdb-4be6-ae51-25df8e615865", "title": "樱花恋曲 CG 全收集攻略", "content": "花了三天终于把樱花恋曲的 CG 全收了！最难拿的是'雨中等待'那张，需要在第3章选择不去图书馆...", "image_urls": ["/assets/cg/3_thumb.jpg"], "like_count": 89, "comment_count": 15, "created_at": yesterday_str},
    {"id": "post-003", "user_id": "3da05a2a-43ba-424a-8f97-fb2256804474", "title": "赛博之梦剧情讨论（含剧透）", "content": "有人玩过赛博之梦吗？第二章那个数据迷宫的设计太精妙了，每个选择都会影响后面的剧情走向...", "image_urls": None, "like_count": 23, "comment_count": 12, "created_at": two_days_ago},
    {"id": "post-004", "user_id": "bd7f90f9-f543-4fb0-98eb-b9c2a42410a2", "title": "深夜咖啡馆太治愈了", "content": "最近压力大的时候就会打开深夜咖啡馆，听着 BGM 和咖啡师聊天，感觉整个世界都安静下来了 ☕", "image_urls": None, "like_count": 56, "comment_count": 6, "created_at": two_days_ago},
    {"id": "post-005", "user_id": "c4444a36-cfdb-4be6-ae51-25df8e615865", "title": "古国王都权谋线太绝了", "content": "刚打完古国王都的权谋线，韩墨这个角色塑造得太好了。表面上冷若冰霜，实际上为了保护主角做了那么多牺牲...", "image_urls": None, "like_count": 37, "comment_count": 9, "created_at": two_days_ago},
]

MOCK_COMMENTS = [
    {"id": "cmt-001", "post_id": "post-001", "user_id": "c4444a36-cfdb-4be6-ae51-25df8e615865", "content": "我也打出了这个结局！真的太感人了 😭", "created_at": now_str},
    {"id": "cmt-002", "post_id": "post-001", "user_id": "3da05a2a-43ba-424a-8f97-fb2256804474", "content": "感谢攻略分享，马上去试试！", "created_at": now_str},
    {"id": "cmt-003", "post_id": "post-002", "user_id": "bd7f90f9-f543-4fb0-98eb-b9c2a42410a2", "content": "雨中等待那张我找了两天，原来要这样！", "created_at": yesterday_str},
    {"id": "cmt-004", "post_id": "post-003", "user_id": "bd7f90f9-f543-4fb0-98eb-b9c2a42410a2", "content": "这个剧本的分支设计确实厉害", "created_at": two_days_ago},
]

MOCK_COLLECTIONS = [
    {"id": "col-001", "item_type": "cg", "item_id": "cg-001", "item_name": "初次相遇", "image_url": "/assets/cg/1_thumb.jpg", "unlocked_at": now_str},
    {"id": "col-002", "item_type": "cg", "item_id": "cg-002", "item_name": "月下誓言", "image_url": "/assets/cg/2_thumb.jpg", "unlocked_at": yesterday_str},
    {"id": "col-003", "item_type": "cg", "item_id": "cg-003", "item_name": "樱花纷飞", "image_url": "/assets/cg/3_thumb.jpg", "unlocked_at": two_days_ago},
    {"id": "col-004", "item_type": "character", "item_id": "char-001", "item_name": "林辰", "image_url": None, "unlocked_at": now_str},
    {"id": "col-005", "item_type": "character", "item_id": "char-002", "item_name": "藤原雪", "image_url": None, "unlocked_at": yesterday_str},
]

MOCK_GALLERY_ACHIEVEMENTS = [
    {"id": "ga-001", "achievement_id": "ach-001", "title": "初见", "description": "完成第一次对话", "icon_url": None, "unlocked_at": "2026-07-15T10:00:00Z"},
    {"id": "ga-002", "achievement_id": "ach-002", "title": "羁绊", "description": "好感度达到60", "icon_url": None, "unlocked_at": "2026-07-16T14:30:00Z"},
    {"id": "ga-003", "achievement_id": "ach-003", "title": "探索者", "description": "完成3个剧本", "icon_url": None, "unlocked_at": "2026-07-17T08:00:00Z"},
]

MOCK_CHARACTERS = [
    {"id": "char-001", "script_id": "11111111-1111-1111-1111-111111111111", "name": "林辰", "description": "温柔的占星师", "dialogue_style": "温柔、诗意", "affection_value": 72, "affection_level": "friendly"},
    {"id": "char-002", "script_id": "a1111111-1111-1111-1111-111111111111", "name": "藤原雪", "description": "文学教授", "dialogue_style": "优雅、文艺", "affection_value": 58, "affection_level": "neutral"},
    {"id": "char-003", "script_id": "66666666-6666-6666-6666-666666666666", "name": "沈星澜", "description": "天才天文学家", "dialogue_style": "傲娇、活泼", "affection_value": 85, "affection_level": "close"},
    {"id": "char-004", "script_id": "b2222222-2222-2222-2222-222222222222", "name": "Zero", "description": "神秘的黑客少女", "dialogue_style": "冷酷、简洁", "affection_value": 45, "affection_level": "neutral"},
    {"id": "char-005", "script_id": "c3333333-3333-3333-3333-333333333333", "name": "韩墨", "description": "冷峻的古代将军", "dialogue_style": "沉稳、威严", "affection_value": 30, "affection_level": "cold"},
    {"id": "char-006", "script_id": "d4444444-4444-4444-4444-444444444444", "name": "苏暖", "description": "温暖的咖啡师", "dialogue_style": "温暖、治愈", "affection_value": 92, "affection_level": "devoted"},
]

MOCK_CHARACTER_DETAIL = {
    "id": "char-001", "script_id": "11111111-1111-1111-1111-111111111111", "script_title": "星辰之约",
    "name": "林辰", "description": "温柔的占星师，喜欢在星空下冥想", "dialogue_style": "温柔、诗意",
    "personality": "温柔体贴、浪漫主义、偶尔害羞", "likes": ["星空", "热可可", "古典音乐"],
    "dislikes": ["噪音", "欺骗", "浪费时间"], "greeting": "啊，你来了。今晚的星星特别亮，要不要一起看看？",
    "sprites": [{"id": "sp-001", "emotion": "neutral", "image_url": "/assets/sprites/linchen_neutral.png"}, {"id": "sp-002", "emotion": "happy", "image_url": "/assets/sprites/linchen_happy.png"}],
    "affection": {"value": 72, "level": "friendly", "level_label": "友好", "next_level": {"level": "close", "level_label": "亲密", "threshold": 80, "remaining": 8}},
    "created_at": "2026-07-01T00:00:00Z",
}

MOCK_GIFTS = [
    {"id": "gift-001", "name": "一杯咖啡", "cost": 10, "affection_bonus": 3, "description": "香浓的手磨咖啡"},
    {"id": "gift-002", "name": "一束鲜花", "cost": 30, "affection_bonus": 8, "description": "精心搭配的鲜花"},
    {"id": "gift-003", "name": "手工饼干", "cost": 20, "affection_bonus": 5, "description": "亲手制作的曲奇"},
    {"id": "gift-004", "name": "星空地图", "cost": 50, "affection_bonus": 15, "description": "限量版星空地图"},
    {"id": "gift-005", "name": "定制项链", "cost": 100, "affection_bonus": 30, "description": "刻有名字的专属项链"},
]

MOCK_MEMORIES = [
    {"id": "mem-001", "character_id": "char-001", "character_name": "林辰", "content": "第一次见面时，林辰指着天空说：'你看，那颗最亮的星就是北极星，它永远不会移动。'", "importance": 0.9, "emotion": "温暖", "scene_context": "第一章·初遇", "tags": ["初遇", "星空"], "created_at": two_days_ago},
    {"id": "mem-002", "character_id": "char-001", "character_name": "林辰", "content": "林辰教你辨认星座，你们一起找到了猎户座和天琴座。", "importance": 0.7, "emotion": "开心", "scene_context": "第二章·星空课堂", "tags": ["星座", "学习"], "created_at": yesterday_str},
    {"id": "mem-003", "character_id": "char-002", "character_name": "藤原雪", "content": "藤原雪在图书馆朗读了一首俳句：'古池塘，蛙跃入水，一声响。'", "importance": 0.85, "emotion": "感动", "scene_context": "第三章·文学鉴赏", "tags": ["文学", "俳句"], "created_at": yesterday_str},
    {"id": "mem-004", "character_id": "char-003", "character_name": "沈星澜", "content": "沈星澜熬夜做了一台小型望远镜送给你，虽然嘴上嫌弃但比谁都上心。", "importance": 0.95, "emotion": "惊喜", "scene_context": "第四章·星澜的礼物", "tags": ["礼物", "望远镜"], "created_at": now_str},
]

MOCK_AFFECTIONS = [
    {"character_id": "char-001", "character_name": "林辰", "value": 72, "level": "friendly", "level_label": "友好", "next_level": {"level": "close", "level_label": "亲密", "threshold": 80, "remaining": 8}},
    {"character_id": "char-002", "character_name": "藤原雪", "value": 58, "level": "neutral", "level_label": "普通", "next_level": {"level": "friendly", "level_label": "友好", "threshold": 60, "remaining": 2}},
    {"character_id": "char-003", "character_name": "沈星澜", "value": 85, "level": "close", "level_label": "亲密", "next_level": {"level": "devoted", "level_label": "挚爱", "threshold": 95, "remaining": 10}},
    {"character_id": "char-004", "character_name": "Zero", "value": 45, "level": "neutral", "level_label": "普通", "next_level": {"level": "friendly", "level_label": "友好", "threshold": 60, "remaining": 15}},
    {"character_id": "char-005", "character_name": "韩墨", "value": 30, "level": "cold", "level_label": "冷淡", "next_level": {"level": "neutral", "level_label": "普通", "threshold": 40, "remaining": 10}},
    {"character_id": "char-006", "character_name": "苏暖", "value": 92, "level": "devoted", "level_label": "挚爱", "next_level": None},
]

MOCK_DAILY_STATS = {"current_streak": 7, "longest_streak": 14, "total_days": 23, "today_checked_in": True}

MOCK_DAILY_TASKS = [
    {"id": "task-001", "name": "完成 3 次对话", "description": "与角色进行 3 次对话", "progress": 3, "target": 3, "completed": True, "claimed": False, "reward": 10},
    {"id": "task-002", "name": "做出 5 次选择", "description": "在对话中做出 5 次选择", "progress": 4, "target": 5, "completed": False, "claimed": False, "reward": 10},
    {"id": "task-003", "name": "查看角色信息", "description": "查看任意角色的详细信息", "progress": 1, "target": 1, "completed": True, "claimed": True, "reward": 5},
    {"id": "task-004", "name": "签到打卡", "description": "完成每日签到", "progress": 1, "target": 1, "completed": True, "claimed": False, "reward": 15},
    {"id": "task-005", "name": "发一条帖子", "description": "在社区发布一条帖子", "progress": 0, "target": 1, "completed": False, "claimed": False, "reward": 20},
]

MOCK_SHARD_BALANCE = {"balance": 1280, "lifetime_earned": 5600, "lifetime_spent": 4320}

MOCK_SHARD_TRANSACTIONS = [
    {"id": "tx-001", "type": "earn", "amount": 50, "source": "daily_checkin", "description": "每日签到奖励", "created_at": now_str},
    {"id": "tx-002", "type": "spend", "amount": 30, "source": "gift", "description": "购买礼物：一束鲜花", "created_at": now_str},
    {"id": "tx-003", "type": "earn", "amount": 100, "source": "achievement", "description": "成就奖励：碎片猎人", "created_at": yesterday_str},
    {"id": "tx-004", "type": "earn", "amount": 200, "source": "activity_chest", "description": "活跃度宝箱 250 分奖励", "created_at": yesterday_str},
    {"id": "tx-005", "type": "spend", "amount": 100, "source": "gift", "description": "购买礼物：定制项链", "created_at": two_days_ago},
]

MOCK_SUBSCRIPTION_STATUS = {
    "subscription_id": None, "tier": "standard", "status": "active",
    "period": "monthly", "start_date": "2026-07-01T00:00:00Z",
    "end_date": "2026-08-01T00:00:00Z", "auto_renew": True,
}

MOCK_USER_PROFILE = {
    "id": "bd7f90f9-f543-4fb0-98eb-b9c2a42410a2",
    "email": "demo@isekai.dev",
    "display_name": "星辰旅者",
    "avatar_url": None,
    "subscription_tier": "standard",
    "created_at": "2026-07-01T00:00:00Z",
}

MOCK_FREE_CHAT_TOPICS = [
    {"id": "topic-001", "label": "今天心情怎么样？", "emoji": "😊"},
    {"id": "topic-002", "label": "聊聊喜欢的动漫", "emoji": "🎬"},
    {"id": "topic-003", "label": "讲个笑话吧", "emoji": "😂"},
    {"id": "topic-004", "label": "推荐一本书", "emoji": "📚"},
    {"id": "topic-005", "label": "周末去哪玩？", "emoji": "🗺️"},
]

MOCK_FREE_CHAT_HISTORY = [
    {"role": "assistant", "content": "你好呀！我是林辰，今晚的星星特别美呢。想聊点什么？", "timestamp": now_str},
]

MOCK_ENDING_PROGRESS = {
    "script_id": "11111111-1111-1111-1111-111111111111",
    "script_title": "星辰之约",
    "total_endings": 5,
    "unlocked_count": 2,
    "unlocked_endings": [
        {"ending_id": "end-001", "ending_name": "星光下的约定", "ending_type": "good", "unlocked_at": two_days_ago},
        {"ending_id": "end-002", "ending_name": "平行线的交汇", "ending_type": "good", "unlocked_at": yesterday_str},
    ],
    "locked_endings": [
        {"ending_id": "end-003", "hint": "在第4章做出不同的选择..."},
        {"ending_id": "end-004", "hint": "好感度需要达到更高..."},
        {"ending_id": "end-005", "hint": "这是一个隐藏的结局..."},
    ],
}

MOCK_SNAPSHOTS = [
    {"id": "snap-001", "session_id": "sess-001", "node_id": "node-10", "node_name": "第三章·月下告白", "is_auto": True, "is_pinned": False, "label": None, "created_at": now_str, "expires_at": None},
    {"id": "snap-002", "session_id": "sess-001", "node_id": "node-08", "node_name": "第二章·星空课堂", "is_auto": False, "is_pinned": True, "label": "重要存档", "created_at": yesterday_str, "expires_at": None},
    {"id": "snap-003", "session_id": "sess-002", "node_id": "node-15", "node_name": "第五章·樱花树下", "is_auto": True, "is_pinned": False, "