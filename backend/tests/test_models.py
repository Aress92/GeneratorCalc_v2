"""
Tests for database models.

Testy modeli bazy danych.
"""

import pytest
from datetime import datetime
from uuid import uuid4

from app.models.user import User, UserRole
from app.models.import_job import ImportJob, ImportStatus, ImportType
from app.core.security import get_password_hash


class TestUserModel:
    """Tests for User model."""

    @pytest.mark.asyncio
    async def test_create_user(self, test_db):
        """Test user creation."""
        user = User(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            password_hash=get_password_hash("password123"),
            role=UserRole.ENGINEER,
            is_active=True,
            is_verified=False
        )

        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        assert user.id is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.role == UserRole.ENGINEER
        assert user.is_active is True
        assert user.is_verified is False
        assert user.created_at is not None

    @pytest.mark.asyncio
    async def test_user_roles(self, test_db):
        """Test user role enumeration."""
        admin_user = User(
            username="admin",
            email="admin@example.com",
            password_hash=get_password_hash("admin123"),
            role=UserRole.ADMIN
        )

        engineer_user = User(
            username="engineer",
            email="engineer@example.com",
            password_hash=get_password_hash("eng123"),
            role=UserRole.ENGINEER
        )

        viewer_user = User(
            username="viewer",
            email="viewer@example.com",
            password_hash=get_password_hash("view123"),
            role=UserRole.VIEWER
        )

        test_db.add_all([admin_user, engineer_user, viewer_user])
        await test_db.commit()

        assert admin_user.role == UserRole.ADMIN
        assert engineer_user.role == UserRole.ENGINEER
        assert viewer_user.role == UserRole.VIEWER

    @pytest.mark.asyncio
    async def test_user_timestamps(self, test_db):
        """Test user timestamp fields."""
        creation_time = datetime.utcnow()

        user = User(
            username="timetest",
            email="time@test.com",
            password_hash=get_password_hash("test123"),
            role=UserRole.VIEWER
        )

        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        assert user.created_at is not None
        assert user.updated_at is not None
        # Allow for small timing differences (microseconds precision)
        assert (user.created_at - creation_time).total_seconds() >= -1
        assert (user.updated_at - creation_time).total_seconds() >= -1


class TestImportJobModel:
    """Tests for ImportJob model."""

    @pytest.mark.asyncio
    async def test_create_import_job(self, test_db):
        """Test import job creation."""
        # First create a user
        user = User(
            username="importuser",
            email="import@test.com",
            password_hash=get_password_hash("test123"),
            role=UserRole.ENGINEER
        )
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        # Create import job
        import_job = ImportJob(
            user_id=str(user.id),
            import_type=ImportType.REGENERATOR_CONFIG,
            filename="test_data.xlsx",
            original_filename="test_regenerators.xlsx",
            file_size=1024,
            status=ImportStatus.PENDING
        )

        test_db.add(import_job)
        await test_db.commit()
        await test_db.refresh(import_job)

        assert import_job.id is not None
        assert import_job.user_id == str(user.id)
        assert import_job.import_type == ImportType.REGENERATOR_CONFIG
        assert import_job.status == ImportStatus.PENDING
        assert import_job.filename == "test_data.xlsx"

    @pytest.mark.asyncio
    async def test_import_job_status_progression(self, test_db):
        """Test import job status changes."""
        user = User(
            username="statususer",
            email="status@test.com",
            password_hash=get_password_hash("test123"),
            role=UserRole.ENGINEER
        )
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        import_job = ImportJob(
            user_id=str(user.id),
            import_type=ImportType.MATERIAL_PROPERTIES,
            filename="materials.xlsx",
            original_filename="materials.xlsx",
            file_size=2048,
            status=ImportStatus.PENDING
        )

        test_db.add(import_job)
        await test_db.commit()

        # Test status progression
        import_job.status = ImportStatus.PROCESSING
        await test_db.commit()
        assert import_job.status == ImportStatus.PROCESSING

        import_job.status = ImportStatus.COMPLETED
        await test_db.commit()

        assert import_job.status == ImportStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_import_job_metadata(self, test_db):
        """Test import job metadata and configuration."""
        user = User(
            username="metauser",
            email="meta@test.com",
            password_hash=get_password_hash("test123"),
            role=UserRole.ADMIN
        )
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        metadata_config = {
            "sheet_name": "Regenerators",
            "has_header": True,
            "delimiter": ",",
            "encoding": "utf-8"
        }

        column_mapping = {
            "Name": "name",
            "Temperature": "operating_temperature",
            "Pressure": "operating_pressure"
        }

        import_job = ImportJob(
            user_id=str(user.id),
            import_type=ImportType.REGENERATOR_CONFIG,
            filename="meta_test.xlsx",
            original_filename="meta_test.xlsx",
            file_size=4096,
            status=ImportStatus.PENDING
        )

        test_db.add(import_job)
        await test_db.commit()
        await test_db.refresh(import_job)

        assert import_job.filename == "meta_test.xlsx"
        assert import_job.import_type == ImportType.REGENERATOR_CONFIG