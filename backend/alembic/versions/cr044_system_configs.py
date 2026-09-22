"""CR-044: system_configs table for runtime configuration

Revision ID: cr044_system_configs
Revises: cr044_db_cleanup
Create Date: 2026-09-20

Creates system_configs table and seeds initial config values.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'cr044_system_configs'
down_revision = 'cr044_db_cleanup'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'system_configs',
        sa.Column('key', sa.String(100), primary_key=True),
        sa.Column('value', sa.Text, nullable=True),
        sa.Column('category', sa.String(50), server_default='general'),
        sa.Column('description', sa.String(255), nullable=True),
        sa.Column('is_secret', sa.Boolean, server_default='false'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Seed initial config values
    configs = [
        ('app_url', '', 'general', 'Application URL for email links', False),
        ('smtp_host', '', 'email', 'SMTP server host', False),
        ('smtp_port', '587', 'email', 'SMTP server port', False),
        ('smtp_user', '', 'email', 'SMTP username', False),
        ('smtp_password', '', 'email', 'SMTP password/auth code', True),
        ('smtp_from', '', 'email', 'Sender email address', False),
        ('jwt_secret', '', 'security', 'JWT signing secret', True),
    ]

    for key, value, category, description, is_secret in configs:
        op.execute(
            f"INSERT INTO system_configs (key, value, category, description, is_secret) "
            f"VALUES ('{key}', '{value}', '{category}', '{description}', {str(is_secret).lower()}) "
            f"ON CONFLICT (key) DO NOTHING;"
        )


def downgrade() -> None:
    op.drop_table('system_configs')
