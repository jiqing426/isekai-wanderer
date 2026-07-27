"""CR-017 unlock animation system

Revision ID: cr017_unlock_animation
Revises: cr016_subscription_paywall
Create Date: 2026-07-25 08:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = 'cr017_unlock_animation'
down_revision: Union[str, None] = 'cr016_subscription_paywall'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    
    # Check if table already exists
    result = conn.execute(sa.text("""
        SELECT tablename FROM pg_tables 
        WHERE schemaname = 'public' AND tablename = 'unlock_records'
    """))
    
    if not result.first():
        # Create unlock_records table
        op.create_table(
            'unlock_records',
            sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
            sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False, index=True),
            sa.Column('unlock_type', sa.String(50), nullable=False, index=True),
            sa.Column('content_id', sa.String(255), nullable=False),
            sa.Column('title', sa.String(255), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('image_url', sa.Text(), nullable=True),
            sa.Column('rarity', sa.String(10), nullable=True),
            sa.Column('reward_data', sa.JSON(), nullable=True),
            sa.Column('unlocked_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column('viewed', sa.Boolean(), nullable=False, server_default=sa.text('false')),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        )
        
        # Create indexes
        op.create_index('ix_unlock_records_user_id', 'unlock_records', ['user_id'])
        op.create_index('ix_unlock_records_unlock_type', 'unlock_records', ['unlock_type'])
        op.create_index('ix_unlock_records_viewed', 'unlock_records', ['viewed'])
        op.create_index('ix_unlock_records_unlocked_at', 'unlock_records', ['unlocked_at'])
        
        # Composite index for common query pattern
        op.create_index('ix_unlock_records_user_viewed', 'unlock_records', ['user_id', 'viewed'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_unlock_records_user_viewed', table_name='unlock_records')
    op.drop_index('ix_unlock_records_unlocked_at', table_name='unlock_records')
    op.drop_index('ix_unlock_records_viewed', table_name='unlock_records')
    op.drop_index('ix_unlock_records_unlock_type', table_name='unlock_records')
    op.drop_index('ix_unlock_records_user_id', table_name='unlock_records')
    
    # Drop table
    op.drop_table('unlock_records')
