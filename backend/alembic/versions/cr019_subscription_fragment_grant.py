"""CR-019: Add fragment grant tracking to subscriptions

Revision ID: cr019_fragment_grant
Revises: cr017_unlock_animation
Create Date: 2026-07-30

Add fields for monthly fragment grant scheduling:
- fragment_quota: Monthly fragments for this tier
- last_fragment_grant_at: Last grant timestamp
- next_fragment_grant_at: Next scheduled grant date
"""
from alembic import op
import sqlalchemy as sa

revision = 'cr019_fragment_grant'
down_revision = 'cr017_unlock_animation'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'subscription_plans',
        sa.Column('fragment_quota', sa.Integer(), nullable=True,
                  comment='Monthly fragments for this tier')
    )
    op.add_column(
        'subscription_plans',
        sa.Column('last_fragment_grant_at', sa.DateTime(timezone=True), nullable=True,
                  comment='Last fragment grant timestamp')
    )
    op.add_column(
        'subscription_plans',
        sa.Column('next_fragment_grant_at', sa.DateTime(timezone=True), nullable=True,
                  comment='Next scheduled grant date')
    )


def downgrade() -> None:
    op.drop_column('subscription_plans', 'next_fragment_grant_at')
    op.drop_column('subscription_plans', 'last_fragment_grant_at')
    op.drop_column('subscription_plans', 'fragment_quota')
