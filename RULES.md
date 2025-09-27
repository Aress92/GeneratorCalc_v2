RULES.md
Spis treści
Metadane dokumentu

Wprowadzenie i cel

Standardy kodu i repozytorium

Architektura i wzorce projektowe

Polityka testowania

Bezpieczeństwo i compliance

CI/CD i deployment

Observability i monitoring

Definition of Done

Szablony i konwencje dokumentacji

Runbooki i procedury operacyjne

Zarządzanie zespołem i responsywności

Słownik pojęć

Changelog

Metadane dokumentu
Pole	Wartość
Tytuł	Engineering Rules - Forglass Regenerator Optimizer
Wersja	1.0.0
Data	2025-09-23
Status	Active - Mandatory compliance
Właściciel	Tech Lead / Engineering Manager
Zakres	Wszystkie zespoły engineering (Backend, Frontend, DevOps, QA)
Review cycle	Quarterly review, continuous updates
Wprowadzenie i cel
Niniejszy dokument definiuje mandatory engineering practices dla projektu Forglass Regenerator Optimizer. Wszystkie zespoły i deweloperzy MUSZĄ przestrzegać tych zasad w celu zapewnienia:

Jakości kodu na poziomie enterprise

Bezpieczeństwa danych i systemu

Maintainability i technical debt control

Współpracy i knowledge sharing

Operational excellence w produkcji

Violation Policy: Naruszenie tych zasad skutkuje mandatory rework przed merge'em do main branch.

Standardy kodu i repozytorium
Python Backend Standards
Wersje i dependencies:

python
# pyproject.toml - MANDATORY versions
[tool.poetry]
python = "^3.12"
fastapi = "^0.104.0"
sqlalchemy = "^2.0.0"
alembic = "^1.12.0"
pydantic = "^2.4.0"
celery = "^5.3.0"
redis = "^5.0.0"
Code formatting i linting (MANDATORY):

text
# pyproject.toml
[tool.ruff]
target-version = "py312"
line-length = 100
select = [
    "E",  # pycodestyle errors
    "W",  # pycodestyle warnings  
    "F",  # pyflakes
    "I",  # isort
    "N",  # pep8-naming
    "D",  # pydocstyle
    "UP", # pyupgrade
    "S",  # bandit security
]
ignore = ["D100", "D104"]  # Allow missing docstrings in __init__.py

[tool.ruff.pydocstyle]
convention = "google"

[tool.black]
line-length = 100
target-version = ['py312']

[tool.mypy]
python_version = "3.12"
strict = true
disallow_untyped_defs = true
disallow_any_generics = true
warn_redundant_casts = true
warn_unused_ignores = true
Type annotations (MANDATORY):

python
# ✅ CORRECT - Full type annotations
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

def optimize_regenerator(
    scenario_id: UUID,
    parameters: Dict[str, float],
    timeout_seconds: Optional[int] = None
) -> OptimizationResult:
    """Optimize regenerator configuration using SLSQP algorithm.
    
    Args:
        scenario_id: Unique identifier for optimization scenario
        parameters: Optimization parameters (bounds, constraints)
        timeout_seconds: Maximum execution time, defaults to 3600s
        
    Returns:
        OptimizationResult containing solution and convergence info
        
    Raises:
        OptimizationError: When algorithm fails to converge
        ValidationError: When parameters are invalid
    """
    # Implementation...

# ❌ INCORRECT - Missing type annotations
def optimize_regenerator(scenario_id, parameters, timeout_seconds=None):
    # Implementation...
Error handling patterns (MANDATORY):

python
# Custom exceptions hierarchy
class FROptimizationError(Exception):
    """Base exception for optimization errors."""
    
class ConvergenceError(FROptimizationError):
    """Algorithm failed to converge."""
    
class ValidationError(FROptimizationError):
    """Input validation failed."""

# ✅ CORRECT - Structured error handling
async def import_xlsx_data(file_data: bytes) -> ImportResult:
    try:
        df = pd.read_excel(BytesIO(file_data))
        validated_data = validate_import_schema(df)
        return ImportResult(success=True, data=validated_data)
    except pd.errors.EmptyDataError:
        logger.error("Empty XLSX file provided", extra={"file_size": len(file_data)})
        raise ValidationError("File contains no data")
    except ValidationError:
        # Re-raise validation errors as-is
        raise
    except Exception as e:
        logger.exception("Unexpected error during import")
        raise FROptimizationError(f"Import failed: {str(e)}") from e
