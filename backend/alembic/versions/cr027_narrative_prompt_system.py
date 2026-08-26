"""CR-027: Narrative Prompt System - Lorebook, SceneConfig, Character extension

Revision ID: cr027_narrative_prompt
Revises: cr019_fragment_grant
Create Date: 2026-08-02

Changes:
- New table: lorebook_entries (world knowledge, soft-delete, tag-based)
- New table: scene_configs (node-scene binding, 1:1)
- Extended table: characters (add desire, fear, secret TEXT nullable)
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB


revision: str = 'cr027_narrative_prompt'
down_revision: Union[str, None] = 'cr019_fragment_grant'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    # --- 1. lorebook_entries ---
    result = conn.execute(sa.text(
        "SELECT tablename FROM pg_tables "
        "WHERE schemaname = 'public' AND tablename = 'lorebook_entries'"
    ))
    if not result.first():
        op.create_table(
            'lorebook_entries',
            sa.Column('id', UUID(as_uuid=True), primary_key=True,
                      server_default=sa.text('gen_random_uuid()')),
            sa.Column('title', sa.String(200), nullable=False),
            sa.Column('content', sa.Text, nullable=False),
            sa.Column('tags', JSONB, nullable=False, server_default='[]'),
            sa.Column('priority', sa.Integer, nullable=False, server_default='0'),
            sa.Column('status', sa.String(20), nullable=False, server_default='active'),
            sa.Column('created_by', UUID(as_uuid=True),
                      sa.ForeignKey('users.id'), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True),
                      nullable=False, server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True),
                      nullable=False, server_default=sa.func.now()),
        )
        op.create_index('idx_lorebook_tags', 'lorebook_entries', ['tags'],
                        postgresql_using='gin')
        op.create_index('idx_lorebook_status', 'lorebook_entries', ['status'])

    # --- 2. scene_configs ---
    result = conn.execute(sa.text(
        "SELECT tablename FROM pg_tables "
        "WHERE schemaname = 'public' AND tablename = 'scene_configs'"
    ))
    if not result.first():
        op.create_table(
            'scene_configs',
            sa.Column('id', UUID(as_uuid=True), primary_key=True,
                      server_default=sa.text('gen_random_uuid()')),
            sa.Column('node_id', UUID(as_uuid=True),
                      sa.ForeignKey('nodes.id'), nullable=False, unique=True),
            sa.Column('scene_name', sa.String(200), nullable=False),
            sa.Column('tags', JSONB, nullable=False, server_default='[]'),
            sa.Column('description', sa.Text, nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True),
                      nullable=False, server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True),
                      nullable=False, server_default=sa.func.now()),
        )
        op.create_index('idx_scene_configs_node', 'scene_configs', ['node_id'])

    # --- 3. characters: add desire / fear / secret ---
    result = conn.execute(sa.text(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_schema = 'public' AND table_name = 'characters' "
        "AND column_name = 'desire'"
    ))
    if not result.first():
        op.add_column('characters', sa.Column('desire', sa.Text, nullable=True))

    result = conn.execute(sa.text(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_schema = 'public' AND table_name = 'characters' "
        "AND column_name = 'fear'"
    ))
    if not result.first():
        op.add_column('characters', sa.Column('fear', sa.Text, nullable=True))

    result = conn.execute(sa.text(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_schema = 'public' AND table_name = 'characters' "
        "AND column_name = 'secret'"
    ))
    if not result.first():
        op.add_column('characters', sa.Column('secret', sa.Text, nullable=True))


def downgrade() -> None:
    op.drop_column('characters', 'secret')
    op.drop_column('characters', 'fear')
    op.drop_column('characters', 'desire')
    op.drop_index('idx_scene_configs_node', table_name='scene_configs')
    op.drop_table('scene_configs')
    op.drop_index('idx_lorebook_status', table_name='lorebook_entries')
    op.drop_index('idx_lorebook_tags', table_name='lorebook_entries')
    op.drop_table('lorebook_entries')
