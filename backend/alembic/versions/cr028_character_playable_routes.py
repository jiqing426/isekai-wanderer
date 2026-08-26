"""CR-028: Character playable routes & multi-story system

Revision ID: cr028_character_playable
Revises: cr027_narrative_prompt
Create Date: 2026-08-02

Changes:
- Extend characters: +5 fields (playable, playable_route_id, play_description, unlock_type, unlock_price)
- Extend game_sessions: +2 fields (character_id, character_name)
- New table: user_character_unlocks (UNIQUE user_id+character_id)
- Data migration: is_main characters → playable=true, unlock_type='free'
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB


revision: str = 'cr028_character_playable'
down_revision: Union[str, None] = 'cr027_narrative_prompt'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    # ── 1. characters: add 5 playable fields ──

    result = conn.execute(sa.text(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_schema = 'public' AND table_name = 'characters' "
        "AND column_name = 'playable'"
    ))
    if not result.first():
        op.add_column('characters', sa.Column('playable', sa.Boolean, nullable=False, server_default='false'))
        op.add_column('characters', sa.Column('playable_route_id', UUID(as_uuid=True),
                                               sa.ForeignKey('routes.id'), nullable=True))
        op.add_column('characters', sa.Column('play_description', sa.Text, nullable=True))
        op.add_column('characters', sa.Column('unlock_type', sa.String(20), nullable=False, server_default='free'))
        op.add_column('characters', sa.Column('unlock_price', sa.Integer, nullable=False, server_default='0'))
        op.create_index('idx_characters_playable', 'characters', ['playable'])

    # ── 2. game_sessions: add 2 character fields ──

    result = conn.execute(sa.text(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_schema = 'public' AND table_name = 'game_sessions' "
        "AND column_name = 'character_id'"
    ))
    if not result.first():
        op.add_column('game_sessions', sa.Column('character_id', UUID(as_uuid=True),
                                                  sa.ForeignKey('characters.id'), nullable=True))
        op.add_column('game_sessions', sa.Column('character_name', sa.String(100), nullable=True))
        op.create_index('idx_game_sessions_character', 'game_sessions', ['character_id'])

    # ── 3. New table: user_character_unlocks ──

    result = conn.execute(sa.text(
        "SELECT tablename FROM pg_tables "
        "WHERE schemaname = 'public' AND tablename = 'user_character_unlocks'"
    ))
    if not result.first():
        op.create_table(
            'user_character_unlocks',
            sa.Column('id', UUID(as_uuid=True), primary_key=True,
                      server_default=sa.text('gen_random_uuid()')),
            sa.Column('user_id', UUID(as_uuid=True),
                      sa.ForeignKey('users.id'), nullable=False),
            sa.Column('character_id', UUID(as_uuid=True),
                      sa.ForeignKey('characters.id'), nullable=False),
            sa.Column('unlocked_at', sa.DateTime(timezone=True),
                      nullable=False, server_default=sa.func.now()),
            sa.UniqueConstraint('user_id', 'character_id', name='uq_user_character_unlock'),
        )
        op.create_index('idx_user_character_unlocks_user', 'user_character_unlocks', ['user_id'])
        op.create_index('idx_user_character_unlocks_character', 'user_character_unlocks', ['character_id'])

    # ── 4. Data migration: is_main → playable ──

    # Set is_main characters to playable=true, unlock_type='free'
    # Use subquery to get first route per script
    conn.execute(sa.text("""
        UPDATE characters
        SET playable = true,
            unlock_type = 'free',
            playable_route_id = (
                SELECT r.id FROM routes r
                WHERE r.script_id = characters.script_id
                ORDER BY r.created_at ASC
                LIMIT 1
            ),
            play_description = COALESCE(
                characters.description,
                '扮演' || characters.name || '探索故事'
            )
        WHERE is_main = true
          AND playable = false
    """))

    # ── 5. Backfill character_name for existing game_sessions ──
    # This handles the case where game_sessions might have character_id set
    # (e.g., via manual SQL or future migrations) but missing character_name
    conn.execute(sa.text("""
        UPDATE game_sessions
        SET character_name = (
            SELECT c.name FROM characters c
            WHERE c.id = game_sessions.character_id
        )
        WHERE character_id IS NOT NULL
          AND character_name IS NULL
    """))

    # Log warning for scripts with no is_main character
    result = conn.execute(sa.text("""
        SELECT s.id, s.title
        FROM scripts s
        WHERE NOT EXISTS (
            SELECT 1 FROM characters c
            WHERE c.script_id = s.id AND c.is_main = true
        )
    """))
    for row in result:
        print(f"WARNING [CR-028]: Script '{row[1]}' ({row[0]}) has no is_main character")


def downgrade() -> None:
    op.drop_table('user_character_unlocks')
    op.drop_index('idx_game_sessions_character', table_name='game_sessions')
    op.drop_column('game_sessions', 'character_name')
    op.drop_column('game_sessions', 'character_id')
    op.drop_index('idx_characters_playable', table_name='characters')
    op.drop_column('characters', 'unlock_price')
    op.drop_column('characters', 'unlock_type')
    op.drop_column('characters', 'play_description')
    op.drop_column('characters', 'playable_route_id')
    op.drop_column('characters', 'playable')