TypeScript/React Frontend Standards
Versions and tooling (MANDATORY):

json
{
  "engines": {
    "node": ">=18.17.0",
    "pnpm": ">=8.0.0"
  },
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.2.0",
    "typescript": "^5.2.0",
    "@tailwindcss/forms": "^0.5.0"
  },
  "devDependencies": {
    "eslint": "^8.50.0",
    "@typescript-eslint/eslint-plugin": "^6.7.0",
    "prettier": "^3.0.0",
    "vitest": "^0.34.0"
  }
}
ESLint configuration (.eslintrc.json):

json
{
  "extends": [
    "next/core-web-vitals",
    "@typescript-eslint/recommended",
    "@typescript-eslint/recommended-requiring-type-checking"
  ],
  "parser": "@typescript-eslint/parser",
  "parserOptions": {
    "project": "./tsconfig.json"
  },
  "rules": {
    "@typescript-eslint/no-unused-vars": "error",
    "@typescript-eslint/no-explicit-any": "error",
    "@typescript-eslint/prefer-const": "error",
    "react-hooks/exhaustive-deps": "error",
    "prefer-const": "error",
    "no-var": "error"
  }
}
Component conventions (MANDATORY):

tsx
// ✅ CORRECT - Proper component structure
import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { OptimizationResult } from '@/types/optimization';

interface OptimizationResultsProps {
  scenarioId: string;
  results?: OptimizationResult;
  isLoading?: boolean;
  onExportPdf?: () => void;
}

export function OptimizationResults({ 
  scenarioId, 
  results, 
  isLoading = false,
  onExportPdf 
}: OptimizationResultsProps) {
  const [expandedSection, setExpandedSection] = useState<string | null>(null);

  // ✅ Proper error handling
  if (!results && !isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>No Results Available</CardTitle>
        </CardHeader>
      </Card>
    );
  }

  return (
    <Card data-testid="optimization-results">
      <CardHeader>
        <CardTitle>Optimization Results - {scenarioId}</CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="flex items-center justify-center p-8">
            <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full" />
          </div>
        ) : (
          <div className="space-y-4">
            {/* Results content */}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// ❌ INCORRECT - Missing types, props destructuring
export function OptimizationResults(props: any) {
  return <div>{props.results}</div>;
}
Git Workflow i Commit Standards
Branch naming (MANDATORY):

bash
# Feature branches
feature/FRO-123-import-xlsx-validation
feature/FRO-124-optimization-wizard

# Bugfix branches  
bugfix/FRO-125-fix-memory-leak-celery
bugfix/FRO-126-cors-headers-missing

# Hotfix branches (production)
hotfix/FRO-127-critical-security-patch

# Release branches
release/1.2.0
Conventional Commits (MANDATORY):

bash
# ✅ CORRECT format
feat(api): add XLSX import validation with schema checking

Add comprehensive validation for XLSX imports including:
- Schema validation against predefined templates
- Data type checking and conversion
- Constraint validation for physical properties
- Progress tracking for large files

Closes: FRO-123
Breaking-change: Import API now returns validation errors array

# ✅ Other examples
fix(frontend): resolve memory leak in optimization progress tracking
docs(readme): update deployment instructions for Docker Compose
chore(deps): upgrade FastAPI to 0.104.0 for security fixes
test(api): add integration tests for optimization endpoints
refactor(auth): simplify JWT token validation logic

# ❌ INCORRECT - Vague, no scope
fix: bug fix
add new feature
update code
Pull Request Requirements (MANDATORY):

Size limit: ≤400 LOC per PR (excluding generated code, migrations)

Title: Must follow conventional commits format

Description: Template with checklist completed

Tests: New functionality must have tests

Reviews: Minimum 2 approvals for main branch

CI: All checks must pass (lint, test, security scan)

PR Template (.github/pull_request_template.md):

text
## Summary
Brief description of changes and motivation.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)  
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed
- [ ] Performance impact assessed

## Checklist
- [ ] Code follows style guidelines (ruff, eslint passed)
- [ ] Self-review of code completed
- [ ] Code is commented, particularly in hard-to-understand areas
- [ ] Corresponding changes to documentation made
- [ ] No new warnings or errors introduced
- [ ] Tests pass locally
- [ ] Security implications considered

## Screenshots (if applicable)
Add screenshots for UI changes.

