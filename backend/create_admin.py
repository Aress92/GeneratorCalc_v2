#!/usr/bin/env python3
"""
Create admin user script.
"""

import asyncio
from app.core.database import AsyncSessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash
from sqlalchemy import select

async def create_admin():
    """Create admin user."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.username == 'admin'))
        if result.scalar():
            print('Admin user already exists')
            return

        admin_user = User(
            username='admin',
            email='admin@forglass.com',
            full_name='System Administrator',
            password_hash=get_password_hash('admin'),
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True
        )
        db.add(admin_user)
        await db.commit()
        print('Admin user created successfully (username: admin, password: admin)')

if __name__ == "__main__":
    asyncio.run(create_admin())