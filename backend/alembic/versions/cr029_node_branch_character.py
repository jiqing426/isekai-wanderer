"""CR-029: Node branch character filtering

Revision ID: cr029_node_branch
Revises: cr028_character_playable
Create Date: 2026-08-03

Changes:
- nodes 表新增 character_id 字段（UUID，可空）
- 创建索引 ix_nodes_character_id
- NULL = 公共节点，非 NULL = 分支节点仅该角色可见
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


revision: str = 'cr029_node_branch'
down_revision: Union[str, None] = 'cr028_character_playable'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    # Check if character_id column already exists
    result = conn.execute(sa.text(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_schema = 'public' AND table_name = 'nodes' "
        "AND column_name = 'character_id'"
    ))
    
    if not result.first():
        # Add character_id column (nullable, FK to characters)
        op.add_column(
            'nodes',
            sa.Column(
                'character_id',
                UUID(as_uuid=True),
                sa.ForeignKey('characters.id'),
                nullable=True,
                comment='CR-029: NULL=public node, non-NULL=branch node visible only to this character'
            )
        )
        
        # Create index for filtering
        op.create_index('ix_nodes_character_id', 'nodes', ['character_id'])
        
        print("CR-029: Added character_id column and index to nodes table")
    else:
        print("CR-029: character_id column already exists, skipping")


def downgrade() -> None:
    op.drop_index('ix_nodes_character_id', table_name='nodes')
    op.drop_column('nodes', 'character_id')
