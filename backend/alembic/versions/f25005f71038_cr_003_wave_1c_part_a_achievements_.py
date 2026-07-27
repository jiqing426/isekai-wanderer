"""cr_003_wave_1c_part_a_achievements_activity_chests

Revision ID: f25005f71038
Revises: c2b84460a40d
Create Date: 2026-07-18 21:46:07.715303
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f25005f71038'
down_revision: Union[str, None] = 'c2b84460a40d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # New tables for CR-003 Wave 1c Part A
    op.create_table('user_achievement_claims',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('achievement_id', sa.String(length=100), nullable=False),
    sa.Column('reward_type', sa.String(length=50), nullable=False),
    sa.Column('reward_amount', sa.Integer(), nullable=False),
    sa.Column('claimed_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_achievement_claims_user_id'), 'user_achievement_claims', ['user_id'], unique=False)

    op.create_table('activity_chest_claims',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('chest_tier', sa.Integer(), nullable=False),
    sa.Column('claimed_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_activity_chest_claims_user_id'), 'activity_chest_claims', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_activity_chest_claims_user_id'), table_name='activity_chest_claims')
    op.drop_table('activity_chest_claims')
    op.drop_index(op.f('ix_user_achievement_claims_user_id'), table_name='user_achievement_claims')
    op.drop_table('user_achievement_claims')
