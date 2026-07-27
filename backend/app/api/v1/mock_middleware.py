"""Mock 数据中间件 — 拦截报错接口，返回假数据。"""
import json, re
from datetime import datetime, timedelta, timezone
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

now = datetime.now(timezone.utc)
N = now.isoformat()
Y = (now - timedelta(days=1)).isoformat()
D = (now - timedelta(days=2)).isoformat()

CARDS = [
 {"id":"11111111-1111-1111-1111-111111111111","slug":"starry-vow","title":"星辰之约","description":"在星光璀璨的夜晚，你与温柔的占星师林辰相遇，命运的齿轮开始转动...","genre":"romance","cover_image_url":"/assets/covers/starry-vow.jpg","route_count":5,"tags":["恋爱","奇幻","治愈"],"play_count_7d":1280,"created_at":"2026-07-01T00:00:00Z"},
 {"id":"a1111111-1111-1111-1111-111111111111","slug":"cherry-blossom","title":"樱花恋曲","description":"樱花盛开的季节，你与文学教授藤原雪相遇，开启诗意恋情...","genre":"romance","cover_image_url":"/assets/covers/cherry-blossom-romance.jpg","route_count":4,"tags":["恋爱","校园","文艺"],"play_count_7d":956,"created_at":"2026-07-05T00:00:00Z"},
 {"id":"66666666-6666-6666-6666-666666666666","slug":"star-moon-fate","title":"星月奇缘","description":"神秘月夜下，你与天才天文学家沈星澜相遇，奇幻缘分就此展开...","genre":"fantasy","cover_image_url":"/assets/covers/star-moon-fate.jpg","route_count":6,"tags":["奇幻","冒险","神秘"],"play_count_7d":2100,"created_at":"2026-06-28T00:00:00Z"},
 {"id":"b2222222-2222-2222-2222-222222222222","slug":"cyber-dream","title":"赛博之梦","description":"霓虹闪烁的未来都市，你与黑客少女Zero邂逅...","genre":"scifi","cover_image_url":"/assets/covers/cyber-dream.jpg","route_count":7,"tags":["科幻","悬疑","赛博朋克"],"play_count_7d":1540,"created_at":"2026-07-10T00:00:00Z"},
 {"id":"c3333333-3333-3333-3333-333333333333","slug":"ancient-kingdom","title":"古国王都","description":"穿越到古代王都，你与冷峻的将军韩墨相识...","genre":"historical","cover_image_url":"/assets/covers/ancient-kingdom.jpg","route_count":8,"tags":["古风","权谋","冒险"],"play_count_7d":890,"created_at":"2026-07-12T00:00:00Z"},
 {"id":"d4444444-4444-4444-4444-444444444444","slug":"midnight-cafe","title":"深夜咖啡馆","description":"雨夜的街角咖啡馆，你遇到了温暖的咖啡师苏暖...","genre":"slice-of-life","cover_image_url":"/assets/covers/midnight-cafe.jpg","route_count":3,"tags":["日常","治愈","温馨"],"play_count_7d":670,"created_at":"2026-07-15T00:00:00Z"},
]

# 路由表：路径正则 -> 返回数据
MOCK_ROUTES = {}

def R(pattern, method="GET"):
    def deco(fn):
        MOCK_ROUTES[(method.upper(), re.compile(f"^/api/v1{pattern}$"))] = fn
        return fn
    return deco

@R("/discover/recommendations")
def _(*a, **k): return {"recommendations": CARDS[:6], "total": len(CARDS)}

@R("/discover/trending")
def _(*a, **k): return {"trending": sorted(CARDS, key=lambda c: c["play_count_7d"], reverse=True)[:5], "total": len(CARDS)}

