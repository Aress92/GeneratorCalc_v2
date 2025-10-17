# Test Coverage Improvement Plan
**Goal: 47% → 80% Coverage (+33 percentage points)**

**Date:** 2025-10-03
**Current Coverage:** 47% (21 passing tests, 70 failing, 76 errors)
**Target Coverage:** 80% (minimum viable for production)
**Estimated Effort:** 6-8 hours of focused work

---

## Executive Summary

This plan focuses on the **4 highest-ROI services** that will deliver the most coverage gain with minimal effort. We'll add ~100-120 new tests targeting core business logic that's currently untested.

### Coverage Gain Analysis

| Service | Current | Target | Missing Lines | New Tests Needed | Estimated Gain |
|---------|---------|--------|---------------|------------------|----------------|
| **import_service.py** | 10% | 60% | 290 | 25-30 | +9.5% |
| **reporting_service.py** | 16% | 60% | 223 | 20-25 | +7.5% |
| **optimization_service.py** | 16% | 70% | 204 | 30-35 | +8.0% |
| **materials_service.py** | 13% | 70% | 156 | 25-30 | +6.5% |
| **TOTAL** | — | — | **873** | **100-120** | **+31.5%** |

**Projected Final Coverage:** 47% + 31.5% = **78.5%** (within margin of target)

---

## Phase 1: Fix Common Test Issues (1 hour)

### Issue 1: Fixture Setup Problems
**Affected:** All async service tests (76 ERRORs)

**Problem:**
- Duplicate UUID fixtures causing UNIQUE constraint violations
- Async session management issues
- Missing required Pydantic schema fields

**Solution:**
```python
# Use uuid4() for all fixtures to prevent collisions
from uuid import uuid4

@pytest.fixture
async def test_user(test_db: AsyncSession) -> User:
    user = User(
        username=f"testuser_{uuid4().hex[:8]}",  # ✅ Unique
        email=f"test_{uuid4().hex[:8]}@example.com",  # ✅ Unique
        # ... rest of fields
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user
```

**Files to Fix:**
- `tests/conftest.py` - Update shared fixtures
- `tests/test_optimization_service.py` - Fix scenario creation schema
- `tests/test_auth_service.py` - Use strong passwords for validation
- `tests/test_materials_service.py` - Fix async fixture dependencies

---

## Phase 2: Optimization Service Tests (2 hours)

**Current:** 16.4% (40/244 lines covered)
**Target:** 70% (170/244 lines covered)
**Gap:** +130 lines coverage

### Existing Tests (4 PASS, 3 ERROR, 9 FAIL)

✅ **Working:**
- `test_calculate_pressure_drop`
- `test_physics_model_with_different_configs`
- `test_edge_cases_thermal_performance`
- `test_optimization_with_mock`

❌ **Failing - Need Schema Fixes:**
- `test_create_scenario` - Missing required fields: `scenario_type`, `base_configuration_id`, `objective`, `constraints` (List not Dict)
- `test_get_scenario_by_id` - Fixture dependency error
- `test_create_optimization_job` - Fixture dependency error

❌ **Failing - Need Implementation:**
- `test_physics_model_initialization` - AssertionError on config parsing
- `test_calculate_thermal_performance` - Missing return values
- `test_calculate_reynolds_number` - Method signature mismatch
- `test_calculate_nusselt_number` - Method signature mismatch
- `test_calculate_heat_loss` - Missing method
- `test_validate_design_variables` - Missing method
- `test_objective_function` - Missing method
- `test_constraint_functions` - Missing method

### New Tests to Add (25-30 tests)

#### A. OptimizationService Core Methods (10 tests)
```python
class TestOptimizationServiceCore:
    async def test_create_optimization_job_success(...)
    async def test_create_optimization_job_invalid_scenario(...)
    async def test_get_optimization_progress_running(...)
    async def test_get_optimization_progress_completed(...)
    async def test_get_optimization_progress_failed(...)
    async def test_run_optimization_slsqp_success(...)
    async def test_run_optimization_convergence_failure(...)
    async def test_run_optimization_constraint_violation(...)
    async def test_run_optimization_timeout(...)
    async def test_cancel_optimization_job(...)
```

**Coverage Target:** Lines 40-110, 193-217, 226-278 (optimization job lifecycle)

