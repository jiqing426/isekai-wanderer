"""Mock 中间件 — 仅用于开发环境，拦截未实现的接口返回 mock 数据。

生产安全：当 APP_ENV=production 或 DISABLE_MOCK=1 时，mock 中间件完全跳过，
mock_data.py 不被导入，所有 mock 路由注册为空操作，所有请求走真实路由。
"""
import os, json, re, sys, logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

MOCK_ENABLED = (
    os.getenv("DISABLE_MOCK", "").strip() not in ("1", "true", "True", "yes")
    and os.getenv("APP_ENV", "").strip() != "production"
)

if MOCK_ENABLED:
    from app.mock_data import (
        N, Y, D, CARDS, CATEGORIES, TAGS, ACHIEVEMENTS, ACTIVITY,
        SAVES, POSTS, COMMENTS, COLLECTIONS, GAL_ACH, CHARS, CHAR_DETAIL,
        AFFECTIONS, GIFTS, MEMORIES, SNAPSHOTS, ENDING, TOPICS, CHAT_HIST,
        ROUTE_MAP,
    )
else:
    logger.warning("[MockMiddleware] DISABLED — production mode or DISABLE_MOCK=1")

# (method, regex) -> handler
ROUTES = []

def _match(method, path):
    for m, pat, fn in ROUTES:
        if method == m and pat.match(path):
            return fn
    return None

def R(method, pattern):
    """Register a mock route. No-op when mock is disabled."""
    def deco(fn):
        if MOCK_ENABLED:
            ROUTES.append((method, re.compile(f"^/api/v1{pattern}$"), fn))
        return fn
    return deco

# ── Discover ──
@R("GET", "/discover/recommendations")
def _(): return {"recommendations": CARDS, "total": len(CARDS)}

@R("GET", "/discover/trending")
def _(): return {"trending": sorted(CARDS, key=lambda c: c["play_count_7d"], reverse=True)[:5], "total": len(CARDS)}

@R("GET", "/discover/tags")
def _(): return {"tags": TAGS}

@R("GET", "/discover/scripts")
def _(): return {"scripts": CARDS, "total": len(CARDS), "offset": 0, "limit": 20}

@R("GET", "/discover/categories")
def _(): return {"categories": CATEGORIES}

# ── Achievements v2 ──
@R("GET", "/achievements-v2")
def _(): return {"achievements": ACHIEVEMENTS}

@R("POST", "/achievements-v2/claim")
def _(): return {"success": True}

# ── Activity ──
@R("GET", "/activity/progress")
def _(): return ACTIVITY

@R("POST", "/activity/claim")
def _(): return {"success": True}

# ── Saves ──
@R("GET", "/saves")
def _(): return {"saves": SAVES}

@R("PATCH", r"/saves/[^/]+")
def _(): return {"status": "ok"}

@R("DELETE", r"/saves/[^/]+")
def _(): return {"status": "deleted"}

@R("GET", r"/saves/[^/]+/snapshots")
def _(): return {"snapshots": SNAPSHOTS}

@R("POST", r"/saves/[^/]+/snapshots")
def _(): return SNAPSHOTS[0]

@R("PATCH", r"/snapshots/[^/]+")
def _(): return {"status": "ok"}

@R("POST", r"/snapshots/[^/]+/fork")
def _(): return {"new_session_id": "sess-forked-001"}

# ── UGC ──
@R("GET", "/ugc/posts")
def _(): return {"posts": POSTS, "page": 1, "page_size": 20}

@R("POST", "/ugc/posts")
def _(): return {"id":"post-new","user_id":"bd7f90f9","title":"新帖子","content":"新内容","image_urls":None,"like_count":0,"comment_count":0,"created_at":N}

@R("GET", r"/ugc/posts/[^/]+/comments")
def _(): return {"comments": COMMENTS}

@R("POST", r"/ugc/posts/[^/]+/comments")
def _(): return {"id":"cmt-new","post_id":"post-001","user_id":"bd7f90f9","content":"新评论","created_at":N}

# ── Gallery ──
@R("GET", "/gallery/collections")
def _(): return {"collections": COLLECTIONS}

@R("POST", "/gallery/collections")
def _(): return {"id":"col-new","item_type":"cg","item_id":"cg-new","item_name":"新收藏","image_url":None,"unlocked_at":N}

@R("DELETE", r"/gallery/collections/[^/]+")
def _(): return {"status": "deleted"}

@R("GET", "/gallery/achievements")
def _(): return {"achievements": GAL_ACH}

@R("POST", "/gallery/achievements")
def _(): return {"id":"ga-new","achievement_id":"ach-new","title":"新成就","description":"描述","icon_url":None,"unlocked_at":N}

