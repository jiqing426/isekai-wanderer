"""v4.4 dual-agent architecture: add convergence_points, user_personas,
affection_history + alter free_chat_sessions, character_memories, scripts.

Revision ID: v44_dual_agent
Revises: b2c3d4e5f6a7
Create Date: 2026-07-21
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision: str = "v44_dual_agent"
down_revision: Union[str, None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    
    # ── New table 1: convergence_points ─────────────────────────────
    result = conn.execute(sa.text("""
        SELECT tablename FROM pg_tables 
        WHERE schemaname = 'public' AND tablename = 'convergence_points'
    """))
    if not result.first():
        op.create_table(
            "convergence_points",
            sa.Column("id", UUID(as_uuid=True), nullable=False),
            sa.Column("script_id", UUID(as_uuid=True), nullable=False),
            sa.Column("chapter", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(length=255), nullable=False),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column("required_rounds", JSONB(), nullable=False, server_default="[]"),
            sa.Column("scene_id", UUID(as_uuid=True), nullable=True),
            sa.Column("content", JSONB(), nullable=False, server_default="{}"),
            sa.Column("is_final", sa.Boolean(), nullable=False, server_default="false"),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                      server_default=sa.text("now()")),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                      server_default=sa.text("now()")),
            sa.PrimaryKeyConstraint("id"),
            sa.ForeignKeyConstraint(["script_id"], ["scripts.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["scene_id"], ["scenes.id"]),
            sa.UniqueConstraint("script_id", "chapter",
                                name="uq_convergence_script_chapter"),
        )
        op.create_index("idx_convergence_script", "convergence_points", ["script_id"])
        op.create_index("idx_convergence_chapter", "convergence_points", ["chapter"])

    # ── New table 2: user_personas ──────────────────────────────────
    result = conn.execute(sa.text("""
        SELECT tablename FROM pg_tables 
        WHERE schemaname = 'public' AND tablename = 'user_personas'
    """))
    if not result.first():
        op.create_table(
            "user_personas",
            sa.Column("user_id", UUID(as_uuid=True), nullable=False),
            sa.Column("chat_style", sa.Text(), nullable=True),
            sa.Column("preferences", JSONB(), nullable=True),
            sa.Column("fav_characters", JSONB(), nullable=True),
            sa.Column("total_chats", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("avg_session_duration", sa.Integer(), nullable=False,
                      server_default="0"),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                      server_default=sa.text("now()")),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                      server_default=sa.text("now()")),
            sa.PrimaryKeyConstraint("user_id"),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        )
        op.create_index("idx_persona_fav_chars", "user_personas", ["fav_characters"],
                        postgresql_using="gin",
                        postgresql_ops={"fav_characters": "jsonb_ops"})

    # ── New table 3: affection_history (re-create with wider columns) ─
    # Check if table exists with old schema
    result = conn.execute(sa.text("""
        SELECT tablename FROM pg_tables 
        WHERE schemaname = 'public' AND tablename = 'affection_history'
    """))
    if result.first():
        # Drop existing table first (it was auto-created by Base.metadata.create_all
        # with narrower VARCHAR(20) for levels and VARCHAR(50) for reason).
        result = conn.execute(sa.text("""
            SELECT indexname FROM pg_indexes 
            WHERE tablename = 'affection_history' AND indexname = 'ix_affection_history_user_id'
        """))
        if result.first():
            op.drop_index("ix_affection_history_user_id", table_name="affection_history")
        op.drop_table("affection_history")

    # Check if new schema already exists
    result = conn.execute(sa.text("""
        SELECT tablename FROM pg_tables 
        WHERE schemaname = 'public' AND tablename = 'affection_history'
    """))
    if not result.first():
        op.create_table(
            "affection_history",
            sa.Column("id", UUID(as_uuid=True), nullable=False),
            sa.Column("user_id", UUID(as_uuid=True), nullable=False),
            sa.Column("character_id", UUID(as_uuid=True), nullable=False),
            sa.Column("delta", sa.Integer(), nullable=False),
            sa.Column("old_value", sa.Integer(), nullable=False),
            sa.Column("new_value", sa.Integer(), nullable=False),
            sa.Column("old_level", sa.String(length=50), nullable=False),
            sa.Column("new_level", sa.String(length=50), nullable=False),
            sa.Column("reason", sa.String(length=100), nullable=False),
            sa.Column("source_session_id", UUID(as_uuid=True), nullable=True),
            sa.Column("source_choice_id", UUID(as_uuid=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                      server_default=sa.text("now()")),
            sa.PrimaryKeyConstraint("id"),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["character_id"], ["characters.id"],
                                    ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["source_session_id"], ["game_sessions.id"]),
            sa.ForeignKeyConstraint(["source_choice_id"], ["node_choices.id"]),
        )
        op.create_index("idx_aff_history_user_char", "affection_history",
                        ["user_id", "character_id"])
        op.create_index("idx_aff_history_created", "affection_history",
                        [sa.text("created_at DESC")],
                        postgresql_using="btree")

    # ── Alter free_chat_sessions: add character_id + script_id ────────
    # Check if columns exist before adding
    conn = op.get_bind()
    result = conn.execute(sa.text("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'free_chat_sessions' AND column_name = 'character_id'
    """))
    if not result.first():
        op.add_column("free_chat_sessions",
                      sa.Column("character_id", UUID(as_uuid=True), nullable=True))
    
    result = conn.execute(sa.text("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'free_chat_sessions' AND column_name = 'script_id'
    """))
    if not result.first():
        op.add_column("free_chat_sessions",
                      sa.Column("script_id", UUID(as_uuid=True), nullable=True))
    
    # Create foreign keys if they don't exist
    result = conn.execute(sa.text("""
        SELECT constraint_name FROM information_schema.table_constraints 
        WHERE table_name = 'free_chat_sessions' AND constraint_name = 'free_chat_sessions_character_id_fkey'
    """))
    if not result.first():
        op.create_foreign_key("free_chat_sessions_character_id_fkey",
                              "free_chat_sessions", "characters",
                              ["character_id"], ["id"])
    
    result = conn.execute(sa.text("""
        SELECT constraint_name FROM information_schema.table_constraints 
        WHERE table_name = 'free_chat_sessions' AND constraint_name = 'free_chat_sessions_script_id_fkey'
    """))
    if not result.first():
        op.create_foreign_key("free_chat_sessions_script_id_fkey",
                              "free_chat_sessions", "scripts",
                              ["script_id"], ["id"])
    
    # Create index if it doesn't exist
    result = conn.execute(sa.text("""
        SELECT indexname FROM pg_indexes 
        WHERE tablename = 'free_chat_sessions' AND indexname = 'idx_free_chat_character'
    """))
    if not result.first():
        op.create_index("idx_free_chat_character", "free_chat_sessions",
                        ["character_id"])

    # ── Alter character_memories: add importance ──────────────────────
    # 'source' already exists from the initial schema; only add importance.
    conn = op.get_bind()
    result = conn.execute(sa.text("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'character_memories' AND column_name = 'importance'
    """))
    if not result.first():
        op.add_column("character_memories",
                      sa.Column("importance", sa.Numeric(precision=3, scale=2),
                                nullable=False, server_default="0.5"))
    
    # Create indexes if they don't exist
    result = conn.execute(sa.text("""
        SELECT indexname FROM pg_indexes 
        WHERE tablename = 'character_memories' AND indexname = 'idx_memory_source'
    """))
    if not result.first():
        op.create_index("idx_memory_source", "character_memories", ["source"])
    
    result = conn.execute(sa.text("""
        SELECT indexname FROM pg_indexes 
        WHERE tablename = 'character_memories' AND indexname = 'idx_memory_importance'
    """))
    if not result.first():
        op.create_index("idx_memory_importance", "character_memories",
                        [sa.text("importance DESC")],
                        postgresql_using="btree")

    # ── Alter scripts: add convergence / character counters ───────────
    result = conn.execute(sa.text("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'scripts' AND column_name = 'total_convergence_points'
    """))
    if not result.first():
        op.add_column("scripts",
                      sa.Column("total_convergence_points", sa.Integer(),
                                nullable=False, server_default="3"))
    
    result = conn.execute(sa.text("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'scripts' AND column_name = 'characters_per_script'
    """))
    if not result.first():
        op.add_column("scripts",
                      sa.Column("characters_per_script", sa.Integer(),
                                nullable=False, server_default="3"))