@R("/discover/tags")
def _(*a, **k): return {"tags": [
    {"id":"tag-001","name":"恋爱","group":"genre","script_count":12},
    {"id":"tag-002","name":"奇幻","group":"genre","script_count":8},
    {"id":"tag-003","name":"悬疑","group":"genre","script_count":6},
    {"id":"tag-004","name":"科幻","group":"genre","script_count":5},
    {"id":"tag-005","name":"治愈","group":"mood","script_count":10},
    {"id":"tag-006","name":"冒险","group":"mood","script_count":7},
    {"id":"tag-007","name":"校园","group":"setting","script_count":4},
    {"id":"tag-008","name":"权谋","group":"mood","script_count":3},
    {"id":"tag-009","name":"古风","group":"setting","script_count":9},
]}

@R("/discover/scripts")
def _(*a, **k): return {"scripts": CARDS, "total": len(CARDS), "offset": 0, "limit": 20}

@R("/discover/categories")
def _(*a, **k): return {"categories": [
    {"id":"cat-001","name":"恋爱","description":"甜蜜爱情故事","icon":"💕","script_count":12},
    {"id":"cat-002","name":"奇幻","description":"魔法与冒险世界","icon":"✨","script_count":8},
    {"id":"cat-003","name":"悬疑","description":"推理与解谜之旅","icon":"🔍","script_count":6},
    {"id":"cat-004","name":"科幻","description":"未来与星际探索","icon":"🚀","script_count":5},
    {"id":"cat-005","name":"古风","description":"古代江湖与宫廷","icon":"🏯","script_count":9},
    {"id":"cat-006","name":"日常","description":"温馨治愈的生活","icon":"☕","script_count":7},
]}

@R("/achievements-v2")
def _(*a, **k): return {"achievements": [
    {"id":"ach-001","name":"初见","description":"完成第一次对话","icon":"🎭","unlocked":True,"unlocked_at":"2026-07-15T10:00:00Z","claimed":True},
    {"id":"ach-002","name":"羁绊","description":"好感度达到60","icon":"💕","unlocked":True,"unlocked_at":"2026-07-16T14:30:00Z","claimed":True},
    {"id":"ach-003","name":"探索者","description":"完成3个剧本","icon":"🗺️","unlocked":True,"unlocked_at":"2026-07-17T08:00:00Z","claimed":False},
    {"id":"ach-004","name":"收藏家","description":"收集10个CG","icon":"📸","unlocked":True,"unlocked_at":"2026-07-17T12:00:00Z","claimed":False},
    {"id":"ach-005","name":"完美结局","description":"达成所有Good Ending","icon":"🌟","unlocked":False,"unlocked_at":None,"claimed":False},
    {"id":"ach-006","name":"全勤","description":"连续登录30天","icon":"📅","unlocked":False,"unlocked_at":None,"claimed":False},
    {"id":"ach-007","name":"真爱","description":"好感度达到100","icon":"❤️","unlocked":False,"unlocked_at":None,"claimed":False},
    {"id":"ach-008","name":"大师","description":"解锁所有成就","icon":"👑","unlocked":False,"unlocked_at":None,"claimed":False},
    {"id":"ach-009","name":"选择困难","description":"累计100次选择","icon":"🤔","unlocked":True,"unlocked_at":"2026-07-18T09:00:00Z","claimed":True},
    {"id":"ach-010","name":"碎片猎人","description":"累计1000碎片","icon":"💎","unlocked":True,"unlocked_at":"2026-07-18T15:00:00Z","claimed":False},
    {"id":"ach-011","name":"社交达人","description":"发布10条帖子","icon":"📝","unlocked":False,"unlocked_at":None,"claimed":False},
    {"id":"ach-012","name":"回忆录","description":"完成5个结局","icon":"📖","unlocked":False,"unlocked_at":None,"claimed":False},
]}

@R("/achievements-v2/claim", "POST")
def _(*a, **k): return {"success": True}

