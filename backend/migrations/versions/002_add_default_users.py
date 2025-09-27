"""Add default users for testing

Revision ID: 002_add_default_users
Revises: 001_initial_migration
Create Date: 2025-01-23 22:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, DateTime, Boolean
from datetime import datetime
import uuid

from app.core.security import get_password_hash

# revision identifiers, used by Alembic.
revision: str = '002_add_default_users'
down_revision: Union[str, None] = '001_initial_migration'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add default users for testing."""

    # Create a table representation for bulk insert
    users_table = table('users',
        column('id', String),
        column('username', String),
        column('email', String),
        column('full_name', String),
        column('password_hash', String),
        column('role', String),
        column('is_active', Boolean),
        column('is_verified', Boolean),
        column('created_at', DateTime),
        column('updated_at', DateTime),
    )

    # Default users data
    now = datetime.utcnow()

    default_users = [
        {
            'id': str(uuid.uuid4()),
            'username': 'admin',
            'email': 'admin@forglass.local',
            'full_name': 'System Administrator',
            'password_hash': get_password_hash('Admin123!'),
            'role': 'ADMIN',
            'is_active': True,
            'is_verified': True,
            'created_at': now,
            'updated_at': now,
        },
        {
            'id': str(uuid.uuid4()),
            'username': 'engineer',
            'email': 'engineer@forglass.local',
            'full_name': 'Jan Kowalski',
            'password_hash': get_password_hash('Engineer123!'),
            'role': 'ENGINEER',
            'is_active': True,
            'is_verified': True,
            'created_at': now,
            'updated_at': now,
        },
        {
            'id': str(uuid.uuid4()),
            'username': 'viewer',
            'email': 'viewer@forglass.local',
            'full_name': 'Anna Nowak',
            'password_hash': get_password_hash('Viewer123!'),
            'role': 'VIEWER',
            'is_active': True,
            'is_verified': True,
            'created_at': now,
            'updated_at': now,
        },
    ]

    # Insert default users
    op.bulk_insert(users_table, default_users)


def downgrade() -> None:
    """Remove default users."""

    # Remove default users by username
    op.execute(
        "DELETE FROM users WHERE username IN ('admin', 'engineer', 'viewer')"
    )