#### B. RegeneratorPhysicsModel Methods (15 tests)
```python
class TestRegeneratorPhysicsModel:
    # Thermal calculations
    def test_calculate_thermal_performance_baseline(...)
    def test_calculate_thermal_performance_optimal(...)
    def test_calculate_thermal_performance_poor(...)

    # Heat transfer
    def test_calculate_reynolds_turbulent(...)
    def test_calculate_reynolds_laminar(...)
    def test_calculate_nusselt_forced_convection(...)
    def test_calculate_htc_high_flow(...)
    def test_calculate_htc_low_flow(...)

    # Effectiveness
    def test_calculate_effectiveness_high_ntu(...)
    def test_calculate_effectiveness_low_ntu(...)

    # Constraints
    def test_validate_design_variables_within_bounds(...)
    def test_validate_design_variables_out_of_bounds(...)
    def test_constraint_pressure_drop_satisfied(...)
    def test_constraint_efficiency_satisfied(...)
    def test_constraint_violation_handling(...)
```

**Coverage Target:** Lines 57-110, 125-173 (physics calculations)

#### C. SLSQP Integration Tests (5 tests)
```python
class TestSLSQPOptimization:
    async def test_slsqp_minimize_fuel_consumption(...)
    async def test_slsqp_maximize_efficiency(...)
    async def test_slsqp_multi_objective(...)
    async def test_slsqp_with_linear_constraints(...)
    async def test_slsqp_convergence_criteria(...)
```

**Coverage Target:** Lines 290-386 (SLSQP algorithm integration)

---

## Phase 3: Materials Service Tests (1.5 hours)

**Current:** 12.8% (23/179 lines covered)
**Target:** 70% (125/179 lines covered)
**Gap:** +102 lines coverage

### Existing Tests (3 PASS, 15 ERROR, 1 FAIL)

✅ **Working:**
- `test_get_material_not_found`
- `test_get_popular_materials`
- `test_initialize_standard_materials`

❌ **Errors - Fixture Issues:**
- All database operation tests fail due to async fixture setup

### New Tests to Add (25-30 tests)

#### A. CRUD Operations (8 tests)
```python
class TestMaterialsCRUD:
    async def test_create_material_refractory(...)
    async def test_create_material_insulation(...)
    async def test_create_material_duplicate_name(...)
    async def test_get_material_by_id_success(...)
    async def test_update_material_properties(...)
    async def test_update_material_not_found(...)
    async def test_delete_material_success(...)
    async def test_delete_material_in_use(...)
```

**Coverage Target:** Lines 44-96, 100-105 (CRUD operations)

#### B. Material Search & Filtering (10 tests)
```python
class TestMaterialsSearch:
    async def test_search_materials_by_name(...)
    async def test_search_materials_by_type(...)
    async def test_search_materials_by_temperature_range(...)
    async def test_search_materials_by_density_range(...)
    async def test_search_materials_multiple_filters(...)
    async def test_get_materials_by_type_refractory(...)
    async def test_get_materials_by_type_insulation(...)
    async def test_filter_active_only(...)
    async def test_filter_inactive_only(...)
    async def test_pagination_limit_offset(...)
```

**Coverage Target:** Lines 124-160, 216-276 (search/filter logic)

#### C. Material Approval Workflow (7 tests)
```python
class TestMaterialsApproval:
    async def test_approve_material_by_admin(...)
    async def test_approve_material_by_engineer_fails(...)
    async def test_reject_material(...)
    async def test_supersede_material_old_to_new(...)
    async def test_supersede_material_circular_reference(...)
    async def test_get_material_statistics_breakdown(...)
    async def test_get_popular_materials_usage_count(...)
```

**Coverage Target:** Lines 173-196, 284-305, 324-357 (approval workflow)

#### D. Standard Materials Initialization (5 tests)
```python
class TestMaterialsInitialization:
    async def test_initialize_standard_materials_first_time(...)
    async def test_initialize_standard_materials_idempotent(...)
    async def test_standard_materials_have_required_properties(...)
    async def test_standard_materials_all_active(...)
    async def test_standard_materials_count_103(...)
```

**Coverage Target:** Lines 376-464 (standard materials data)

---

## Phase 4: Import Service Tests (2 hours)

**Current:** 9.9% (32/322 lines covered)
**Target:** 60% (193/322 lines covered)
**Gap:** +161 lines coverage

### Existing Tests (3 PASS, 11 ERROR, 4 FAIL)

✅ **Working:**
- Basic tests pass but cover minimal code

