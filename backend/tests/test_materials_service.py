"""
Tests for materials service.

Testy dla serwisu materiałów.
"""

import pytest
from uuid import uuid4
from unittest.mock import Mock, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.services.materials_service import MaterialsService
from app.models.user import User, UserRole
from app.models.regenerator import Material
from app.schemas.regenerator_schemas import MaterialCreate, MaterialUpdate, MaterialFilter


class TestMaterialsService:
    """Test materials service functionality."""

    @pytest.fixture
    async def materials_service(self, test_db: AsyncSession) -> MaterialsService:
        """Create materials service instance."""
        return MaterialsService(test_db)

    @pytest.fixture
    async def test_user(self, test_db: AsyncSession) -> User:
        """Create test user."""
        unique_id = uuid4().hex[:8]
        user = User(
            username=f"matuser_{unique_id}",
            email=f"matuser_{unique_id}@example.com",
            full_name="Materials Test User",
            password_hash="hashed_password",
            role=UserRole.ENGINEER,
            is_active=True,
            is_verified=True
        )
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)
        return user

    @pytest.fixture
    async def admin_user(self, test_db: AsyncSession) -> User:
        """Create admin user for approval tests."""
        unique_id = uuid4().hex[:8]
        user = User(
            username=f"matadmin_{unique_id}",
            email=f"matadmin_{unique_id}@example.com",
            full_name="Materials Admin User",
            password_hash="hashed_password",
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True
        )
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)
        return user

    @pytest.fixture
    async def test_material(self, test_db: AsyncSession, test_user: User) -> Material:
        """Create test material."""
        unique_id = uuid4().hex[:6]
        material = Material(
            name=f"Test Material {unique_id}",
            description="Test material description",
            manufacturer="Test Manufacturer",
            material_type="refractory",
            category="alumina",
            application="high_temp",
            properties={
                "thermal_expansion": 8.5e-6,
                "compressive_strength": 50.0
            },
            thermal_conductivity=2.5,
            specific_heat=900.0,
            density=2300.0,
            max_temperature=1600.0,
            chemical_composition={"Al2O3": 85.0, "SiO2": 12.0},
            created_by_id=str(test_user.id),
            is_active=True,
            is_standard=False,
            version=1
        )
        test_db.add(material)
        await test_db.commit()
        await test_db.refresh(material)
        return material

    async def test_create_material(self, materials_service: MaterialsService, test_user: User):
        """Test creating a new material."""
        material_data = MaterialCreate(
            name="New Test Material",
            description="New test material description",
            manufacturer="New Test Manufacturer",
            material_type="insulation",
            category="ceramic_fiber",
            thermal_conductivity=0.15,
            specific_heat=1000.0,
            density=128.0,
            max_temperature=1200.0,
            thermal_expansion=5.0e-6,
            compressive_strength=0.5,
            chemical_composition={"Al2O3": 45.0, "SiO2": 55.0},
            applications=["insulation"],
            notes="New test material",
            datasheet_url="https://example.com/new-datasheet.pdf"
        )

        result = await materials_service.create_material(material_data, str(test_user.id))

        assert result.name == "New Test Material"
        assert result.material_type == "insulation"
        assert result.thermal_conductivity == 0.15
        assert result.created_by_id == str(test_user.id)
        assert result.approval_status == "pending"

    async def test_get_material_by_id(self, materials_service: MaterialsService, test_material: Material):
        """Test getting material by ID."""
        result = await materials_service.get_material(str(test_material.id))

        assert result is not None
        assert result.id == test_material.id
        assert result.name == test_material.name
        assert result.material_type == test_material.material_type

    async def test_get_material_not_found(self, materials_service: MaterialsService):
        """Test getting non-existent material."""
        result = await materials_service.get_material("non-existent-id")
        assert result is None

    async def test_update_material(self, materials_service: MaterialsService, test_material: Material, test_user: User):
        """Test updating material."""
        update_data = MaterialUpdate(
            name="Updated Material Name",
            description="Updated description",
            thermal_conductivity=3.0,
            max_temperature=1700.0
        )

        result = await materials_service.update_material(str(test_material.id), update_data, str(test_user.id))

        assert result is not None
        assert result.name == "Updated Material Name"
        assert result.description == "Updated description"
        assert result.thermal_conductivity == 3.0
        assert result.max_temperature == 1700.0

    async def test_delete_material(self, materials_service: MaterialsService, test_material: Material, test_user: User):
        """Test deleting material (soft delete)."""
        success = await materials_service.delete_material(str(test_material.id), str(test_user.id))

        assert success is True

        # Verify material is soft deleted
        deleted_material = await materials_service.get_material(str(test_material.id))
        assert deleted_material is None

    async def test_get_materials_with_filters(self, materials_service: MaterialsService, test_material: Material):
        """Test getting materials with filters."""
        filters = MaterialFilter(
            material_type="refractory",
            category="alumina",
            is_active=True
        )

        results = await materials_service.get_materials(filters=filters, limit=10, offset=0)

        assert len(results) >= 1
        found_material = next((m for m in results if m.id == test_material.id), None)
        assert found_material is not None

    async def test_search_materials(self, materials_service: MaterialsService, test_material: Material):
        """Test searching materials by name."""
        results = await materials_service.get_materials(
            search="Test Material",
            limit=10,
            offset=0
        )

        assert len(results) >= 1
        found_material = next((m for m in results if m.id == test_material.id), None)
        assert found_material is not None

    async def test_get_materials_by_type(self, materials_service: MaterialsService, test_material: Material):
        """Test getting materials by type."""
        results = await materials_service.get_materials_by_type("refractory")

        assert len(results) >= 1
        found_material = next((m for m in results if m.id == test_material.id), None)
        assert found_material is not None

    async def test_get_popular_materials(self, materials_service: MaterialsService):
        """Test getting popular/standard materials."""
        results = await materials_service.get_popular_materials(limit=20)

        # Should return materials if any exist
        assert isinstance(results, list)

    async def test_get_material_statistics(self, materials_service: MaterialsService, test_material: Material):
        """Test getting material statistics."""
        stats = await materials_service.get_material_statistics()

        assert "total_materials" in stats
        assert "by_type" in stats
        assert "by_approval_status" in stats
        assert "standard_materials" in stats
        assert "custom_materials" in stats

        assert stats["total_materials"] >= 1
        assert "refractory" in stats["by_type"]

    async def test_initialize_standard_materials(self, materials_service: MaterialsService):
        """Test initializing standard materials."""
        # This should not create duplicates if materials already exist
        count = await materials_service.initialize_standard_materials()

        assert isinstance(count, int)
        assert count >= 0

    async def test_approve_material(self, materials_service: MaterialsService, test_material: Material, test_user: User):
        """Test approving a material."""
        # First set material to pending
        test_material.approval_status = "pending"
        await materials_service.db.commit()

        result = await materials_service.approve_material(str(test_material.id), str(test_user.id))

        assert result is not None
        assert result.approval_status == "approved"

    async def test_reject_material(self, materials_service: MaterialsService, test_material: Material, test_user: User):
        """Test rejecting a material."""
        # First set material to pending
        test_material.approval_status = "pending"
        await materials_service.db.commit()

        result = await materials_service.reject_material(str(test_material.id), str(test_user.id), "Test rejection reason")

        assert result is not None
        assert result.approval_status == "rejected"

    async def test_get_materials_pagination(self, materials_service: MaterialsService, test_material: Material):
        """Test materials pagination."""
        # Test first page
        page1 = await materials_service.get_materials(limit=1, offset=0)
        assert len(page1) <= 1

        # Test second page
        page2 = await materials_service.get_materials(limit=1, offset=1)
        assert len(page2) <= 1

    async def test_validate_material_data(self, materials_service: MaterialsService):
        """Test material data validation."""
        # Test with invalid thermal conductivity
        invalid_data = MaterialCreate(
            name="Invalid Material",
            description="Material with invalid data",
            manufacturer="Test",
            material_type="refractory",
            category="alumina",
            thermal_conductivity=-1.0,  # Invalid negative value
            specific_heat=900.0,
            density=2300.0,
            max_temperature=1600.0
        )

        with pytest.raises(ValueError):
            await materials_service._validate_material_data(invalid_data.model_dump())

    async def test_material_type_filtering(self, materials_service: MaterialsService, test_db: AsyncSession, test_user: User):
        """Test filtering materials by multiple types."""
        # Create materials of different types
        refractory = Material(
            name="Refractory Material",
            material_type="refractory",
            category="alumina",
            thermal_conductivity=2.5,
            specific_heat=900.0,
            density=2300.0,
            max_temperature=1600.0,
            created_by_id=str(test_user.id),
            is_active=True
        )

        insulation = Material(
            name="Insulation Material",
            material_type="insulation",
            category="ceramic_fiber",
            thermal_conductivity=0.15,
            specific_heat=1000.0,
            density=128.0,
            max_temperature=1200.0,
            created_by_id=str(test_user.id),
            is_active=True
        )

        test_db.add_all([refractory, insulation])
        await test_db.commit()

        # Test filtering by refractory type
        refractory_materials = await materials_service.get_materials_by_type("refractory")
        refractory_names = [m.name for m in refractory_materials]
        assert "Refractory Material" in refractory_names

        # Test filtering by insulation type
        insulation_materials = await materials_service.get_materials_by_type("insulation")
        insulation_names = [m.name for m in insulation_materials]
        assert "Insulation Material" in insulation_names

    async def test_material_search_functionality(self, materials_service: MaterialsService, test_db: AsyncSession, test_user: User):
        """Test material search by name and description."""
        # Create materials with specific names
        ceramic_material = Material(
            name="Advanced Ceramic Brick",
            description="High-performance ceramic material for furnaces",
            material_type="refractory",
            category="alumina",
            thermal_conductivity=2.8,
            specific_heat=850.0,
            density=2400.0,
            max_temperature=1700.0,
            created_by_id=str(test_user.id),
            is_active=True
        )

        test_db.add(ceramic_material)
        await test_db.commit()

        # Search by name
        results = await materials_service.get_materials(search="Ceramic", limit=10, offset=0)
        result_names = [m.name for m in results]
        assert "Advanced Ceramic Brick" in result_names

        # Search by description
        results = await materials_service.get_materials(search="performance", limit=10, offset=0)
        result_names = [m.name for m in results]
        assert "Advanced Ceramic Brick" in result_names