@R("GET", "/gallery/cgs")
def _(): return {"cgs": [
    {"id":"cg-001","title":"初次相遇","script_id":"11111111-1111-1111-1111-111111111111","character_id":"char-001","unlocked":True,"thumbnail_url":"/assets/cg/1_thumb.jpg","full_url":"/assets/cg/1_full.jpg"},
    {"id":"cg-002","title":"月下誓言","script_id":"11111111-1111-1111-1111-111111111111","character_id":"char-001","unlocked":True,"thumbnail_url":"/assets/cg/2_thumb.jpg","full_url":"/assets/cg/2_full.jpg"},
    {"id":"cg-003","title":"樱花纷飞","script_id":"a1111111-1111-1111-1111-111111111111","character_id":"char-002","unlocked":True,"thumbnail_url":"/assets/cg/3_thumb.jpg","full_url":"/assets/cg/3_full.jpg"},
    {"id":"cg-004","title":"星空告白","script_id":"66666666-6666-6666-6666-666666666666","character_id":"char-003","unlocked":False,"thumbnail_url":"/assets/cg/4_thumb.jpg","full_url":"/assets/cg/4_full.jpg"},
    {"id":"cg-005","title":"永恒之约","script_id":"66666666-6666-6666-6666-666666666666","character_id":"char-003","unlocked":False,"thumbnail_url":"/assets/cg/5_thumb.jpg","full_url":"/assets/cg/5_full.jpg"},
]}

# ── Characters ──
@R("GET", "/characters")
def _(): return {"characters": CHARS, "total": len(CHARS), "offset": 0, "limit": 20}

@R("GET", "/characters/gifts/catalog")
def _(): return {"gifts": GIFTS}

@R("GET", r"/characters/[^/]+/affection")
def _(): return {"character_id":"char-001","character_name":"林辰","value":72,"level":"friendly","level_label":"友好","next_level":{"level":"close","level_label":"亲密","threshold":80,"remaining":8},"history":[{"change_value":5,"reason":"选择了一起看星星","created_at":N},{"change_value":3,"reason":"送了一杯热可可","created_at":Y},{"change_value":-2,"reason":"说错了星座","created_at":D}]}

@R("POST", r"/characters/[^/]+/gift")
def _(): return {"status":"ok","new_affection_value":75,"affection_gained":3,"remaining_shards":1250}

@R("GET", r"/characters/[^/]+/memories")
def _(): return {"memories": MEMORIES}

@R("GET", r"/characters/[^/]+$")
def _(): return CHAR_DETAIL

# ── Affection ──
@R("GET", "/affection")
def _(): return {"affections": [
    {"character_id":"char-001","character_name":"林辰","value":72,"level":"bond"},
    {"character_id":"char-002","character_name":"藤原雪","value":58,"level":"trust"},
    {"character_id":"char-003","character_name":"沈星澜","value":85,"level":"love"},
    {"character_id":"char-004","character_name":"Zero","value":45,"level":"trust"},
    {"character_id":"char-005","character_name":"韩墨","value":12,"level":"acquaintance"},
    {"character_id":"char-006","character_name":"苏暖","value":92,"level":"love"},
]}

@R("GET", r"/affection/[^/]+")
def _(): return {"character_id":"char-001","character_name":"林辰","affection_value":72,"level":"friendly","history":[{"delta":5,"old_value":67,"new_value":72,"old_level":"friendly","new_level":"friendly","reason":"选择一起看星星","created_at":N},{"delta":3,"old_value":64,"new_value":67,"old_level":"friendly","new_level":"friendly","reason":"送了热可可","created_at":Y}]}

# ── Daily ──
@R("GET", "/daily/stats")
def _(): return {"current_streak":7,"longest_streak":14,"total_days":23,"today_checked_in":True}

@R("GET", "/daily/tasks")
def _(): return {"tasks":[{"id":"task_dialogue","title":"完成3次对话","description":"与角色进行3次对话","progress":3,"target":3,"completed":True,"reward":{"type":"fragment","amount":10}},{"id":"task_choice","title":"做出5次选择","description":"在对话中做出5次选择","progress":4,"target":5,"completed":False,"reward":{"type":"fragment","amount":10}},{"id":"task_profile","title":"查看角色信息","description":"查看任意角色详细信息","progress":1,"target":1,"completed":True,"reward":{"type":"fragment","amount":5}}],"total":3,"completed":2,"all_completed":False,"reset_at":"UTC 00:00"}

# CR-post-page Day 2: /daily/checkin 已实现真实 API，移除 mock
# @R("POST", "/daily/checkin")