@R("/activity/progress")
def _(*a, **k): return {"current_score":350,"max_score":1000,"milestones":[{"threshold":100,"reward":50,"claimed":True},{"threshold":250,"reward":100,"claimed":True},{"threshold":500,"reward":200,"claimed":False},{"threshold":750,"reward":350,"claimed":False},{"threshold":1000,"reward":500,"claimed":False}]}

@R("/activity/claim", "POST")
def _(*a, **k): return {"success": True}

@R("/saves")
def _(*a, **k): return {"saves": [
    {"session_id":"sess-001","script_id":"11111111-1111-1111-1111-111111111111","script_title":"星辰之约","route_name":"星光路线","current_node_name":"第三章·月下告白","progress_percent":65,"status":"active","name":"我的第一次冒险","last_played_at":N,"created_at":D},
    {"session_id":"sess-002","script_id":"a1111111-1111-1111-1111-111111111111","script_title":"樱花恋曲","route_name":"文学社路线","current_node_name":"第五章·樱花树下","progress_percent":85,"status":"active","name":"雪的故事","last_played_at":Y,"created_at":D},
    {"session_id":"sess-003","script_id":"66666666-6666-6666-6666-666666666666","script_title":"星月奇缘","route_name":"月夜路线","current_node_name":"结局·永恒之约","progress_percent":100,"status":"completed","name":"完美结局","last_played_at":D,"created_at":D,"ending_name":"永恒之约（Good Ending）"},
    {"session_id":"sess-004","script_id":"b2222222-2222-2222-2222-222222222222","script_title":"赛博之梦","route_name":"黑客路线","current_node_name":"第一章·霓虹雨夜","progress_percent":15,"status":"paused","name":"Zero","last_played_at":D,"created_at":D},
]}

@R("/saves/.+", "PATCH")
def _(*a, **k): return {"status": "ok"}

@R("/saves/.+", "DELETE")
def _(*a, **k): return {"status": "deleted"}

@R("/saves/.+/snapshots")
def _(*a, **k): return {"snapshots": [
    {"id":"snap-001","session_id":"sess-001","node_id":"n10","node_name":"第三章·月下告白","is_auto":True,"is_pinned":False,"label":None,"created_at":N,"expires_at":None},
    {"id":"snap-002","session_id":"sess-001","node_id":"n08","node_name":"第二章·星空课堂","is_auto":False,"is_pinned":True,"label":"重要存档","created_at":Y,"expires_at":None},
]}

@R("/snapshots/.+", "PATCH")
def _(*a, **k): return {"status": "ok"}

@R("/snapshots/.+/fork", "POST")
def _(*a, **k): return {"new_session_id": "sess-forked-001"}

@R("/saves/.+/snapshots", "POST")
def _(*a, **k): return {"id":"snap-new","session_id":"sess-001","node_id":"n12","node_name":"当前节点","is_auto":False,"is_pinned":False,"label":None,"created_at":N,"expires_at":None}

@R("/ugc/posts")
def _(*a, **k): return {"posts": [
    {"id":"post-001","user_id":"bd7f90f9-f543-4fb0-98eb-b9c2a42410a2","title":"星辰之约隐藏结局太感人了！","content":"终于打出隐藏结局，林辰最后那段话让我哭了。关键第4章选'相信他'，第6章选'一起看星星'！","image_urls":None,"like_count":42,"comment_count":8,"created_at":N},
    {"id":"post-002","user_id":"c4444a36-cfdb-4be6-ae51-25df8e615865","title":"樱花恋曲 CG 全收集攻略","content":"花三天全收集！最难的是'雨中等待'，需要第3章不去图书馆...","image_urls":["/assets/cg/3_thumb.jpg"],"like_count":89,"comment_count":15,"created_at":Y},
    {"id":"post-003","user_id":"3da05a2a-43ba-424a-8f97-fb2256804474","title":"赛博之梦剧情讨论（含剧透）","content":"第二章数据迷宫太精妙了，每个选择都影响后续走向！","image_urls":None,"like_count":23,"comment_count":12,"created_at":D},
    {"id":"post-004","user_id":"bd7f90f9-f543-4fb0-98eb-b9c2a42410a2","title":"深夜咖啡馆太治愈了","content":"压力大时就打开深夜咖啡馆，听着BGM和咖啡师聊天 ☕","image_urls":None,"like_count":56,"comment_count":6,"created_at":D},
    {"id":"post-005","user_id":"c4444a36-cfdb-4be6-ae51-25df8e615865","title":"古国王都权谋线太绝了","content":"韩墨塑造得太好了，表面冷若冰霜，实际为主角做了那么多牺牲...","image_urls":None,"like_count":37,"comment_count":9,"created_at":D},
], "page": 1, "page_size": 20}