## Related Issues
Closes #123
Code Review Standards
Review Checklist (MANDATORY for reviewers):

 Functionality: Code does what it's supposed to do

 Readability: Code is self-documenting, well-named variables/functions

 Performance: No obvious performance issues, efficient algorithms

 Security: No security vulnerabilities, input validation present

 Error Handling: Proper exception handling, graceful degradation

 Testing: Adequate test coverage, edge cases considered

 Documentation: API docs updated, complex logic explained

 Consistency: Follows established patterns and conventions

Review Response SLA:

Critical fixes: 4 hours

Normal features: 24 hours

Documentation: 48 hours

Architektura i wzorce projektowe
Backend Architecture Patterns
Dependency Injection (MANDATORY):

python
# services/optimization_service.py
from abc import ABC, abstractmethod
from typing import Protocol

class OptimizationRepository(Protocol):
    async def save_result(self, result: OptimizationResult) -> UUID:
        ...
    async def get_by_id(self, id: UUID) -> OptimizationResult:
        ...

class NotificationService(Protocol):
    async def send_completion_notification(self, user_id: UUID, result: OptimizationResult) -> None:
        ...

class OptimizationService:
    def __init__(
        self, 
        repository: OptimizationRepository,
        notification: NotificationService,
        physics_engine: PhysicsEngine
    ):
        self.repository = repository
        self.notification = notification  
        self.physics_engine = physics_engine
    
    async def run_optimization(self, scenario: OptimizationScenario) -> OptimizationResult:
        # Business logic here
        result = await self.physics_engine.optimize(scenario)
        await self.repository.save_result(result)
        await self.notification.send_completion_notification(scenario.user_id, result)
        return result

# di/container.py - Dependency injection container
def create_optimization_service() -> OptimizationService:
    return OptimizationService(
        repository=SQLOptimizationRepository(get_db_session()),
        notification=EmailNotificationService(get_smtp_config()),
        physics_engine=SLSQPPhysicsEngine()
    )
Repository Pattern (MANDATORY):

python
# repositories/base.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List
from uuid import UUID

T = TypeVar('T')

class BaseRepository(Generic[T], ABC):
    @abstractmethod
    async def create(self, entity: T) -> T:
        pass
    
    @abstractmethod  
    async def get_by_id(self, id: UUID) -> Optional[T]:
        pass
    
    @abstractmethod
    async def update(self, id: UUID, entity: T) -> T:
        pass
    
    @abstractmethod
    async def delete(self, id: UUID) -> bool:
        pass
    
    @abstractmethod
    async def list(self, offset: int = 0, limit: int = 100) -> List[T]:
        pass

# repositories/scenario_repository.py
class ScenarioRepository(BaseRepository[OptimizationScenario]):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, scenario: OptimizationScenario) -> OptimizationScenario:
        db_scenario = ScenarioORM(**scenario.model_dump())
        self.session.add(db_scenario)
        await self.session.commit()
        await self.session.refresh(db_scenario)
        return OptimizationScenario.from_orm(db_scenario)
    
    async def get_by_user_id(self, user_id: UUID) -> List[OptimizationScenario]:
        stmt = select(ScenarioORM).where(ScenarioORM.user_id == user_id)
        result = await self.session.execute(stmt)
        return [OptimizationScenario.from_orm(row) for row in result.scalars()]
API Layer Patterns (MANDATORY):

python
# api/v1/scenarios.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from typing import List

router = APIRouter(prefix="/scenarios", tags=["scenarios"])
security = HTTPBearer()