@R("GET", "/daily-tasks")
def _(): return {"tasks":[{"id":"task-001","name":"完成3次对话","description":"与角色对话","progress":3,"target":3,"completed":True,"claimed":False,"reward":10},{"id":"task-002","name":"做出5次选择","description":"做出选择","progress":4,"target":5,"completed":False,"claimed":False,"reward":10},{"id":"task-003","name":"签到打卡","description":"每日签到","progress":1,"target":1,"completed":True,"claimed":False,"reward":15},{"id":"task-004","name":"发一条帖子","description":"社区发帖","progress":0,"target":1,"completed":False,"claimed":False,"reward":20}]}

@R("POST", "/daily-tasks/claim")
def _(): return {"success": True}

# ── Shards ──
@R("GET", "/shards/balance")
def _(): return {"balance":1280,"lifetime_earned":5600,"lifetime_spent":4320}

@R("GET", "/shards/transactions")
def _(): return {"transactions":[{"id":"tx-001","type":"earn","amount":50,"source":"daily_checkin","description":"每日签到奖励","created_at":N},{"id":"tx-002","type":"spend","amount":30,"source":"gift","description":"购买：一束鲜花","created_at":N},{"id":"tx-003","type":"earn","amount":100,"source":"achievement","description":"成就奖励：碎片猎人","created_at":Y},{"id":"tx-004","type":"earn","amount":200,"source":"activity_chest","description":"活跃度宝箱奖励","created_at":Y},{"id":"tx-005","type":"spend","amount":100,"source":"gift","description":"购买：定制项链","created_at":D}],"total":5}

# ── Subscription ──
@R("GET", "/subscription/status")
def _(): return {"subscription_id":None,"tier":"standard","status":"active","period":"monthly","start_date":"2026-07-01T00:00:00Z","end_date":"2026-08-01T00:00:00Z","auto_renew":True}

@R("POST", "/subscription/cancel")
def _(): return {"status":"cancelled","message":"订阅已取消"}

# ── User ──
@R("GET", "/user/profile")
def _(): return {"id":"bd7f90f9-f543-4fb0-98eb-b9c2a42410a2","email":"demo@isekai.dev","display_name":"星辰旅者","avatar_url":None,"subscription_tier":"standard","onboarding_completed":True,"email_verified":True,"created_at":"2026-07-01T00:00:00Z"}

@R("PUT", "/user/profile")
def _(): return {"id":"bd7f90f9-f543-4fb0-98eb-b9c2a42410a2","email":"demo@isekai.dev","display_name":"星辰旅者","avatar_url":None,"subscription_tier":"standard","onboarding_completed":True,"email_verified":True,"created_at":"2026-07-01T00:00:00Z"}

@R("GET", "/user/stats")
def _(): return {"total_plays": 47, "completed_scripts": 3, "total_hours": 86.5, "total_choices": 312, "unlocked_endings": 8, "unlocked_achievements": 4, "shards_balance": 1280, "current_streak": 7, "longest_streak": 14, "subscription_tier": "standard"}

@R("GET", "/user/preferences")
def _(): return {"language":"zh-CN","theme":"dark","notifications":True,"sound_effects":True,"auto_save":True,"text_speed":"normal"}

@R("PUT", "/user/preferences")
def _(): return {"language":"zh-CN","theme":"dark","notifications":True}

@R("PATCH", "/user/preferences")
def _(): return {"language":"zh-CN","theme":"dark","notifications":True}

# ── Scripts ──
# CR-post-page: /scripts 已实现真实 API，移除 mock
# @R("GET", "/scripts")
# @R("GET", r"/scripts/[^/]+$")

# ── Auth extra ──
@R("POST", "/auth/verify-email")
def _(): return {"status": "ok", "message": "邮箱已验证"}

@R("POST", "/auth/resend-verification")
def _(): return {"status": "ok", "message": "验证邮件已发送"}

@R("POST", "/auth/forgot-password")
def _(): return {"status": "ok", "message": "重置密码邮件已发送"}

@R("POST", "/auth/reset-password")
def _(): return {"status": "ok", "message": "密码已重置"}

@R("GET", r"/auth/oauth/[^/]+/callback")
def _(): return {"access_token": "***", "token_type": "bearer", "expires_in": 86400}

@R("POST", r"/auth/oauth/[^/]+$")
def _(): return {"access_token": "***", "token_type": "bearer", "expires_in": 86400}

# ── Discord ──
@R("GET", "/discord/config")
def _(): return {"invite_url": "https://discord.gg/isekai-wanderer", "guild_id": "123456789", "enabled": True}