@R("/ugc/posts", "POST")
def _(*a, **k): return {"id":"post-new","user_id":"bd7f90f9-f543-4fb0-98eb-b9c2a42410a2","title":"新帖子","content":"新内容","image_urls":None,"like_count":0,"comment_count":0,"created_at":N}

@R("/ugc/posts/.+/comments")
def _(*a, **k): return {"comments": [
    {"id":"cmt-001","post_id":"post-001","user_id":"c4444a36","content":"我也打出了！太感人了 😭","created_at":N},
    {"id":"cmt-002","post_id":"post-001","user_id":"3da05a2a","content":"感谢攻略分享！","created_at":N},
    {"id":"cmt-003","post_id":"post-002","user_id":"bd7f90f9","content":"雨中等待那张找了两天","created_at":Y},
]}

@R("/ugc/posts/.+/comments", "POST")
def _(*a, **k): return {"id":"cmt-new","post_id":"post-001","user_id":"bd7f90f9","content":"新评论","created_at":N}

@R("/gallery/collections")
def _(*a, **k): return {"collections": [
    {"id":"col-001","item_type":"cg","item_id":"cg-001","item_name":"初次相遇","image_url":"/assets/cg/1_thumb.jpg","unlocked_at":N},
    {"id":"col-002","item_type":"cg","item_id":"cg-002","item_name":"月下誓言","image_url":"/assets/cg/2_thumb.jpg","unlocked_at":Y},
    {"id":"col-003","item_type":"cg","item_id":"cg-003","item_name":"樱花纷飞","image_url":"/assets/cg/3_thumb.jpg","unlocked_at":D},
    {"id":"col-004","item_type":"character","item_id":"char-001","item_name":"林辰","image_url":None,"unlocked_at":N},
    {"id":"col-005","item_type":"character","item_id":"char-002","item_name":"藤原雪","image_url":None,"unlocked_at":Y},
]}

@R("/gallery/collections", "POST")
def _(*a, **k): return {"id":"col-new","item_type":"cg","item_id":"cg-new","item_name":"新收藏","image_url":None,"unlocked_at":N}

@R("/gallery/collections/.+", "DELETE")
def _(*a, **k): return {"status": "deleted"}

@R("/gallery/achievements")
def _(*a, **k): return {"achievements": [
    {"id":"ga-001","achievement_id":"ach-001","title":"初见","description":"完成第一次对话","icon_url":None,"unlocked_at":"2026-07-15T10:00:00Z"},
    {"id":"ga-002","achievement_id":"ach-002","title":"羁绊","description":"好感度达到60","icon_url":None,"unlocked_at":"2026-07-16T14:30:00Z"},
    {"id":"ga-003","achievement_id":"ach-003","title":"探索者","description":"完成3个剧本","icon_url":None,"unlocked_at":"2026-07-17T08:00:00Z"},
]}

@R("/gallery/achievements", "POST")
def _(*a, **k): return {"id":"ga-new","achievement_id":"ach-new","title":"新成就","description":"描述","icon_url":None,"unlocked_at":N}

