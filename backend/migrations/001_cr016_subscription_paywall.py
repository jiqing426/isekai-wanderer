"""Migration: CR-016 subscription, dialogue quota, paywall tables, and affection decay column.

Run against PostgreSQL. Requires existing `users` table.

Tables created:
  - subscription_plans
  - dialogue_quotas
  - paywall_events

Tables altered:
  - users: ADD COLUMN affection_decay_last_calc TIMESTAMPTZ

Usage:
  python migrations/001_cr016_subscription_paywall.py
  # or via Alembic if configured
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import engine, Base
from app.models.subscription import Subscription  # noqa: F401
from app.models.dialogue_quota import DialogueQuota  # noqa: F401
from app.models.paywall_event import PaywallEvent  # noqa: F401


CREATE_SUBSCRIPTION_PLANS = """
CREATE TABLE IF NOT EXISTS subscription_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    tier VARCHAR(20) NOT NULL DEFAULT 'free',
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_subscription_plans_user_id ON subscription_plans(user_id);
CREATE INDEX IF NOT EXISTS ix_subscription_plans_tier ON subscription_plans(tier);
CREATE INDEX IF NOT EXISTS ix_subscription_plans_status ON subscription_plans(status);
"""

CREATE_DIALOGUE_QUOTAS = """
CREATE TABLE IF NOT EXISTS dialogue_quotas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    date DATE NOT NULL,
    base_quota INTEGER NOT NULL DEFAULT 3,
    consumed INTEGER NOT NULL DEFAULT 0,
    fragment_extra INTEGER NOT NULL DEFAULT 0,
    fragment_consumed INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_dialogue_quota_user_date UNIQUE (user_id, date)
);

CREATE INDEX IF NOT EXISTS ix_dialogue_quotas_user_id ON dialogue_quotas(user_id);
"""

CREATE_PAYWALL_EVENTS = """
CREATE TABLE IF NOT EXISTS paywall_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    scene VARCHAR(30) NOT NULL,
    display_type VARCHAR(10) NOT NULL,
    triggered_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_paywall_events_user_id ON paywall_events(user_id);
CREATE INDEX IF NOT EXISTS ix_paywall_events_scene ON paywall_events(scene);
"""

ALTER_USERS_ADD_DECAY = """
ALTER TABLE users ADD COLUMN IF NOT EXISTS affection_decay_last_calc TIMESTAMPTZ;
ALTER TABLE users ADD COLUMN IF NOT EXISTS returnee_activated_at TIMESTAMPTZ;
"""


async def run_migration():
    """Execute migration DDL statements."""
    print("Running CR-016 migration...")

    async with engine.begin() as conn:
        print("  Creating subscription_plans table...")
        await conn.execute(text(CREATE_SUBSCRIPTION_PLANS))

        print("  Creating dialogue_quotas table...")
        await conn.execute(text(CREATE_DIALOGUE_QUOTAS))

        print("  Creating paywall_events table...")
        await conn.execute(text(CREATE_PAYWALL_EVENTS))

        print("  Altering users table (adding affection_decay_last_calc)...")
        await conn.execute(text(ALTER_USERS_ADD_DECAY))

    print("CR-016 migration completed successfully.")


if __name__ == "__main__":
    asyncio.run(run_migration())