def downgrade() -> None:
    # ── Scripts ───────────────────────────────────────────────────────
    op.drop_column("scripts", "characters_per_script")
    op.drop_column("scripts", "total_convergence_points")

    # ── character_memories ────────────────────────────────────────────
    op.drop_index("idx_memory_importance", table_name="character_memories")
    op.drop_index("idx_memory_source", table_name="character_memories")
    op.drop_column("character_memories", "importance")

    # ── free_chat_sessions ────────────────────────────────────────────
    op.drop_index("idx_free_chat_character", table_name="free_chat_sessions")
    op.drop_constraint("free_chat_sessions_script_id_fkey",
                       "free_chat_sessions", type_="foreignkey")
    op.drop_constraint("free_chat_sessions_character_id_fkey",
                       "free_chat_sessions", type_="foreignkey")
    op.drop_column("free_chat_sessions", "script_id")
    op.drop_column("free_chat_sessions", "character_id")

    # ── affection_history (restore original narrow version) ───────────
    op.drop_index("idx_aff_history_created", table_name="affection_history")
    op.drop_index("idx_aff_history_user_char", table_name="affection_history")
    op.drop_table("affection_history")

    op.create_table(
        "affection_history",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("character_id", UUID(as_uuid=True), nullable=False),
        sa.Column("delta", sa.Integer(), nullable=False),
        sa.Column("old_value", sa.Integer(), nullable=False),
        sa.Column("new_value", sa.Integer(), nullable=False),
        sa.Column("old_level", sa.String(length=20), nullable=False),
        sa.Column("new_level", sa.String(length=20), nullable=False),
        sa.Column("reason", sa.String(length=50), server_default="choice"),
        sa.Column("source_session_id", UUID(as_uuid=True), nullable=True),
        sa.Column("source_choice_id", UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["character_id"], ["characters.id"]),
        sa.ForeignKeyConstraint(["source_session_id"], ["game_sessions.id"]),
        sa.ForeignKeyConstraint(["source_choice_id"], ["node_choices.id"]),
    )
    op.create_index("ix_affection_history_user_id", "affection_history",
                    ["user_id"])

    # ── user_personas ─────────────────────────────────────────────────
    op.drop_index("idx_persona_fav_chars", table_name="user_personas")
    op.drop_table("user_personas")

    # ── convergence_points ────────────────────────────────────────────
    op.drop_index("idx_convergence_chapter", table_name="convergence_points")
    op.drop_index("idx_convergence_script", table_name="convergence_points")
    op.drop_table("convergence_points")