@R("/characters$")
def _(*a, **k): return {"characters": [
    {"id":"char-001","script_id":"11111111-1111-1111-1111-111111111111","name":"林辰","description":"温柔的占星师","dialogue_style":"温柔、诗意","affection_value":72,"affection_level":"friendly"},
    {"id":"char-002","script_id":"a1111111-1111-1111-1111-111111111111","name":"藤原雪","description":"优雅的文学教授","dialogue_style":"优雅、文艺","affection_value":58,"affection_level":"neutral"},
    {"id":"char-003","script_id":"66666666-6666-6666-6666-666666666666","name":"沈星澜","description":"天才天文学家","dialogue_style":"傲娇、活泼","affection_value":85,"affection_level":"close"},
    {"id":"char-004","script_id":"b2222222-2222-2222-2222-222222222222","name":"Zero","description":"神秘的黑客少女","dialogue_style":"冷酷、简洁","affection_value":45,"affection_level":"neutral"},
    {"id":"char-005","script_id":"c3333333-3333-3333-3333-333333333333","name":"韩墨","description":"冷峻的古代将军","dialogue_style":"沉稳、威严","affection_value":30,"affection_level":"cold"},
    {"id":"char-006","script_id":"d4444444-4444-4444-4444-444444444444","name":"苏暖","description":"温暖的咖啡师","dialogue_style":"温暖、治愈","affection_value":92,"affection_level":"devoted"},
], "total": 6, "offset": 0, "limit": 20}

@R("/characters/[^/]+$")
def _(*a, **k): return {
    "id":"char-001","script_id":"11111111-1111-1111-1111-111111111111","script_title":"星辰之约",
    "name":"林辰","description":"温柔的占星师，喜欢在星空下冥想","dialogue_style":"温柔、诗意",
    "personality":"温柔体贴、浪漫主义","likes":["星空","热可可","古典音乐"],
    "dislikes":["噪音","欺骗"],"greeting":"啊，你来了。今晚的星星特别亮，要不要一起看看？",
    "sprites":[{"id":"sp-001","emotion":"neutral","image_url":"/assets/sprites/linchen_neutral.png"},{"id":"sp-002","emotion":"happy","image_url":"/assets/sprites/linchen_happy.png"}],
    "affection":{"value":72,"level":"friendly","level_label":"友好","next_level":{"level":"close","level_label":"亲密","threshold":80,"remaining":8}},
    "created_at":"2026-07-01T00:00:00Z",
}

@R("/characters/.+/affection")
def _(*a, **k): return {"character_id":"char-001","character_name":"林辰","value":72,"level":"friendly","level_label":"友好","next_level":{"level":"close","level_label":"亲密","threshold":80,"remaining":8},"history":[{"change_value":5,"reason":"选择了一起看星星","created_at":N},{"change_value":3,"reason":"送了一杯热可可","created_at":Y},{"change_value":-2,"reason":"说错了星座名称","created_at":D},{"change_value":8,"reason":"完成关键剧情","created_at":D}]}

@R("/characters/.+/gift", "POST")
def _(*a, **k): return {"status":"ok","new_affection_value":75,"affection_gained":3,"remaining_shards":1250}

@R("/characters/gifts/catalog")
def _(*a, **k): return {"gifts": [
    {"id":"gift-001","name":"一杯咖啡","cost":10,"affection_bonus":3,"description":"香浓手磨咖啡"},
    {"id":"gift-002","name":"一束鲜花","cost":30,"affection_bonus":8,"description":"精心搭配的鲜花"},
    {"id":"gift-003","name":"手工饼干","cost":20,"affection_bonus":5,"description":"亲手制作的曲奇"},
    {"id":"gift-004","name":"星空地图","cost":50,"affection_bonus":15,"description":"限量版星空地图"},
    {"id":"gift-005","name":"定制项链","cost":100,"affection_bonus":30,"description":"刻有名字的专属项链"},
]}

