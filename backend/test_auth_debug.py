#!/usr/bin/env python3
"""
Debug authentication issue.
"""

import asyncio
from uuid import UUID

from app.core.database import AsyncSessionLocal
from app.core.security import verify_token
from app.models.user import User
from sqlalchemy import select

async def debug_auth():
    """Debug authentication flow."""

    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTg3MDA5OTgsInN1YiI6IjY0YzQxMzE1LTllYjUtNDg3OC1iY2RiLTNlOTQzODQ3ZTc2ZiIsImlhdCI6MTc1ODY3MjE5OCwidHlwZSI6ImFjY2VzcyIsInVzZXJuYW1lIjoiYWRtaW4iLCJyb2xlIjoiQURNSU4iLCJpc192ZXJpZmllZCI6dHJ1ZX0.z839r2BSO4eletUYee11OIlBE3b32qFpjqMWLXl-U6g"

    print("Step 1: Verify token")
    payload = verify_token(token)
    if not payload:
        print("❌ Token verification failed")
        return
    print(f"✅ Token payload: {payload}")

    print("\nStep 2: Extract user ID")
    user_id_str = payload.get("sub")
    if not user_id_str:
        print("❌ No 'sub' in token")
        return
    print(f"✅ User ID string: {user_id_str}")

    print("\nStep 3: Convert to UUID")
    try:
        user_id = UUID(user_id_str)
        print(f"✅ UUID object: {user_id}")
        print(f"✅ UUID type: {type(user_id)}")
    except ValueError as e:
        print(f"❌ UUID conversion failed: {e}")
        return

    print("\nStep 4: Query database")
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()

            if user:
                print(f"✅ User found: {user.username} ({user.id})")
                print(f"✅ User active: {user.is_active}")
            else:
                print("❌ User not found in database")

                # Let's also try a direct query to see what's in the database
                print("\nStep 5: Check all users in database")
                all_users = await db.execute(select(User.id, User.username))
                for db_user in all_users.all():
                    print(f"  DB User: {db_user.id} ({type(db_user.id)}) - {db_user.username}")
                    print(f"  Comparison: {db_user.id == user_id} | {str(db_user.id) == str(user_id)}")

        except Exception as e:
            print(f"❌ Database query failed: {e}")

if __name__ == "__main__":
    asyncio.run(debug_auth())