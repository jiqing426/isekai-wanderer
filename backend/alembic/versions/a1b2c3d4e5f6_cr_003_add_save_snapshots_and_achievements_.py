"""cr_003_add_save_snapshots_and_achievements_tables

Revision ID: a1b2c3d4e5f6
Revises: f25005f71038
Create Date: 2026-07-24 02:45:00.000000

Fixes P0 BUG-CR3-001 (achievements 500) and BUG-CR3-002 (saves 500).
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'f25005f71038'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # save_snapshots — used by CR3-012/013 saves API
    op.create_table('save_snapshots',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('session_id', sa.UUID(), nullable=False),
        sa.Column('label', sa.String(length=100), nullable=True),
        sa.Column('choice_history', sa.JSON(), nullable=True),
        sa.Column('current_node_id', sa.UUID(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['session_id'], ['game_sessions.id'], ),
        sa.ForeignKeyConstraint(['current_node_id'], ['nodes.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_save_snapshots_user_id'), 'save_snapshots', ['user_id'], unique=False)
    op.create_index(op.f('ix_save_snapshots_session_id'), 'save_snapshots', ['session_id'], unique=False)

    # achievements — used by CR3-020/021 achievements-v2 API
    op.create_table('achievements',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('achievement_id', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('icon_url', sa.Text(), nullable=True),
        sa.Column('unlocked_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_achievements_user_id'), 'achievements', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_achievements_user_id'), table_name='achievements')
    op.drop_table('achievements')
    op.drop_index(op.f('ix_save_snapshots_session_id'), table_name='save_snapshots')
    op.drop_index(op.f('ix_save_snapshots_user_id'), table_name='save_snapshots')
    op.drop_table('save_snapshots')
