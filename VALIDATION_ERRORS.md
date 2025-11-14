# User-Friendly Validation Error Messages

## Overview

System FRO now provides user-friendly, Polish-language error messages for all 422 validation errors.

## Implementation

### Backend (`app/main.py`)

Custom `RequestValidationError` handler converts Pydantic validation errors to readable Polish messages:

```python
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Convert technical validation errors to user-friendly Polish messages."""
```

**Response Format:**
```json
{
  "detail": "Błąd walidacji danych",
  "errors": [
    {
      "field": "name",
      "message": "Pole 'name' jest wymagane",
      "type": "missing"
    },
    {
      "field": "max_iterations",
      "message": "Pole 'max_iterations' musi być większe lub równe 10",
      "type": "value_error.number.not_ge"
    }
  ],
  "type": "validation_error"
}
```

### Supported Error Types

| Error Type | Polish Message | Example |
|-----------|----------------|---------|
| `missing` | Pole '{field}' jest wymagane | name is required |
| `value_error` | Nieprawidłowa wartość dla pola '{field}' | Invalid value |
| `type_error` | Nieprawidłowy typ danych dla pola '{field}' | Expected int, got string |
| `string_too_short` | Pole '{field}' jest za krótkie (minimum X znaków) | Min length 1 |
| `string_too_long` | Pole '{field}' jest za długie (maksimum X znaków) | Max length 255 |
| `value_error.number.not_gt` | Pole '{field}' musi być większe niż X | value > 10 |
| `value_error.number.not_ge` | Pole '{field}' musi być większe lub równe X | value >= 10 |
| `value_error.number.not_lt` | Pole '{field}' musi być mniejsze niż X | value < 100 |
| `value_error.number.not_le` | Pole '{field}' musi być mniejsze lub równe X | value <= 100 |
| `enum` | Pole '{field}' musi mieć jedną z wartości: A, B, C | Invalid enum |

### Frontend (`lib/api-client.ts`)

API client enhanced to parse and expose validation errors:

```typescript
// Validation errors are attached to error object
if (response.status === 422 && errorData.errors) {
  const error: any = new Error(errorData.detail || 'Validation error');
  error.validationErrors = errorData.errors;
  error.status = 422;
  throw error;
}
```

### React Component (`components/common/ValidationErrorAlert.tsx`)

Reusable component displays validation errors in user-friendly format:

```tsx
<ValidationErrorAlert
  errors={validationErrors}
  title="Błąd walidacji danych"
  onClose={() => setValidationErrors([])}
/>
```

**Visual Display:**
- Red border alert box
- Error icon
- Field name + message for each error
- Dismissible with X button
- Bullet list format

## Usage Examples

### Example 1: Missing Required Field

**Request:**
```json
POST /api/v1/optimize/scenarios
{
  "scenario_type": "geometry_optimization",
  "objective": "minimize_fuel_consumption"
  // Missing: name, base_configuration_id, design_variables
}
```

**Response (422):**
```json
{
  "detail": "Błąd walidacji danych",
  "errors": [
    {
      "field": "name",
      "message": "Pole 'name' jest wymagane",
      "type": "missing"
    },
    {
      "field": "base_configuration_id",
      "message": "Pole 'base_configuration_id' jest wymagane",
      "type": "missing"
    },
    {
      "field": "design_variables",
      "message": "Pole 'design_variables' jest wymagane",
      "type": "missing"
    }
  ],
  "type": "validation_error"
}
```

### Example 2: Out of Range Value

**Request:**
```json
POST /api/v1/optimize/scenarios
{
  "name": "Test",
  "scenario_type": "geometry_optimization",
  "base_configuration_id": "abc-123",
  "objective": "minimize_fuel_consumption",
  "design_variables": {},
  "max_iterations": 50000  // Max is 10000
}
```

**Response (422):**
```json
{
  "detail": "Błąd walidacji danych",
  "errors": [
    {
      "field": "max_iterations",
      "message": "Pole 'max_iterations' musi być mniejsze lub równe 10000",
      "type": "value_error.number.not_le"
    }
  ],
  "type": "validation_error"
}
```

### Example 3: Invalid Enum Value

**Request:**
```json
POST /api/v1/optimize/scenarios
{
  "name": "Test",
  "scenario_type": "invalid_type",  // Invalid
  "base_configuration_id": "abc-123",
  "objective": "minimize_fuel_consumption",
  "design_variables": {}
}
```

