"""cr_003_add_routes_branch_columns_and_node_choice_columns

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-07-24 02:55:00.000000

Fixes BUG-CR3-004: routes.branch_type/branch_label/branch_condition missing.
Also adds node_choices columns if missing (CR3-047 choice_streak).
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add branch columns to routes table (CR3-051 multi-branch routing)
    op.add_column('routes', sa.Column('branch_type', sa.String(length=50), nullable=True, comment='Branch category: main, branch_a, branch_b, secret'))
    op.add_column('routes', sa.Column('branch_label', sa.String(length=100), nullable=True, comment='Human-readable branch identifier'))
    op.add_column('routes', sa.Column('branch_condition', sa.JSON(), nullable=True, comment='Condition to enter this branch'))

    # Add columns to node_choices if they don't exist (CR3-047 choice_streak)
    op.add_column('node_choices', sa.Column('hidden', sa.Boolean(), nullable=True, server_default='false', comment='Hidden choice requiring condition'))
    op.add_column('node_choices', sa.Column('hint', sa.String(length=255), nullable=True, comment='Hint text for locked choices'))
    op.add_column('node_choices', sa.Column('required_condition', sa.JSON(), nullable=True, comment='Condition to unlock this choice'))


def downgrade() -> None:
    op.drop_column('node_choices', 'required_condition')
    op.drop_column('node_choices', 'hint')
    op.drop_column('node_choices', 'hidden')
    op.drop_column('routes', 'branch_condition')
    op.drop_column('routes', 'branch_label')
    op.drop_column('routes', 'branch_type')
