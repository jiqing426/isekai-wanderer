"""CR-030: Chapter structure refactor

Revision ID: cr030_chapter_structure
Revises: cr029_node_branch
Create Date: 2026-08-04

Changes:
- routes 表新增 chapter_number (INTEGER, nullable) 字段
- routes 表新增 chapter_type (VARCHAR(50), nullable) 字段
- 创建 3 个索引: ix_routes_chapter_number, ix_routes_chapter_type, ix_routes_script_chapter
- 数据迁移: 11 条现有 route 映射到章节结构
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'cr030_chapter_structure'
down_revision: Union[str, None] = 'cr029_node_branch'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    # Check if chapter_number column already exists
    result = conn.execute(sa.text(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_schema = 'public' AND table_name = 'routes' "
        "AND column_name = 'chapter_number'"
    ))

    if not result.first():
        # Add chapter_number column
        op.add_column(
            'routes',
            sa.Column('chapter_number', sa.Integer(), nullable=True,
                      comment='CR-030: Chapter number (1-4), NULL for backward compat')
        )
        print("CR-030: Added chapter_number column to routes table")
    else:
        print("CR-030: chapter_number column already exists, skipping")

    # Check if chapter_type column already exists
    result = conn.execute(sa.text(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_schema = 'public' AND table_name = 'routes' "
        "AND column_name = 'chapter_type'"
    ))

    if not result.first():
        # Add chapter_type column
        op.add_column(
            'routes',
            sa.Column('chapter_type', sa.String(50), nullable=True,
                      comment='CR-030: Chapter type (encounter/daily/conflict/convergence), NULL for backward compat')
        )
        print("CR-030: Added chapter_type column to routes table")
    else:
        print("CR-030: chapter_type column already exists, skipping")

    # Create indexes (IF NOT EXISTS)
    op.execute("CREATE INDEX IF NOT EXISTS ix_routes_chapter_number ON routes(chapter_number)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_routes_chapter_type ON routes(chapter_type)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_routes_script_chapter ON routes(script_id, chapter_number)")
    print("CR-030: Created indexes on routes table")

    # Data migration: map 11 existing routes to chapters
    # Mapping based on design.md:
    # 星月奇缘: 第一章=1/encounter, 第二章=2/daily, 第三章=3/conflict
    # 星辰之约: 星夜邂逅=1/encounter, 林辰线=2/daily, 流星线=3/conflict, 银河线=4/convergence
    # 樱花恋曲: 樱花树下=1/encounter, 月夜线=2/daily, 阳菜线=3/conflict, 雪乃线=4/convergence

    data_migration = [
        # (route_title_pattern, script_title, chapter_number, chapter_type)
        ('第一章：月夜邂逅', '星月奇缘', 1, 'encounter'),
        ('第二章：星辰之约', '星月奇缘', 2, 'daily'),
        ('第三章：命运交织', '星月奇缘', 3, 'conflict'),
        ('星夜邂逅', '星辰之约', 1, 'encounter'),
        ('林辰线：星光指引', '星辰之约', 2, 'daily'),
        ('流星线：刹那永恒', '星辰之约', 3, 'conflict'),
        ('银河线：命运交汇', '星辰之约', 4, 'convergence'),
        ('樱花树下', '樱花恋曲', 1, 'encounter'),
        ('月夜线：静谧之恋', '樱花恋曲', 2, 'daily'),
        ('阳菜线：夏日恋歌', '樱花恋曲', 3, 'conflict'),
        ('雪乃线：樱花树下的约定', '樱花恋曲', 4, 'convergence'),
    ]

    for route_title, script_title, chapter_number, chapter_type in data_migration:
        conn.execute(sa.text(
            "UPDATE routes SET chapter_number = :chapter_number, chapter_type = :chapter_type "
            "WHERE title = :route_title AND script_id = (SELECT id FROM scripts WHERE title = :script_title)"
        ), {
            'chapter_number': chapter_number,
            'chapter_type': chapter_type,
            'route_title': route_title,
            'script_title': script_title,
        })

    print("CR-030: Data migration completed for 11 routes")


def downgrade() -> None:
    op.drop_index('ix_routes_script_chapter', table_name='routes')
    op.drop_index('ix_routes_chapter_type', table_name='routes')
    op.drop_index('ix_routes_chapter_number', table_name='routes')
    op.drop_column('routes', 'chapter_type')
    op.drop_column('routes', 'chapter_number')
    print("CR-030: Rolled back chapter structure changes")
