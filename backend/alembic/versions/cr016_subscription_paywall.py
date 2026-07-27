"""CR-016 subscription paywall system

Revision ID: cr016_subscription_paywall
Revises: b9888a8e49f2
Create Date: 2026-07-25 05:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = 'cr016_subscription_paywall'
down_revision: Union[str, None] = 'b9888a8e49f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    
    # 1. Create subscription_plans table
    result = conn.execute(sa.text("""
        SELECT tablename FROM pg_tables 
        WHERE schemaname = 'public' AND tablename = 'subscription_plans'
    """))
    if not result.first():
        op.create_table(
            'subscription_plans',
            sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
            sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False, index=True),
            sa.Column('tier', sa.String(20), nullable=False, default='free', index=True),
            sa.Column('status', sa.String(20), nullable=False, default='active', index=True),
            sa.Column('started_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        )
        op.create_index('ix_subscription_plans_user_id', 'subscription_plans', ['user_id'])
        op.create_index('ix_subscription_plans_tier', 'subscription_plans', ['tier'])
        op.create_index('ix_subscription_plans_status', 'subscription_plans', ['status'])
    
    # 2. Create dialogue_quotas table
    result = conn.execute(sa.text("""
        SELECT tablename FROM pg_tables 
        WHERE schemaname = 'public' AND tablename = 'dialogue_quotas'
    """))
    if not result.first():
        op.create_table(
            'dialogue_quotas',
            sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
            sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False, index=True),
            sa.Column('date', sa.Date(), nullable=False),
            sa.Column('base_quota', sa.Integer(), nullable=False, default=3),
            sa.Column('consumed', sa.Integer(), nullable=False, default=0),
            sa.Column('fragment_extra', sa.Integer(), nullable=False, default=0),
            sa.Column('fragment_consumed', sa.Integer(), nullable=False, default=0),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.UniqueConstraint('user_id', 'date', name='uq_dialogue_quota_user_date'),
        )
        op.create_index('ix_dialogue_quotas_user_id', 'dialogue_quotas', ['user_id'])
    
    # 3. Create paywall_events table
    result = conn.execute(sa.text("""
        SELECT tablename FROM pg_tables 
        WHERE schemaname = 'public' AND tablename = 'paywall_events'
    """))
    if not result.first():
        op.create_table(
            'paywall_events',
            sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
            sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False, index=True),
            sa.Column('scene', sa.String(30), nullable=False, index=True),
            sa.Column('display_type', sa.String(10), nullable=False),
            sa.Column('triggered_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        )
        op.create_index('ix_paywall_events_user_id', 'paywall_events', ['user_id'])
        op.create_index('ix_paywall_events_scene', 'paywall_events', ['scene'])
    
    # 4. Add affection_decay_last_calc column to users table
    result = conn.execute(sa.text("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'affection_decay_last_calc'
    """))
    if not result.first():
        op.add_column('users', sa.Column('affection_decay_last_calc', sa.DateTime(timezone=True), nullable=True))
    
    # 5. Add returnee_activated_at column to users table
    result = conn.execute(sa.text("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'returnee_activated_at'
    """))
    if not result.first():
        op.add_column('users', sa.Column('returnee_activated_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    # Drop columns from users table
    op.drop_column('users', 'returnee_activated_at')
    op.drop_column('users', 'affection_decay_last_calc')
    
    # Drop tables
    op.drop_table('paywall_events')
    op.drop_table('dialogue_quotas')
    op.drop_table('subscription_plans')
