"""Initial schema — screens, alarms, device_status tables.

Revision ID: 001
Revises:
Create Date: 2026-01-31

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import inspect

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)
    existing_tables = inspector.get_table_names()

    if "screens" not in existing_tables:
        op.execute("""
            CREATE TABLE screens (
                id UUID PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                content TEXT NOT NULL DEFAULT '',
                screen_type VARCHAR(50) NOT NULL DEFAULT 'text',
                is_active BOOLEAN NOT NULL DEFAULT true,
                display_order INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT now(),
                updated_at TIMESTAMP DEFAULT now()
            )
        """)

    if "alarms" not in existing_tables:
        op.execute("""
            CREATE TABLE alarms (
                id UUID PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                trigger_time TIME NOT NULL,
                message TEXT NOT NULL DEFAULT '',
                status VARCHAR(50) NOT NULL DEFAULT 'active',
                repeat_days INTEGER[] NOT NULL DEFAULT '{}',
                created_at TIMESTAMP DEFAULT now(),
                updated_at TIMESTAMP DEFAULT now()
            )
        """)

    if "device_status" not in existing_tables:
        op.execute("""
            CREATE TABLE device_status (
                id UUID PRIMARY KEY,
                device_id VARCHAR(100) NOT NULL UNIQUE,
                ip_address VARCHAR(45) NOT NULL DEFAULT '',
                firmware_version VARCHAR(50) NOT NULL DEFAULT '',
                battery_level INTEGER,
                last_seen TIMESTAMP DEFAULT now()
            )
        """)
        op.execute("CREATE INDEX ix_device_status_device_id ON device_status (device_id)")


def downgrade() -> None:
    op.drop_table("device_status")
    op.drop_table("alarms")
    op.drop_table("screens")