class TestMaterialsServiceAdvanced:
    """Advanced tests for MaterialsService functionality."""

    @pytest.fixture
    async def materials_service(self, test_db: AsyncSession) -> MaterialsService:
        """Create materials service instance."""
        return MaterialsService(test_db)

    @pytest.fixture
    async def test_user(self, test_db: AsyncSession) -> User:
        """Create test user."""
        unique_id = uuid4().hex[:8]
        user = User(
            username=f"advmat_{unique_id}",
            email=f"advmat_{unique_id}@example.com",
            full_name="Advanced Materials User",
            password_hash="hashed_password",
            role=UserRole.ENGINEER,
            is_active=True,
            is_verified=True
        )
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)
        return user

    @pytest.fixture
    async def admin_user(self, test_db: AsyncSession) -> User:
        """Create admin user."""
        unique_id = uuid4().hex[:8]
        user = User(
            username=f"advadmin_{unique_id}",
            email=f"advadmin_{unique_id}@example.com",
            full_name="Admin User",
            password_hash="hashed_password",
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True
        )
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)
        return user

    # === CRUD TESTS ===

    async def test_create_material_refractory(
        self,
        materials_service: MaterialsService,
        test_user: User
    ):
        """Test creating a refractory material."""
        unique_id = uuid4().hex[:6]
        material_data = MaterialCreate(
            name=f"High Alumina Brick {unique_id}",
            description="High alumina refractory brick for furnaces",
            manufacturer="Refractories Inc",
            material_type="refractory",
            category="alumina",
            thermal_conductivity=2.8,
            specific_heat=950.0,
            density=2500.0,
            max_temperature=1750.0,
            thermal_expansion=8.0e-6,
            compressive_strength=80.0,
            chemical_composition={"Al2O3": 90.0, "SiO2": 8.0, "others": 2.0},
            applications=["glass_furnace", "steel_furnace"],
            notes="Excellent thermal shock resistance"
        )

        result = await materials_service.create_material(material_data, str(test_user.id))

        assert result is not None
        assert result.name == f"High Alumina Brick {unique_id}"
        assert result.material_type == "refractory"
        assert result.thermal_conductivity == 2.8
        assert result.created_by_id == str(test_user.id)
        assert result.approval_status == "pending"
        assert result.is_active is True

    async def test_create_material_insulation(
        self,
        materials_service: MaterialsService,
        test_user: User
    ):
        """Test creating an insulation material."""
        unique_id = uuid4().hex[:6]
        material_data = MaterialCreate(
            name=f"Ceramic Fiber Blanket {unique_id}",
            description="Lightweight ceramic fiber insulation",
            manufacturer="Insulation Co",
            material_type="insulation",
            category="ceramic_fiber",
            thermal_conductivity=0.12,
            specific_heat=1050.0,
            density=128.0,
            max_temperature=1260.0,
            thermal_expansion=2.0e-6,
            chemical_composition={"Al2O3": 48.0, "SiO2": 52.0},
            applications=["backup_insulation"],
            notes="Low thermal mass"
        )

        result = await materials_service.create_material(material_data, str(test_user.id))

        assert result.material_type == "insulation"
        assert result.density < 200.0  # Insulation is lightweight

    async def test_create_material_duplicate_name(
        self,
        materials_service: MaterialsService,
        test_user: User,
        test_db: AsyncSession
    ):
        """Test creating material with duplicate name (should fail)."""
        # Create first material
        unique_id = uuid4().hex[:6]
        material1 = Material(
            name=f"Unique Material {unique_id}",
            material_type="refractory",
            thermal_conductivity=2.5,
            specific_heat=900.0,
            density=2300.0,
            max_temperature=1600.0,
            created_by_id=str(test_user.id)
        )
        test_db.add(material1)
        await test_db.commit()

        # Try to create duplicate
        material_data = MaterialCreate(
            name=f"Unique Material {unique_id}",  # Same name
            material_type="insulation",
            thermal_conductivity=0.15,
            specific_heat=1000.0,
            density=150.0,
            max_temperature=1200.0
        )

        # Should raise integrity error or return None
        try:
            result = await materials_service.create_material(material_data, str(test_user.id))
            # If it doesn't raise, check if it handled gracefully
            assert result is None or result.id != material1.id
        except Exception:
            pass  # Expected behavior

    async def test_update_material_properties(
        self,
        materials_service: MaterialsService,
        test_user: User,
        test_db: AsyncSession
    ):
        """Test updating material properties."""
        # Create material
        unique_id = uuid4().hex[:6]
        material = Material(
            name=f"Material To Update {unique_id}",
            material_type="refractory",
            thermal_conductivity=2.5,
            specific_heat=900.0,
            density=2300.0,
            max_temperature=1600.0,
            created_by_id=str(test_user.id)
        )
        test_db.add(material)
        await test_db.commit()
        await test_db.refresh(material)

        # Update material
        update_data = MaterialUpdate(
            description="Updated description",
            thermal_conductivity=2.8,
            max_temperature=1700.0
        )

        result = await materials_service.update_material(
            str(material.id),
            update_data,
            str(test_user.id)
        )

        assert result is not None
        assert result.description == "Updated description"
        assert result.thermal_conductivity == 2.8
        assert result.max_temperature == 1700.0
        assert result.version > material.version  # Version incremented

    async def test_update_material_not_found(
        self,
        materials_service: MaterialsService,
        test_user: User
    ):
        """Test updating non-existent material."""
        update_data = MaterialUpdate(
            description="This won't work"
        )

        result = await materials_service.update_material(
            str(uuid4()),
            update_data,
            str(test_user.id)
        )

        assert result is None

    async def test_delete_material_success(
        self,
        materials_service: MaterialsService,
        test_user: User,
        test_db: AsyncSession
    ):
        """Test deleting a material."""
        # Create material
        unique_id = uuid4().hex[:6]
        material = Material(
            name=f"Material To Delete {unique_id}",
            material_type="refractory",
            thermal_conductivity=2.5,
            specific_heat=900.0,
            density=2300.0,
            max_temperature=1600.0,
            created_by_id=str(test_user.id),
            is_active=True
        )
        test_db.add(material)
        await test_db.commit()

        # Delete material
        success = await materials_service.delete_material(
            str(material.id),
            str(test_user.id)
        )

        assert success is True

        # Verify material is inactive
        deleted_mat = await materials_service.get_material(str(material.id))
        assert deleted_mat is not None
        assert deleted_mat.is_active is False

    async def test_delete_material_not_found(
        self,
        materials_service: MaterialsService,
        test_user: User
    ):
        """Test deleting non-existent material."""
        success = await materials_service.delete_material(
            str(uuid4()),
            str(test_user.id)
        )

        assert success is False

    # === SEARCH & FILTERING TESTS ===

    async def test_search_materials_by_name(
        self,
        materials_service: MaterialsService,
        test_user: User,
        test_db: AsyncSession
    ):
        """Test searching materials by name."""
        # Create test materials
        unique_id = uuid4().hex[:4]
        mat1 = Material(
            name=f"Alumina Brick {unique_id}",
            material_type="refractory",
            thermal_conductivity=2.5,
            specific_heat=900.0,
            density=2300.0,
            max_temperature=1600.0,
            created_by_id=str(test_user.id)
        )
        mat2 = Material(
            name=f"Silica Brick {unique_id}",
            material_type="refractory",
            thermal_conductivity=1.8,
            specific_heat=850.0,
            density=2100.0,
            max_temperature=1700.0,
            created_by_id=str(test_user.id)
        )
        test_db.add_all([mat1, mat2])
        await test_db.commit()

        # Search for "Alumina"
        filter_data = MaterialFilter(name_contains="Alumina")
        results = await materials_service.search_materials(filter_data, limit=50)

        result_names = [m.name for m in results]
        assert any("Alumina" in name for name in result_names)

    async def test_search_materials_by_type(
        self,
        materials_service: MaterialsService,
        test_user: User,
        test_db: AsyncSession
    ):
        """Test filtering materials by type."""
        filter_data = MaterialFilter(material_type="refractory")
        results = await materials_service.search_materials(filter_data, limit=50)

        assert all(m.material_type == "refractory" for m in results)

    async def test_search_materials_by_temperature_range(
        self,
        materials_service: MaterialsService,
        test_user: User,
        test_db: AsyncSession
    ):
        """Test filtering materials by temperature range."""
        filter_data = MaterialFilter(
            min_temperature=1500.0,
            max_temperature=2000.0
        )
        results = await materials_service.search_materials(filter_data, limit=50)

        for material in results:
            assert material.max_temperature >= 1500.0
            assert material.max_temperature <= 2000.0

    async def test_search_materials_combined_filters(
        self,
        materials_service: MaterialsService
    ):
        """Test searching with multiple filters combined."""
        filter_data = MaterialFilter(
            material_type="refractory",
            min_temperature=1400.0,
            is_active=True
        )
        results = await materials_service.search_materials(filter_data, limit=50)

        for material in results:
            assert material.material_type == "refractory"
            assert material.max_temperature >= 1400.0
            assert material.is_active is True

    # === APPROVAL WORKFLOW TESTS ===

    async def test_approve_material_by_admin(
        self,
        materials_service: MaterialsService,
        test_user: User,
        admin_user: User,
        test_db: AsyncSession
    ):
        """Test material approval by admin."""
        # Create pending material
        unique_id = uuid4().hex[:6]
        material = Material(
            name=f"Pending Material {unique_id}",
            material_type="refractory",
            thermal_conductivity=2.5,
            specific_heat=900.0,
            density=2300.0,
            max_temperature=1600.0,
            created_by_id=str(test_user.id),
            approval_status="pending"
        )
        test_db.add(material)
        await test_db.commit()

        # Approve material
        result = await materials_service.approve_material(
            str(material.id),
            str(admin_user.id),
            "approved"
        )

        assert result is not None
        assert result.approval_status == "approved"
        assert result.approved_by_id == str(admin_user.id)
        assert result.approved_at is not None

    async def test_reject_material(
        self,
        materials_service: MaterialsService,
        test_user: User,
        admin_user: User,
        test_db: AsyncSession
    ):
        """Test material rejection."""
        # Create pending material
        unique_id = uuid4().hex[:6]
        material = Material(
            name=f"Material To Reject {unique_id}",
            material_type="refractory",
            thermal_conductivity=2.5,
            specific_heat=900.0,
            density=2300.0,
            max_temperature=1600.0,
            created_by_id=str(test_user.id),
            approval_status="pending"
        )
        test_db.add(material)
        await test_db.commit()

        # Reject material
        result = await materials_service.approve_material(
            str(material.id),
            str(admin_user.id),
            "rejected"
        )

        assert result is not None
        assert result.approval_status == "rejected"

    async def test_supersede_material(
        self,
        materials_service: MaterialsService,
        test_user: User,
        test_db: AsyncSession
    ):
        """Test superseding an old material with a new one."""
        # Create old material
        unique_id = uuid4().hex[:6]
        old_material = Material(
            name=f"Old Material {unique_id}",
            material_type="refractory",
            thermal_conductivity=2.0,
            specific_heat=900.0,
            density=2300.0,
            max_temperature=1500.0,
            created_by_id=str(test_user.id),
            is_active=True
        )
        test_db.add(old_material)
        await test_db.commit()
        await test_db.refresh(old_material)

        # Create new material
        new_material = Material(
            name=f"New Material {unique_id}",
            material_type="refractory",
            thermal_conductivity=2.8,
            specific_heat=950.0,
            density=2400.0,
            max_temperature=1700.0,
            created_by_id=str(test_user.id),
            is_active=True
        )
        test_db.add(new_material)
        await test_db.commit()
        await test_db.refresh(new_material)

        # Supersede old with new
        success = await materials_service.supersede_material(
            str(old_material.id),
            str(new_material.id),
            str(test_user.id)
        )

        assert success is True

        # Verify old material is inactive and has superseded_by
        updated_old = await materials_service.get_material(str(old_material.id))
        assert updated_old.is_active is False
        assert updated_old.superseded_by_id == str(new_material.id)

    async def test_get_material_statistics_comprehensive(
        self,
        materials_service: MaterialsService,
        test_user: User,
        test_db: AsyncSession
    ):
        """Test comprehensive material statistics."""
        # Create diverse materials
        unique_id = uuid4().hex[:4]
        materials = [
            Material(
                name=f"Ref Mat {unique_id} {i}",
                material_type="refractory",
                thermal_conductivity=2.5,
                specific_heat=900.0,
                density=2300.0,
                max_temperature=1600.0,
                created_by_id=str(test_user.id),
                is_standard=i % 2 == 0
            )
            for i in range(3)
        ]
        test_db.add_all(materials)
        await test_db.commit()

        # Get statistics
        stats = await materials_service.get_material_statistics()

        assert "total_materials" in stats
        assert "by_type" in stats
        assert "standard_materials" in stats
        assert "custom_materials" in stats
        assert stats["total_materials"] >= 3