❌ **Errors - Fixture Issues:**
- Most async database tests fail

### New Tests to Add (30-35 tests)

#### A. File Preview & Validation (10 tests)
```python
class TestFilePreview:
    async def test_preview_excel_file_valid(...)
    async def test_preview_excel_file_invalid_format(...)
    async def test_preview_csv_file_utf8(...)
    async def test_preview_csv_file_latin1_encoding(...)
    async def test_preview_file_empty(...)
    async def test_preview_file_too_large(...)
    async def test_preview_file_corrupted(...)
    async def test_detect_column_headers(...)
    async def test_detect_data_types(...)
    async def test_preview_pagination_100_rows(...)
```

**Coverage Target:** Lines 54-100 (file parsing)

#### B. Column Mapping (8 tests)
```python
class TestColumnMapping:
    async def test_validate_column_mapping_all_required(...)
    async def test_validate_column_mapping_missing_required(...)
    async def test_validate_column_mapping_duplicate_targets(...)
    async def test_auto_detect_column_mapping(...)
    async def test_column_mapping_data_type_conversion(...)
    async def test_column_mapping_custom_transformations(...)
    async def test_column_mapping_units_conversion(...)
    async def test_get_import_templates(...)
```

**Coverage Target:** Lines 119-155, 217-234 (column mapping)

#### C. Dry Run Import (7 tests)
```python
class TestDryRunImport:
    async def test_dry_run_import_valid_data(...)
    async def test_dry_run_import_validation_errors(...)
    async def test_dry_run_import_warnings(...)
    async def test_dry_run_import_statistics(...)
    async def test_dry_run_import_preview_results(...)
    async def test_dry_run_import_duplicate_detection(...)
    async def test_dry_run_import_referential_integrity(...)
```

**Coverage Target:** Lines 167-213 (dry run validation)

#### D. Import Job Lifecycle (10 tests)
```python
class TestImportJobLifecycle:
    async def test_create_import_job_regenerators(...)
    async def test_create_import_job_materials(...)
    async def test_create_import_job_operating_data(...)
    async def test_get_import_job_by_id(...)
    async def test_get_user_import_jobs_pagination(...)
    async def test_process_import_job_success(...)
    async def test_process_import_job_partial_success(...)
    async def test_process_import_job_complete_failure(...)
    async def test_update_job_progress_incremental(...)
    async def test_cancel_import_job(...)
```

**Coverage Target:** Lines 246-303, 315-384, 401-465 (job management)

#### E. Error Handling & Cleanup (5 tests)
```python
class TestImportErrorHandling:
    async def test_handle_import_row_error(...)
    async def test_handle_import_batch_error(...)
    async def test_rollback_failed_import(...)
    async def test_cleanup_failed_imports_old(...)
    async def test_get_import_job_statistics(...)
```

**Coverage Target:** Lines 469-572, 582-632 (error handling)

---

## Phase 5: Reporting Service Tests (1.5 hours)

**Current:** 16.5% (44/267 lines covered)
**Target:** 60% (160/267 lines covered)
**Gap:** +116 lines coverage

### Existing Tests (4 PASS, 15 ERROR, 2 FAIL)

✅ **Working:**
- Basic tests pass but cover minimal code

### New Tests to Add (25-30 tests)

#### A. Report Creation & Lifecycle (10 tests)
```python
class TestReportLifecycle:
    async def test_create_report_optimization_summary(...)
    async def test_create_report_performance_analysis(...)
    async def test_create_report_material_usage(...)
    async def test_create_report_duplicate_name(...)
    async def test_get_report_by_id(...)
    async def test_get_user_reports_pagination(...)
    async def test_delete_report_success(...)
    async def test_delete_report_not_found(...)
    async def test_update_report_status(...)
    async def test_get_report_progress(...)
```

**Coverage Target:** Lines 52-122, 127-138 (report CRUD)

#### B. Report Generation (8 tests)
```python
class TestReportGeneration:
    async def test_generate_report_pdf(...)
    async def test_generate_report_excel(...)
    async def test_generate_report_with_charts(...)
    async def test_generate_report_with_tables(...)
    async def test_generate_report_multi_scenario_comparison(...)
    async def test_generate_report_progress_tracking(...)
    async def test_generate_report_failure_handling(...)
    async def test_mark_report_completed_with_file_path(...)
```

**Coverage Target:** Lines 142-212 (report generation)