**Response (422):**
```json
{
  "detail": "Błąd walidacji danych",
  "errors": [
    {
      "field": "scenario_type",
      "message": "Pole 'scenario_type' musi mieć jedną z wartości: geometry_optimization, material_optimization, operating_conditions, comprehensive",
      "type": "enum"
    }
  ],
  "type": "validation_error"
}
```

## Frontend Integration

### In Page Components

```typescript
const [validationErrors, setValidationErrors] = useState<Array<{
  field: string;
  message: string;
  type: string;
}>>([]);

const submitForm = async () => {
  setValidationErrors([]);

  try {
    await API.createSomething(data);
  } catch (error: any) {
    if (error.status === 422 && error.validationErrors) {
      setValidationErrors(error.validationErrors);
      return; // Show errors, don't alert
    }
    alert(`Error: ${error.message}`);
  }
};

// In JSX:
{validationErrors.length > 0 && (
  <ValidationErrorAlert
    errors={validationErrors}
    onClose={() => setValidationErrors([])}
  />
)}
```

## Schema Documentation

### Enhanced Field Descriptions

All Pydantic schemas now include Polish descriptions and examples:

```python
class OptimizationScenarioCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Nazwa scenariusza",
        json_schema_extra={"example": "Optymalizacja geometrii regeneratora"}
    )
    max_iterations: int = Field(
        1000,
        ge=10,
        le=10000,
        description="Maksymalna liczba iteracji (10-10000, domyślnie 1000)"
    )
```

## Testing

### Manual Testing via Browser

1. Open `/optimize` page
2. Click "Nowy Scenariusz"
3. Leave "Nazwa" field empty
4. Click "Utwórz"
5. **Expected**: Red alert box with "Pole 'name' jest wymagane"

### Manual Testing via cURL

```bash
# Test missing field
curl -X POST http://localhost:8000/api/v1/optimize/scenarios \
  -H "Content-Type: application/json" \
  -H "Cookie: access_token=YOUR_TOKEN" \
  -d '{
    "scenario_type": "geometry_optimization",
    "objective": "minimize_fuel_consumption",
    "design_variables": {}
  }'

# Expected: 422 with Polish error messages
```

## Benefits

✅ **User-Friendly**: Polish messages instead of technical Pydantic errors
✅ **Actionable**: Clear indication of what field has problem and why
✅ **Consistent**: Same error format across all endpoints
✅ **Developer-Friendly**: Structured errors easy to parse in frontend
✅ **Maintainable**: Centralized error handling in one place

## Files Modified

- `backend/app/main.py` - Custom validation error handler
- `backend/app/schemas/optimization_schemas.py` - Enhanced field descriptions
- `frontend/src/lib/api-client.ts` - Error parsing and propagation
- `frontend/src/components/common/ValidationErrorAlert.tsx` - Display component
- `frontend/src/app/optimize/page.tsx` - Integration example

## System Status (2025-10-01)

✅ **All Core Systems Verified and Operational**

### Authentication & Security
- ✅ Login endpoint working (`/api/v1/auth/login`)
- ✅ JWT token generation and HttpOnly cookies
- ✅ Bcrypt password hashing with SHA-256 pre-hashing for long passwords
- ✅ Admin user operational (username: admin, password: admin)

### API & Database
- ✅ Backend health check passing
- ✅ Database connections established
- ✅ UUID/String mapping working correctly
- ✅ Optimization scenarios query functional
- ✅ CORS configuration correct

### Validation System
- ✅ Custom RequestValidationError handler active
- ✅ Polish error messages implemented
- ✅ Frontend ValidationErrorAlert component ready
- ✅ API client enhanced with error parsing

### Recent Fixes (2025-10-01)
1. **Bcrypt 72-byte limit**: Fixed with SHA-256 pre-hashing in `core/security.py`
2. **Docker dependency**: Rebuilt backend with bcrypt 4.3.0
3. **Optimization status field**: Fixed default value from `ScenarioType.BASELINE` to `"active"`
4. **Migration chain**: Corrected revision IDs and down_revision references

## Future Enhancements

- [ ] Add field highlighting in forms (highlight field with error in red)
- [ ] Add inline error messages next to form fields
- [ ] Support for nested object validation errors
- [ ] Localization support (currently Polish only)
- [ ] Error codes for programmatic handling
- [ ] Fix validation error handler tests (update httpx AsyncClient API usage)
