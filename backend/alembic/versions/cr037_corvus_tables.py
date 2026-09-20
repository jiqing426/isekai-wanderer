"""CR-037 Corvus-Story-Core: 5 new tables

Revision ID: cr037_corvus_tables
Revises: cr030_chapter_structure
Create Date: 2026-07-25

Player candidates, Corvus game sessions, session NPCs, inventory items, story flags.
All PKs are UUID v4 (gen_random_uuid()). corvus_internal_game_id is VARCHAR(100).
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = "cr037_corvus_tables"
down_revision = "cr030_chapter_structure"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. player_candidates
    op.create_table(
        "player_candidates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("personality", sa.Text, nullable=True),
        sa.Column("backstory", sa.Text, nullable=True),
        sa.Column("appearance", sa.Text, nullable=True),
        sa.Column("initial_inventory", postgresql.JSONB, server_default=sa.text("'[]'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # 2. corvus_game_sessions
    op.create_table(
        "corvus_game_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("selected_player_candidate_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("player_candidates.id"), nullable=True),
        sa.Column("initial_location_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", sa.String(30), server_default="'waiting_select_player'", index=True),
        sa.Column("corvus_internal_game_id", sa.String(100), nullable=True),
        sa.Column("engine_type", sa.String(10), server_default="'corvus'"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # 3. session_npcs
    op.create_table(
        "session_npcs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("game_session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("corvus_game_sessions.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("npc_template_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("name", sa.String(100), nullable=True),
        sa.Column("affinity", sa.Integer, server_default="0"),
        sa.Column("present", sa.Boolean, server_default=sa.text("true")),
        sa.Column("corvus_character_id", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # 4. inventory_items
    op.create_table(
        "inventory_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("game_session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("corvus_game_sessions.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("quantity", sa.Integer, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # 5. story_flags
    op.create_table(
        "story_flags",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("game_session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("corvus_game_sessions.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("flag_key", sa.String(200), nullable=False),
        sa.Column("flag_value", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("game_session_id", "flag_key", name="story_flags_game_session_id_flag_key_key"),
    )


def downgrade() -> None:
    op.drop_table("story_flags")
    op.drop_table("inventory_items")
    op.drop_table("session_npcs")
    op.drop_table("corvus_game_sessions")
    op.drop_table("player_candidates")
