"""API v1 router registry."""

from fastapi import APIRouter
from app.api.v1.health import router as health_router
from app.api.v1.auth import router as auth_router
from app.api.v1.scripts import router as scripts_router
from app.api.v1.game import router as game_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(scripts_router)
api_router.include_router(game_router)

from app.api.v1.user import router as user_router
from app.api.v1.daily import router as daily_router
from app.api.v1.affection import router as affection_router
from app.api.v1.memories import router as memories_router
from app.api.v1.payment import router as payment_router
from app.api.v1.oauth import router as oauth_router
from app.api.v1.ugc import router as ugc_router
from app.api.v1.share import router as share_router
from app.api.v1.gallery import router as gallery_router
from app.api.v1.gallery import achievements_router
from app.api.v1.subscription import router as subscription_router
from app.api.v1.moderation import router as moderation_router
from app.api.v1.discover import router as discover_router
from app.api.v1.characters import router as characters_router
from app.api.v1.characters import ai_router
from app.api.v1.saves import router as saves_router
from app.api.v1.ending_progress import router as ending_progress_router
from app.api.v1.shards import router as shards_router
from app.api.v1.achievements import router as achievements_v2_router
from app.api.v1.daily_tasks import router as daily_tasks_router
from app.api.v1.activity import router as activity_router
from app.api.v1.recap import router as recap_router
from app.api.v1.chat import router as chat_router
from app.api.v1.user_dialogue import router as user_dialogue_router
from app.api.v1.users import router as users_me_router
from app.api.v1.sign import router as sign_router
from app.api.v1.settings import router as settings_router
from app.api.v1.fragment import router as fragment_router
from app.api.v1.gift import router as gift_router
from app.api.v1.paywall import router as paywall_router
from app.api.v1.community import router as community_router
from app.api.v1.user_subscription import router as user_subscription_router
from app.api.v1.upload import router as upload_router
from app.api.v1.cr016_subscription import router as cr016_subscription_router
from app.api.v1.cr016_dialogue import router as cr016_dialogue_router
from app.api.v1.cr016_paywall import router as cr016_paywall_router
from app.api.v1.cr017_unlock import router as cr017_unlock_router

api_router.include_router(user_router)
api_router.include_router(daily_router)
api_router.include_router(affection_router)
api_router.include_router(memories_router)
api_router.include_router(payment_router)
api_router.include_router(oauth_router)
api_router.include_router(ugc_router)
api_router.include_router(share_router)
api_router.include_router(gallery_router)
api_router.include_router(achievements_v2_router)  # DB-backed achievements API
# achievements_router removed - using achievements_v2_router instead
api_router.include_router(subscription_router)
api_router.include_router(moderation_router)
api_router.include_router(discover_router)
api_router.include_router(characters_router)
api_router.include_router(ai_router)
api_router.include_router(saves_router)
api_router.include_router(ending_progress_router)
api_router.include_router(shards_router)
api_router.include_router(daily_tasks_router)
api_router.include_router(activity_router)
api_router.include_router(recap_router)
api_router.include_router(chat_router)
api_router.include_router(user_dialogue_router)
api_router.include_router(users_me_router)
api_router.include_router(sign_router)
api_router.include_router(settings_router)
api_router.include_router(fragment_router)
api_router.include_router(gift_router)
api_router.include_router(paywall_router)
api_router.include_router(community_router)
api_router.include_router(user_subscription_router)
api_router.include_router(upload_router)
api_router.include_router(cr016_subscription_router)
api_router.include_router(cr016_dialogue_router)
api_router.include_router(cr016_paywall_router)
api_router.include_router(cr017_unlock_router)
