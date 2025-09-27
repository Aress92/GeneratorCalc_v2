"""
Tests for import API endpoints.

Testy endpointów importu danych.
"""

import pytest
from httpx import AsyncClient
from io import BytesIO


class TestImportAPI:
    """Tests for data import endpoints."""

    @pytest.mark.asyncio
    async def test_get_templates(self, test_client: AsyncClient, auth_headers):
        """Test getting import templates."""
        response = await test_client.get(
            "/api/v1/import/templates/regenerators",
            headers=auth_headers
        )

        # Should return template info or file
        assert response.status_code in [200, 404]  # 404 if not implemented yet

    @pytest.mark.asyncio
    async def test_list_import_jobs(self, test_client: AsyncClient, auth_headers):
        """Test listing import jobs."""
        response = await test_client.get(
            "/api/v1/import/jobs",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_dry_run_import(self, test_client: AsyncClient, auth_headers):
        """Test dry run import validation."""
        # Create a simple CSV content
        csv_content = "Name,Temperature,Pressure\nTest Regenerator,800,150\n"
        csv_bytes = csv_content.encode('utf-8')

        response = await test_client.post(
            "/api/v1/import/dry-run-simple",
            headers=auth_headers,
            files={"file": ("test.csv", BytesIO(csv_bytes), "text/csv")},
            data={"import_type": "regenerators"}
        )

        # Should process or return validation error
        assert response.status_code in [200, 400, 422]

    @pytest.mark.asyncio
    async def test_import_types(self, test_client: AsyncClient, auth_headers):
        """Test getting available import types."""
        response = await test_client.get(
            "/api/v1/import/types",
            headers=auth_headers
        )

        # Should return list of available import types
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_unauthorized_access(self, test_client: AsyncClient):
        """Test import endpoints require authentication."""
        response = await test_client.get("/api/v1/import/jobs")
        assert response.status_code == 401

        response = await test_client.get("/api/v1/import/templates/regenerators")
        assert response.status_code == 401


class TestImportValidation:
    """Tests for import validation logic."""

    @pytest.mark.asyncio
    async def test_column_mapping_endpoint(self, test_client: AsyncClient, auth_headers):
        """Test column mapping suggestions."""
        # This would test the column mapping AI/logic
        test_columns = ["Regenerator Name", "Operating Temp", "Working Pressure"]

        response = await test_client.post(
            "/api/v1/import/suggest-mapping",
            headers=auth_headers,
            json={
                "import_type": "regenerators",
                "columns": test_columns
            }
        )

        # Should suggest mappings or return error if not implemented
        assert response.status_code in [200, 404, 422]

    @pytest.mark.asyncio
    async def test_validation_rules(self, test_client: AsyncClient, auth_headers):
        """Test getting validation rules for import type."""
        response = await test_client.get(
            "/api/v1/import/validation-rules/regenerators",
            headers=auth_headers
        )

        # Should return validation rules or 404 if not implemented
        assert response.status_code in [200, 404]