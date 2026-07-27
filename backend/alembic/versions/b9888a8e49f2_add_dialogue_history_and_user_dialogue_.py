"""add dialogue_history and user_dialogue_counts tables

Revision ID: b9888a8e49f2
Revises: v44_dual_agent
Create Date: 2026-07-24 07:06:02.243365

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = 'b9888a8e49f2'
down_revision: Union[str, None] = 'v44_dual_agent'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    
    # Create dialogue_history table if not exists
    result = conn.execute(sa.text("""
        SELECT tablename FROM pg_tables 
        WHERE schemaname = 'public' AND tablename = 'dialogue_history'
    """))
    if not result.first():
        op.create_table(
            'dialogue_history',
            sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
            sa.Column('session_id', UUID(as_uuid=True), sa.ForeignKey('game_sessions.id', ondelete='CASCADE'), nullable=False),
            sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('role', sa.String(20), nullable=False),
            sa.Column('content', sa.Text(), nullable=False),
            sa.Column('character_id', UUID(as_uuid=True), sa.ForeignKey('characters.id'), nullable=True),
            sa.Column('character_name', sa.String(100), nullable=True),
            sa.Column('emotion', sa.String(50), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        )
        op.create_index('idx_dialogue_history_session_id', 'dialogue_history', ['session_id'])
        op.create_index('idx_dialogue_history_user_id', 'dialogue_history', ['user_id'])
        op.create_index('idx_dialogue_history_created_at', 'dialogue_history', [sa.text('created_at DESC')])

    # Create user_dialogue_counts table if not exists
    result = conn.execute(sa.text("""
        SELECT tablename FROM pg_tables 
        WHERE schemaname = 'public' AND tablename = 'user_dialogue_counts'
    """))
    if not result.first():
        op.create_table(
            'user_dialogue_counts',
            sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
            sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('script_id', UUID(as_uuid=True), sa.ForeignKey('scripts.id', ondelete='CASCADE'), nullable=False),
            sa.Column('dialogue_count', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('last_dialogue_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.UniqueConstraint('user_id', 'script_id', name='uq_user_script'),
        )
        op.create_index('idx_user_dialogue_counts_user_id', 'user_dialogue_counts', ['user_id'])
        op.create_index('idx_user_dialogue_counts_script_id', 'user_dialogue_counts', ['script_id'])


def downgrade() -> None:
    op.drop_index('idx_user_dialogue_counts_script_id', table_name='user_dialogue_counts')
    op.drop_index('idx_user_dialogue_counts_user_id', table_name='user_dialogue_counts')
    op.drop_table('user_dialogue_counts')
    
    op.drop_index('idx_dialogue_history_created_at', table_name='dialogue_history')
    op.drop_index('idx_dialogue_history_user_id', table_name='dialogue_history')
    op.drop_index('idx_dialogue_history_session_id', table_name='dialogue_history')
    op.drop_table('dialogue_history')
