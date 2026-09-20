"""Alembic environment configuration for async SQLAlchemy."""

import sys
import os

# Ensure app package is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context

# Import all models so Alembic can detect them
from app.core.database import Base
from app.models.user import User, PasswordReset, OAuthAccount
from app.models.recall import RecallEmail
from app.models.script import Script, Route, Node, NodeChoice, Character, CharacterSprite, Scene
from app.models.game import GameSession, GameProgress
from app.models.affection import Affection
from app.models.memory import CharacterMemory
from app.models.daily import DailyCheckin, StreakRecord, DailyTask
from app.models.payment import Fragment, FragmentTransaction, Purchase, Subscription
from app.models.discord import DiscordConfig
from app.models.free_chat import FreeChatSession
from app.models.asset import (
    UnlockedScript, UnlockedCG, CGAsset,
    UserPreference, EmailVerification,
)
from app.models.share import ShareCard
from app.models.gallery import Achievement, UserAchievementClaim, ActivityChestClaim
from app.models.save import SaveSnapshot
from app.models.shard import Fragment, FragmentTransaction  # noqa: F811 re-export
from app.models.convergence_point import ConvergencePoint  # v4.4
from app.models.user_persona import UserPersona  # v4.4

# CR-016 models
from app.models.subscription import Subscription as CR016Subscription  # noqa: F401
from app.models.dialogue_quota import DialogueQuota  # noqa: F401
from app.models.paywall_event import PaywallEvent  # noqa: F401

# CR-037 Corvus-Story-Core models
from app.models.corvus import (  # noqa: F401
    PlayerCandidate, CorvusGameSession, SessionNpc, InventoryItem, StoryFlag,
)

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Run migrations with a connection."""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode with async engine."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode using sync engine."""
    url = config.get_main_option("sqlalchemy.url")
    connectable = create_engine(url, poolclass=pool.NullPool)
    with connectable.connect() as connection:
        do_run_migrations(connection)
    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