@router.post("/", response_model=OptimizationScenarioResponse, status_code=status.HTTP_201_CREATED)
async def create_scenario(
    request: CreateOptimizationScenarioRequest,
    current_user: User = Depends(get_current_user),
    service: OptimizationService = Depends(get_optimization_service)
) -> OptimizationScenarioResponse:
    """Create new optimization scenario.
    
    Requires ENGINEER or ADMIN role.
    """
    if current_user.role not in [UserRole.ENGINEER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    try:
        scenario = await service.create_scenario(
            user_id=current_user.id,
            **request.model_dump()
        )
        return OptimizationScenarioResponse.from_domain(scenario)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.exception("Failed to create scenario", extra={
            "user_id": str(current_user.id),
            "request": request.model_dump()
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/{scenario_id}", response_model=OptimizationScenarioResponse)
async def get_scenario(
    scenario_id: UUID,
    current_user: User = Depends(get_current_user),
    service: OptimizationService = Depends(get_optimization_service)
) -> OptimizationScenarioResponse:
    scenario = await service.get_scenario_by_id(scenario_id)
    if not scenario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    # Check ownership or admin privileges
    if scenario.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    return OptimizationScenarioResponse.from_domain(scenario)
Frontend Architecture Patterns
Custom Hooks Pattern (MANDATORY):

tsx
// hooks/useOptimization.ts
import { useState, useCallback } from 'react';
import { useToast } from '@/hooks/use-toast';
import type { OptimizationScenario, OptimizationResult } from '@/types/optimization';

interface UseOptimizationReturn {
  isRunning: boolean;
  progress: OptimizationProgress | null;
  result: OptimizationResult | null;
  error: string | null;
  startOptimization: (scenarioId: string) => Promise<void>;
  pauseOptimization: () => Promise<void>;
  cancelOptimization: () => Promise<void>;
}

export function useOptimization(): UseOptimizationReturn {
  const [isRunning, setIsRunning] = useState(false);
  const [progress, setProgress] = useState<OptimizationProgress | null>(null);
  const [result, setResult] = useState<OptimizationResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [eventSource, setEventSource] = useState<EventSource | null>(null);
  const { toast } = useToast();

  const startOptimization = useCallback(async (scenarioId: string) => {
    try {
      setIsRunning(true);
      setError(null);
      
      // Start optimization job
      const response = await fetch('/api/v1/optimize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenario_id: scenarioId })
      });
      
      if (!response.ok) throw new Error('Failed to start optimization');
      
      const { job_id } = await response.json();
      
      // Setup SSE connection for progress
      const es = new EventSource(`/api/v1/jobs/${job_id}/events`);
      setEventSource(es);
      
      es.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        switch (data.type) {
          case 'optimization.progress':
            setProgress(data.data);
            break;
          case 'optimization.completed':
            setResult(data.data);
            setIsRunning(false);
            es.close();
            toast({
              title: 'Optimization Complete',
              description: `Completed in ${data.data.execution_time}s`
            });
            break;
          case 'optimization.error':
            setError(data.data.message);
            setIsRunning(false);
            es.close();
            break;
        }
      };
      
      es.onerror = () => {
        setError('Connection to server lost');
        setIsRunning(false);
        es.close();
      };
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      setIsRunning(false);
    }
  }, [toast]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (eventSource) {
        eventSource.close();
      }
    };
  }, [eventSource]);

  return {
    isRunning,
    progress,
    result,
    error,
    startOptimization,
    pauseOptimization,
    cancelOptimization
  };
}
State Management (MANDATORY - Zustand):

tsx
// stores/userStore.ts
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

interface User {
  id: string;
  username: string;
  email: string;
  role: 'ADMIN' | 'ENGINEER' | 'VIEWER';
}

interface UserState {
  user: User | null;
  isLoading: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
}

export const useUserStore = create<UserState>()(
  devtools(
    persist(
      (set, get) => ({
        user: null,
        isLoading: false,
        
        login: async (credentials) => {
          set({ isLoading: true });
          try {
            const response = await fetch('/api/v1/auth/login', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(credentials)
            });
            
            if (!response.ok) throw new Error('Login failed');
            
            const user = await response.json();
            set({ user, isLoading: false });
          } catch (error) {
            set({ isLoading: false });
            throw error;
          }
        },
        
        logout: async () => {
          await fetch('/api/v1/auth/logout', { method: 'POST' });
          set({ user: null });
        },
        
        checkAuth: async () => {
          try {
            const response = await fetch('/api/v1/auth/me');
            if (response.ok) {
              const user = await response.json();
              set({ user });
            }
          } catch (error) {
            set({ user: null });
          }
        }
      }),
      {
        name: 'user-storage',
        partialize: (state) => ({ user: state.user })
      }
    )
  )
);
Database Patterns
Migration Standards (MANDATORY):