# ── Game ──
# CR-post-page: /free-chat 相关接口已实现真实 API，移除 mock
# @R("GET", r"/game/[^/]+/free-chat/topics")
# @R("GET", r"/game/[^/]+/free-chat/history")
# @R("POST", r"/game/[^/]+/free-chat")

@R("GET", r"/game/[^/]+/route-map")
def _(): return ROUTE_MAP

@R("GET", r"/game/[^/]+/recap")
def _(): return {"events": [
    {"id":"ev-001","type":"scene_change","text":"你来到了星辰之约的世界...","scene":"序章·命运之夜","timestamp":D},
    {"id":"ev-002","type":"dialogue","text":"林辰：'你看，那颗最亮的星就是北极星。'","scene":"第一章·初遇","timestamp":D},
    {"id":"ev-003","type":"choice","text":"你选择了'一起看星星'","scene":"第二章·星空课堂","choice_text":"一起看星星","affection_delta":5,"timestamp":Y},
    {"id":"ev-004","type":"dialogue","text":"林辰：'和你一起看星星的感觉，和一个人完全不同。'","scene":"第三章·月下告白","timestamp":N},
]}

@R("GET", r"/game/[^/]+/ending")
def _(): return {"ending_id":"end-001","ending_name":"星光下的约定","ending_type":"good","description":"在星光璀璨的夜晚，你和林辰许下了永恒的约定。从此以后，每个晴朗的夜晚，你们都会一起仰望星空。","unlocked_at":D}

@R("GET", r"/scripts/[^/]+/ending-progress")
def _(): return ENDING

# ── Auth mock (login/register) ──
@R("POST", "/auth/login")
def _(): return {"access_token":"mock-jwt-token-for-demo","refresh_token":"mock-refresh-token","token_type":"bearer","expires_in":86400}

@R("POST", "/auth/register")
def _(): return {"access_token":"mock-jwt-token-for-demo","refresh_token":"mock-refresh-token","token_type":"bearer","expires_in":86400}

@R("POST", "/auth/refresh")
def _(): return {"access_token":"mock-jwt-token-refreshed","refresh_token":"mock-refresh-token-new","token_type":"bearer","expires_in":86400}

# ── Share ──
@R("GET", r"/share/[^/]+")
def _(): return {"share_id":"share-001","title":"星辰之约 - 星光下的约定","description":"我在星辰之约中达成了Good Ending！","script_title":"星辰之约","ending_name":"星光下的约定","created_at":D}

@R("POST", "/share/generate")
def _(): return {"share_id":"share-new","share_url":"https://isekai.dev/share/share-new"}

# ── Payment ──
@R("GET", "/payment/plans")
def _(): return {"plans":[{"id":"free","name":"Free","price":0,"currency":"CNY","billing_cycle":"monthly","features":["免费剧本","基础AI对话","1个游戏存档"],"limits":{"concurrent_sessions":1,"daily_dialogue_turns":50,"premium_scripts":False}},{"id":"standard","name":"Standard","price":29.9,"currency":"CNY","billing_cycle":"monthly","features":["全部免费功能","解锁所有剧本","无限对话","3个存档","优先生成"],"limits":{"concurrent_sessions":3,"daily_dialogue_turns":-1,"premium_scripts":True}},{"id":"premium","name":"Premium","price":79.9,"currency":"CNY","billing_cycle":"monthly","features":["全部Standard功能","10个存档","自定义角色声音","抢先体验","导出剧本"],"limits":{"concurrent_sessions":10,"daily_dialogue_turns":-1,"premium_scripts":True}}]}

@R("POST", "/payment/subscribe")
def _(): return {"status":"ok","message":"订阅成功"}

@R("POST", "/payment/purchase")
def _(): return {"status":"ok","message":"购买成功"}

@R("POST", "/payment/recharge")
def _(): return {"status":"ok","balance":1380}

@R("GET", "/payment/history")
def _(): return {"transactions":[{"id":"pay-001","type":"subscription","amount":29.9,"description":"Standard月度订阅","created_at":"2026-07-01T00:00:00Z"}]}


class MockMiddleware(BaseHTTPMiddleware):
    """拦截 /api/v1 请求，如果匹配到 mock 路由则直接返回，不走真实路由。

    生产安全：APP_ENV=production 或 DISABLE_MOCK=1 时，中间件完全透传，
    不拦截任何请求，mock_data.py 不被导入。
    """

    async def dispatch(self, request: Request, call_next):
        if not MOCK_ENABLED:
            return await call_next(request)

        path = request.url.path
        method = request.method

        handler = _match(method, path)
        if handler:
            data = handler()
            return JSONResponse(content=data)

        response = await call_next(request)
        return response