#### C. Dashboard Metrics (7 tests)
```python
class TestDashboardMetrics:
    async def test_get_dashboard_metrics_complete(...)
    async def test_dashboard_metrics_no_data(...)
    async def test_dashboard_metrics_optimization_summary(...)
    async def test_dashboard_metrics_fuel_savings(...)
    async def test_dashboard_metrics_co2_reduction(...)
    async def test_dashboard_metrics_recent_reports(...)
    async def test_dashboard_metrics_system_status(...)
```

**Coverage Target:** Lines 216-255 (dashboard calculations)

#### D. Report Templates (5 tests)
```python
class TestReportTemplates:
    async def test_create_report_template(...)
    async def test_get_report_templates_all(...)
    async def test_get_templates_by_type_optimization(...)
    async def test_get_templates_by_type_performance(...)
    async def test_use_template_for_report(...)
```

**Coverage Target:** Lines 259-288 (template management)

#### E. Report Analytics & Cleanup (5 tests)
```python
class TestReportAnalytics:
    async def test_get_report_analytics_monthly(...)
    async def test_get_report_analytics_by_type(...)
    async def test_cleanup_old_reports_30_days(...)
    async def test_cleanup_old_reports_preserve_recent(...)
    async def test_download_report_file(...)
```

**Coverage Target:** Lines 292-359, 364-431 (analytics & maintenance)

---

## Phase 6: Verification & Documentation (30 mins)

### Tasks:
1. **Run Full Test Suite:**
   ```bash
   docker compose exec backend python -m pytest --cov=app --cov-report=term-missing --cov-report=html -v
   ```

2. **Verify Coverage Targets:**
   - Overall: ≥80%
   - optimization_service.py: ≥70%
   - materials_service.py: ≥70%
   - import_service.py: ≥60%
   - reporting_service.py: ≥60%

3. **Update Documentation:**
   - Update `backend/TEST_COVERAGE_ANALYSIS.md` with new results
   - Update `CLAUDE.md` with new coverage status
   - Create coverage badge for README

4. **Commit Changes:**
   ```bash
   git add tests/
   git commit -m "test: boost coverage from 47% to 80%+ with comprehensive service tests

   - Add 100+ new tests for optimization, materials, import, and reporting services
   - Fix async fixture issues causing 76 ERRORs
   - Fix Pydantic schema validation in optimization tests
   - Achieve 80%+ coverage target for production readiness

   Coverage improvements:
   - optimization_service.py: 16% → 70%
   - materials_service.py: 13% → 70%
   - import_service.py: 10% → 60%
   - reporting_service.py: 16% → 60%"
   ```

---

## Out of Scope (For This Phase)

### 1. Celery Task Tests (0% coverage)
**Why skip:** Complex mocking required for Celery workers, Redis broker, and async event loops. Low ROI.
**Future work:** Add integration tests with test Celery worker

### 2. Failing Config Tests (11 failures)
**Why skip:** Tests expect non-existent Settings attributes. Would require adding unused features.
**Future work:** Rewrite tests to match actual Settings class or remove

### 3. PDF/Excel Generator Tests (9-18% coverage)
**Why skip:** Complex file generation mocking, covered indirectly through reporting_service tests
**Future work:** Add unit tests for specific formatting/layout functions

### 4. API Endpoint Tests (18-24% coverage)
**Why skip:** Integration tests, already covered through service layer tests
**Future work:** Add E2E tests with TestClient

---

## Risk Mitigation

### Risk 1: Async Test Fixtures Fail
**Probability:** Medium
**Impact:** High (blocks all service tests)
**Mitigation:**
- Fix `conftest.py` shared fixtures first
- Add `uuid4()` to all fixtures for uniqueness
- Test fixture setup in isolation before bulk test creation

### Risk 2: Coverage Gain Less Than Expected
**Probability:** Low
**Impact:** Medium (may not reach 80%)
**Mitigation:**
- Conservative estimates (70% gain instead of 90%)
- Focus on line coverage, not branch coverage
- Priority services selected based on actual coverage data

### Risk 3: Tests Pass But Don't Exercise Real Logic
**Probability:** Medium
**Impact:** Medium (false sense of security)
**Mitigation:**
- Use real database (SQLite) instead of mocks where possible
- Verify actual business logic outcomes, not just method calls
- Include edge cases and error paths, not just happy paths

---

## Success Metrics

