"""Database cleanup: merge subscription tables, remove unused tables, add constraints

Revision ID: cr044_db_cleanup
Revises: cr037_corvus_tables
Create Date: 2026-09-20

Changes:
1. Drop email_verifications table (verification codes use Redis)
2. Drop user_preferences table (merged into user_settings)
3. Drop subscription_plans table (merged into subscriptions)
4. Add unique constraint on post_likes (user_id, post_id)
5. Add ondelete CASCADE to affection foreign keys
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'cr044_db_cleanup'
down_revision = 'cr037_corvus_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Drop email_verifications (unused, verification codes in Redis)
    op.execute("DROP TABLE IF EXISTS email_verifications CASCADE;")

    # 2. Drop user_preferences (0 rows, merged into user_settings)
    op.execute("DROP TABLE IF EXISTS user_preferences CASCADE;")

    # 3. Drop subscription_plans (merged into subscriptions)
    #    First check if subscriptions table has the tier column, if not add it
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    subscriptions_cols = [c['name'] for c in inspector.get_columns('subscriptions')]
    
    if 'tier' not in subscriptions_cols:
        op.add_column('subscriptions', sa.Column('tier', sa.String(20), nullable=False, server_default='free'))
        op.create_index('ix_subscriptions_tier', 'subscriptions', ['tier'])
    
    if 'fragment_quota' not in subscriptions_cols:
        op.add_column('subscriptions', sa.Column('fragment_quota', sa.Integer, nullable=True))
    
    if 'last_fragment_grant_at' not in subscriptions_cols:
        op.add_column('subscriptions', sa.Column('last_fragment_grant_at', sa.DateTime(timezone=True), nullable=True))
    
    if 'next_fragment_grant_at' not in subscriptions_cols:
        op.add_column('subscriptions', sa.Column('next_fragment_grant_at', sa.DateTime(timezone=True), nullable=True))

    # Migrate any data from subscription_plans to subscriptions
    op.execute("""
        INSERT INTO subscriptions (user_id, tier, status, started_at, expires_at, fragment_quota, last_fragment_grant_at, next_fragment_grant_at, plan_id, billing_cycle, currency, price, is_mock, auto_renew, quota_total, quota_used, quota_period)
        SELECT sp.user_id, sp.tier, sp.status, sp.started_at, sp.expires_at, sp.fragment_quota, sp.last_fragment_grant_at, sp.next_fragment_grant_at,
               sp.tier AS plan_id, 'monthly' AS billing_cycle, 'CNY' AS currency, 0 AS price, true AS is_mock, false AS auto_renew, 50 AS quota_total, 0 AS quota_used, 'regular' AS quota_period
        FROM subscription_plans sp
        WHERE NOT EXISTS (SELECT 1 FROM subscriptions s WHERE s.user_id = sp.user_id);
    """)
    
    # Now safely drop subscription_plans
    op.execute("DROP TABLE IF EXISTS subscription_plans CASCADE;")

    # 4. Add unique constraint on post_likes (user_id, post_id)
    op.execute("DELETE FROM post_likes WHERE (user_id, post_id) IN (SELECT user_id, post_id FROM post_likes GROUP BY user_id, post_id HAVING count(*) > 1);")
    op.create_unique_constraint('uq_post_likes_user_post', 'post_likes', ['user_id', 'post_id'])

    # 5. Add ondelete CASCADE to affection tables (recreate FKs)
    op.drop_constraint('affection_user_id_fkey', 'affection', type_='foreignkey')
    op.create_foreign_key('affection_user_id_fkey', 'affection', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('affection_character_id_fkey', 'affection', type_='foreignkey')
    op.create_foreign_key('affection_character_id_fkey', 'affection', 'characters', ['character_id'], ['id'], ondelete='CASCADE')
    
    op.drop_constraint('affection_history_user_id_fkey', 'affection_history', type_='foreignkey')
    op.create_foreign_key('affection_history_user_id_fkey', 'affection_history', 'users', ['user_id'], ['id'], ondelete='CASCADE')


def downgrade() -> None:
    # Recreate subscription_plans
    op.create_table(
        'subscription_plans',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('tier', sa.String(20), nullable=False, index=True),
        sa.Column('status', sa.String(20), nullable=False, index=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('fragment_quota', sa.Integer, nullable=True),
        sa.Column('last_fragment_grant_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_fragment_grant_at', sa.DateTime(timezone=True), nullable=True),
    )
    
    # Recreate email_verifications
    op.create_table(
        'email_verifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('token', sa.String(255), nullable=False, index=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used', sa.Boolean, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    
    # Recreate user_preferences
    op.create_table(
        'user_preferences',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False, unique=True, index=True),
        sa.Column('language', sa.String(10), default='en'),
        sa.Column('bgm_enabled', sa.Boolean, default=True),
        sa.Column('sfx_enabled', sa.Boolean, default=True),
        sa.Column('text_speed', sa.String(20), default='normal'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    
    # Drop unique constraint on post_likes
    op.drop_constraint('uq_post_likes_user_post', 'post_likes', type_='unique')