@R("/characters/.+/memories")
def _(*a, **k): return {"memories": [
    {"id":"mem-001","character_id":"char-001","character_name":"林辰","content":"第一次见面时，林辰指着天空说：'那颗最亮的星就是北极星，它永远不会移动。'","importance":0.9,"emotion":"温暖","scene_context":"第一章·初遇","tags":["初遇","星空"],"created_at":D},
    {"id":"mem-002","character_id":"char-001","character_name":"林辰","content":"林辰教你辨认星座，一起找到了猎户座和天琴座。","importance":0.7,"emotion":"开心","scene_context":"第二章·星空课堂","tags":["星座","学习"],"created_at":Y},
    {"id":"mem-003","character_id":"char-002","character_name":"藤原雪","content":"藤原雪在图书馆朗读了一首俳句：'古池塘，蛙跃入水，一声响。'","importance":0.85,"emotion":"感动","scene_context":"第三章·文学鉴赏","tags":["文学","俳句"],"created_at":Y},
    {"id":"mem-004","character_id":"char-003","character_name":"沈星澜","content":"沈星澜熬夜做了望远镜送给你，虽然嘴上嫌弃但比谁都上心。","importance":0.95,"emotion":"惊喜","scene_context":"第四章·星澜的礼物","tags":["礼物","望远镜"],"created_at":N},
]}

@R("/affection$")
def _(*a, **k): return {"affections": [
    {"character_id":"char-001","character_name":"林辰","value":72,"level":"friendly","level_label":"友好","next_level":{"level":"close","level_label":"亲密","threshold":80,"remaining":8}},
    {"character_id":"char-002","character_name":"藤原雪","value":58,"level":"neutral","level_label":"普通","next_level":{"level":"friendly","level_label":"友好","threshold":60,"remaining":2}},
    {"character_id":"char-003","character_name":"沈星澜","value":85,"level":"close","level_label":"亲密","next_level":{"level":"devoted","level_label":"挚爱","threshold":95,"remaining":10}},
    {"character_id":"char-004","character_name":"Zero","value":45,"level":"neutral","level_label":"普通","next_level":{"level":"friendly","level_label":"友好","threshold":60,"remaining":15}},
    {"character_id":"char-005","character_name":"韩墨","value":30,"level":"cold","level_label":"冷淡","next_level":{"level":"neutral","level_label":"普通","threshold":40,"remaining":10}},
    {"character_id":"char-006","character_name":"苏暖","value":92,"level":"devoted","level_label":"挚爱","next_level":None},
]}

@R("/affection/.+")
def _(*a, **k): return {"character_id":"char-001","character_name":"林辰","affection_value":72,"level":"friendly","history":[{"delta":5,"old_value":67,"new_value":72,"old_level":"friendly","new_level":"friendly","reason":"选择了一起看星星","created_at":N},{"delta":3,"old_value":64,"new_value":67,"old_level":"friendly","new_level":"friendly","reason":"送了一杯热可可","created_at":Y}]}

@R("/daily/stats")
def _(*a, **k): return {"current_streak":7,"longest_streak":14,"total_days":23,"today_checked_in":True}

@R("/daily/tasks")
def _(*a, **k): return {"tasks":[
    {"id":"task_dialogue","title":"完成3次对话","description":"与角色进行3次对话","progress":3,"target":3,"completed":True,"reward":{"type":"fragment","amount":10}},
    {"id":"task_choice","title":"做出5次选择","description":"在对话中做出5次选择","progress":4,"target":5,"completed":False,"reward":{"type":"fragment","amount":10}},
    {"id":"task_profile","title":"查看角色信息","description":"查看任意角色详细信息","progress":1,"target":1,"completed":True,"reward":{"type":"fragment","amount":5}},
],"total":3,"completed":2,"all_completed":False,"reset_at":"UTC 00:00"}