python
# alembic/versions/001_create_scenarios_table.py
"""Create scenarios table

Revision ID: 001_create_scenarios
Revises: 
Create Date: 2025-09-23 17:48:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision = '001_create_scenarios'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create table with proper constraints and indexes
    op.create_table('scenarios',
        sa.Column('id', sa.String(36), primary_key=True, nullable=False),
        sa.Column('name', sa.String(200), nullable=False, index=True),
        sa.Column('regenerator_id', sa.String(36), nullable=False, index=True),
        sa.Column('user_id', sa.String(36), nullable=False, index=True),
        sa.Column('status', sa.Enum('DRAFT', 'RUNNING', 'COMPLETED', 'FAILED', name='scenario_status'), 
                  nullable=False, default='DRAFT'),
        sa.Column('input_parameters', sa.JSON, nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), 
                  onupdate=sa.func.now()),
        sa.Column('started_at', sa.DateTime, nullable=True),
        sa.Column('completed_at', sa.DateTime, nullable=True),
        
        # Foreign key constraints
        sa.ForeignKeyConstraint(['regenerator_id'], ['regenerators.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        
        # Composite indexes for common queries
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4'
    )
    
    # Create indexes for performance
    op.create_index('idx_scenarios_user_status', 'scenarios', ['user_id', 'status'])
    op.create_index('idx_scenarios_created_at', 'scenarios', ['created_at'])

def downgrade() -> None:
    op.drop_table('scenarios')
Polityka testowania
Test Coverage Requirements (MANDATORY)
Komponenta	Coverage Target	Test Types	Tools
Backend API	≥80% line coverage	Unit, Integration, Contract	pytest, pytest-cov
Frontend Components	≥70% line coverage	Unit, Integration	Vitest, React Testing Library
E2E Critical Paths	100% happy paths	End-to-end	Playwright
Performance	Key endpoints	Load, stress	Locust, k6
Security	Critical vulnerabilities	SAST, DAST	Bandit, OWASP ZAP
Testing Pyramid Structure
Unit Tests (60% of total tests):

python
# tests/unit/test_optimization_service.py
import pytest
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

from services.optimization_service import OptimizationService
from models.optimization import OptimizationScenario, OptimizationResult

class TestOptimizationService:
    @pytest.fixture
    def mock_repository(self):
        return AsyncMock()
    
    @pytest.fixture  
    def mock_notification(self):
        return AsyncMock()
    
    @pytest.fixture
    def mock_physics_engine(self):
        mock = Mock()
        mock.optimize = AsyncMock()
        return mock
    
    @pytest.fixture
    def service(self, mock_repository, mock_notification, mock_physics_engine):
        return OptimizationService(
            repository=mock_repository,
            notification=mock_notification,
            physics_engine=mock_physics_engine
        )
    
    @pytest.mark.asyncio
    async def test_run_optimization_success(self, service, mock_physics_engine, mock_repository):
        # Arrange
        scenario = OptimizationScenario(
            id=uuid4(),
            name="Test Scenario",
            user_id=uuid4(),
            input_parameters={"max_temp": 1200}
        )
        expected_result = OptimizationResult(
            id=uuid4(),
            scenario_id=scenario.id,
            objective_value=1234.56,
            convergence_status="SUCCESS"
        )
        mock_physics_engine.optimize.return_value = expected_result
        
        # Act
        result = await service.run_optimization(scenario)
        
        # Assert
        assert result == expected_result
        mock_physics_engine.optimize.assert_called_once_with(scenario)
        mock_repository.save_result.assert_called_once_with(expected_result)
    
    @pytest.mark.asyncio
    async def test_run_optimization_physics_engine_failure(self, service, mock_physics_engine):
        # Arrange
        scenario = OptimizationScenario(id=uuid4(), name="Test")
        mock_physics_engine.optimize.side_effect = ConvergenceError("Failed to converge")
        
        # Act & Assert
        with pytest.raises(ConvergenceError):
            await service.run_optimization(scenario)
Integration Tests (30% of total tests):

python
# tests/integration/test_scenario_api.py
import pytest
from httpx import AsyncClient
from fastapi import status

@pytest.mark.integration
class TestScenarioAPI:
    @pytest.mark.asyncio
    async def test_create_scenario_full_workflow(self, client: AsyncClient, engineer_user):
        # Create regenerator first
        regenerator_data = {
            "name": "Test Regenerator",
            "configuration": {"type": "crown", "chambers": 2}
        }
        regen_response = await client.post(
            "/api/v1/regenerators", 
            json=regenerator_data,
            headers={"Authorization": f"Bearer {engineer_user.token}"}
        )
        assert regen_response.status_code == status.HTTP_201_CREATED
        regenerator_id = regen_response.json()["id"]
        
        # Create scenario
        scenario_data = {
            "name": "Integration Test Scenario",
            "regenerator_id": regenerator_id,
            "input_parameters": {
                "target_efficiency": 0.85,
                "max_temperature": 1200,
                "fuel_type": "natural_gas"
            }
        }
        
        response = await client.post(
            "/api/v1/scenarios",
            json=scenario_data,
            headers={"Authorization": f"Bearer {engineer_user.token}"}
        )
        
        # Verify response
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == scenario_data["name"]
        assert data["status"] == "DRAFT"
        assert data["user_id"] == str(engineer_user.id)
        
        # Verify scenario exists in database
        scenario_id = data["id"]
        get_response = await client.get(
            f"/api/v1/scenarios/{scenario_id}",
            headers={"Authorization": f"Bearer {engineer_user.token}"}
        )
        assert get_response.status_code == status.HTTP_200_OK
End-to-End Tests (10% of total tests):

typescript
// tests/e2e/optimization-workflow.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Optimization Workflow', () => {
  test('complete optimization workflow from import to report', async ({ page }) => {
    // Login as engineer
    await page.goto('/login');
    await page.fill('[data-testid=username-input]', 'engineer@company.com');
    await page.fill('[data-testid=password-input]', 'password123');
    await page.click('[data-testid=login-button]');
    
    await expect(page).toHaveURL('/dashboard');
    
    // Import XLSX data
    await page.click('[data-testid=import-data-button]');
    await page.setInputFiles(
      '[data-testid=file-upload]', 
      'tests/fixtures/regenerator-data.xlsx'
    );
    await page.click('[data-testid=upload-button]');
    
    // Wait for import validation
    await expect(page.locator('[data-testid=import-success]')).toBeVisible();
    
    // Create new scenario
    await page.click('[data-testid=new-scenario-button]');
    await page.fill('[data-testid=scenario-name]', 'E2E Test Scenario');
    
    // Go through wizard steps
    await page.selectOption('[data-testid=regenerator-select]', 'Test Regenerator');
    await page.click('[data-testid=next-step]');
    
    await page.fill('[data-testid=target-efficiency]', '0.85');
    await page.fill('[data-testid=max-temperature]', '1200');
    await page.click('[data-testid=next-step]');
    
    // Review and start optimization
    await page.click('[data-testid=start-optimization]');
    
    // Wait for optimization to complete (with timeout)
    await expect(page.locator('[data-testid=optimization-complete]')).toBeVisible({
      timeout: 180000 // 3 minutes
    });
    
    // Verify results are displayed
    await expect(page.locator('[data-testid=fuel-savings]')).toBeVisible();
    await expect(page.locator('[data-testid=co2-reduction]')).toBeVisible();
    
    // Generate and download report
    await page.click('[data-testid=generate-report]');
    const downloadPromise = page.waitForDownload();
    await page.click('[data-testid=download-pdf]');
    const download = await downloadPromise;
    
    expect(download.suggestedFilename()).toMatch(/optimization-report.*\.pdf$/);
  });
});
Test Data Management
Fixtures and Factories (MANDATORY):

python
# tests/fixtures/factories.py
import factory
from datetime import datetime, timezone
from uuid import uuid4

from models.user import User, UserRole
from models.regenerator import Regenerator
from models.optimization import OptimizationScenario

class UserFactory(factory.Factory):
    class Meta:
        model = User
    
    id = factory.LazyFunction(uuid4)
    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    role = UserRole.ENGINEER
    is_active = True
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))

class RegeneratorFactory(factory.Factory):
    class Meta:
        model = Regenerator
    
    id = factory.LazyFunction(uuid4)
    name = factory.Sequence(lambda n: f"Regenerator {n}")
    configuration = {
        "type": "crown",
        "chambers": 2,
        "checker_pattern": "standard"
    }
    created_by = factory.SubFactory(UserFactory)

class ScenarioFactory(factory.Factory):
    class Meta:
        model = OptimizationScenario
    
    id = factory.LazyFunction(uuid4)
    name = factory.Sequence(lambda n: f"Scenario {n}")
    regenerator = factory.SubFactory(RegeneratorFactory)
    user = factory.SubFactory(UserFactory)
    input_parameters = {
        "target_efficiency": 0.85,
        "max_temperature": 1200,
        "fuel_type": "natural_gas"
    }
    status = "DRAFT"

# tests/conftest.py
@pytest.fixture
async def db_session():
    """Provide clean database session for each test."""
    async with TestAsyncSession() as session:
        yield session
        await session.rollback()

@pytest.fixture  
def engineer_user():
    """Provide engineer user for testing."""
    return UserFactory(role=UserRole.ENGINEER)

@pytest.fixture
def admin_user():
    """Provide admin user for testing."""
    return UserFactory(role=UserRole.ADMIN)

@pytest.fixture
def sample_regenerator(engineer_user):
    """Provide sample regenerator for testing."""
    return RegeneratorFactory(created_by=engineer_user)