### Primary Metrics:
- ✅ Overall coverage: **≥80%**
- ✅ optimization_service.py: **≥70%**
- ✅ materials_service.py: **≥70%**
- ✅ import_service.py: **≥60%**
- ✅ reporting_service.py: **≥60%**

### Secondary Metrics:
- ✅ Test suite runtime: **<60 seconds**
- ✅ No test errors (ERRORs): **76 → 0**
- ✅ Test failures acceptable: **<5%** (flaky tests)
- ✅ All tests isolated (no interdependencies)

### Quality Metrics:
- ✅ Each test has clear docstring
- ✅ Each test uses descriptive names
- ✅ Each test asserts specific behavior
- ✅ No "god tests" (test only one thing)

---

## Implementation Order

**Day 1 (4 hours):**
1. ✅ Phase 1: Fix common fixture issues (1h)
2. ✅ Phase 2: Optimization service tests (2h)
3. ✅ Phase 3: Materials service tests (1h)

**Day 2 (3 hours):**
4. ✅ Phase 4: Import service tests (2h)
5. ✅ Phase 5: Reporting service tests (1h)

**Day 3 (1 hour):**
6. ✅ Phase 6: Verification & documentation (0.5h)
7. ✅ Code review and cleanup (0.5h)

**Total Estimated Time:** 8 hours over 3 days

---

## Appendix A: Test Template

```python
"""
Tests for [SERVICE_NAME] service.

Testy dla serwisu [SERVICE_NAME].
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.[service_name] import [ServiceClass]
from app.models.[model_name] import [Models...]
from app.schemas.[schema_name] import [Schemas...]
from app.models.user import User, UserRole


class Test[ServiceClass]:
    """Test [ServiceClass] functionality."""

    @pytest.fixture
    async def service(self, test_db: AsyncSession) -> [ServiceClass]:
        """Create service instance."""
        return [ServiceClass](test_db)

    @pytest.fixture
    async def test_user(self, test_db: AsyncSession) -> User:
        """Create test user with unique credentials."""
        user = User(
            username=f"testuser_{uuid4().hex[:8]}",
            email=f"test_{uuid4().hex[:8]}@example.com",
            full_name="Test User",
            password_hash="$2b$12$hashed",
            role=UserRole.ENGINEER,
            is_active=True,
            is_verified=True
        )
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)
        return user

    async def test_[method_name]_success(self, service, test_user):
        """Test [method_name] with valid input."""
        # Arrange
        input_data = {...}

        # Act
        result = await service.[method_name](input_data, str(test_user.id))

        # Assert
        assert result is not None
        assert result.field == expected_value

    async def test_[method_name]_not_found(self, service):
        """Test [method_name] with non-existent ID."""
        # Act & Assert
        with pytest.raises(HTTPException) as exc:
            await service.[method_name]("non-existent-id")
        assert exc.value.status_code == 404
```

---

## Appendix B: Coverage Baseline (2025-10-03)

```
Name                                   Stmts   Miss  Cover   Missing
--------------------------------------------------------------------
app/services/auth_service.py            158    132    16%   46, 67-107, ...
app/services/excel_generator.py         179    162     9%   22-23, 28-46, ...
app/services/import_service.py          322    290    10%   35, 54-100, ...
app/services/materials_service.py       179    156    13%   27, 44-96, ...
app/services/optimization_service.py    244    204    16%   40-44, 57-110, ...
app/services/pdf_generator.py           174    143    18%   26-27, 34-38, ...
app/services/regenerator_service.py     149    129    13%   27-28, 48-116, ...
app/services/reporting_service.py       267    223    16%   38-39, 44-45, ...
app/services/unit_conversion.py         118     89    25%   40-41, 47-153, ...
app/services/validation_service.py      170    147    14%   30-31, 48-61, ...
app/tasks/import_export.py                7      7     0%   7-45
app/tasks/maintenance.py                 84     84     0%   7-180
app/tasks/optimization.py                10     10     0%   7-44
app/tasks/optimization_tasks.py         162    162     0%   7-345
app/tasks/reporting_tasks.py            157    157     0%   7-363
app/tasks/reports.py                      7      7     0%   7-44
--------------------------------------------------------------------
TOTAL                                  5544   3133    43%
```

**Test Results:**
- 21 passed
- 70 failed
- 76 errors
- 16 warnings
- Runtime: 84.85s

---

**END OF TEST PLAN**