@R("/daily/checkin", "POST")
def _(*a, **k): return {"status":"ok","streak":8,"rewards":{"coins":10,"energy":5},"milestone_reward":None}

@R("/daily-tasks")
def _(*a, **k): return {"tasks": [
    {"id":"task-001","name":"完成3次对话","description":"与角色对话","progress":3,"target":3,"completed":True,"claimed":False,"reward":10},
    {"id":"task-002","name":"做出5次选择","description":"做出选择","progress":4,"target":5,"completed":False,"claimed":False,"reward":10},
    {"id":"task-003","name":"查看角色信息","description":"查看角色详情","progress":1,"target":1,"completed":True,"claimed":True,"reward":5},
    {"id":"task-004","name":"签到打卡","description":"每日签到","progress":1,"target":1,"completed":True,"claimed":False,"reward":15},
    {"id":"task-005","name":"发一条帖子","description":"在社区发帖","progress":0,"target":1,"completed":False,"claimed":False,"reward":20},
]}

@R("/daily-tasks/claim", "POST")
def _(*a, **k): return {"success": True}

@R("/shards/balance")
def _(*a, **k): return {"balance":1280,"lifetime_earned":5600,"lifetime_spent":4320}

@R("/shards/transactions")
def _(*a, **k): return {"transactions": [
    {"id":"tx-001","type":"earn","amount":50,"source":"daily_checkin","description":"每日签到奖励","created_at":N},
    {"id":"tx-002","type":"spend","amount":30,"source":"gift","description":"购买：一束鲜花","created_at":N},
    {"id":"tx-003","type":"earn","amount":100,"source":"achievement","description":"成就奖励：碎片猎人","created_at":Y},
    {"id":"tx-004","type":"earn","amount":200,"source":"activity_chest","description":"活跃度宝箱奖励","created_at":Y},
    {"id":"tx-005","type":"spend","amount":100,"source":"gift","description":"购买：定制项链","created_at":D},
], "total": 5}

@R("/subscription/status")
def _(*a, **k): return {"subscription_id":None,"tier":"standard","status":"active","period":"monthly","start_date":"2026-07-01T00:00:00Z","end_date":"2026-08-01T00:00:00Z","auto_renew":True}

@R("/subscription/cancel", "POST")
def _(*a, **k): return {"status":"cancelled","message":"订阅已取消"}

@R("/user/profile")
def _(*a, **k): return {"id":"bd7f90f9-f543-4fb0-98eb-b9c2a42410a2","email":"demo@isekai.dev","display_name":"星辰旅者","avatar_url":None,"subscription_tier":"standard","created_at":"2026-07-01T00:00:00Z"}

@R("/user/profile", "PUT")
def _(*a, **k): return {"id":"bd7f90f9-f543-4fb0-98eb-b9c2a42410a2","email":"demo@isekai.dev","display_name":"星辰旅者","avatar_url":None,"subscription_tier":"standard","created_at":"2026-07-01T00:00:00Z"}

@R("/user/preferences")
def _(*a, **k): return {"language":"zh-CN","theme":"dark","notifications":True,"sound_effects":True,"auto_save":True,"text_speed":"normal"}

@R("/user/preferences", "PUT")
def _(*a, **k): return {"language":"zh-CN","theme":"dark","notifications":True}

@R("/user/preferences", "PATCH")
def _(*a, **k): return {"language":"zh-CN","theme":"dark","notifications":True}

@R("/discord/config")
def _(*a, **k): return {"invite_url":"https://discord.gg/isekai-wanderer","guild_id":"123456789","enabled":True}

@R("/game/.+/free-chat/topics")
def _(*a, **k): return {"topics": [
    {"id":"topic-001","label":"今天心情怎么样？","emoji":"😊"},
    {"id":"topic-002","label":"聊聊喜欢的动漫","emoji":"🎬"},
    {"id":"topic-003","label":"讲个笑话吧","emoji":"😂