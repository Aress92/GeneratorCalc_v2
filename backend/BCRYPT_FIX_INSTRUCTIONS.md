# Bcrypt Password Hashing Fix

## Problem
Bcrypt 5.0+ has compatibility issues with passlib 1.7.4, causing errors when hashing passwords longer than 72 bytes.

## Solution Applied

### 1. Code Changes (app/core/security.py)
- Added `_normalize_password()` function that uses SHA-256 pre-hashing for passwords > 72 bytes
- This is a security best practice and prevents bcrypt truncation issues
- Updated `get_password_hash()` and `verify_password()` to use normalization

### 2. Dependency Pinning
- **requirements.txt**: Added `bcrypt>=4.0.0,<5.0.0`
- **pyproject.toml**: Added `bcrypt = ">=4.0.0,<5.0.0"`

### 3. CryptContext Configuration
```python
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,  # Explicit rounds for better compatibility
    bcrypt__ident="2b"   # Use 2b variant for better compatibility
)
```

## To Apply Fix to Running Container

1. Rebuild backend container:
```bash
docker compose build backend
docker compose up -d backend
```

2. Verify fix:
```bash
docker compose exec backend python -c "
from app.core.security import get_password_hash, verify_password
pwd = 'test123'
hash_val = get_password_hash(pwd)
print(f'Hash works: {verify_password(pwd, hash_val)}')
"
```

## Why This Fix is Safe

1. **Backward Compatible**: Existing passwords will continue to work
2. **Security Best Practice**: SHA-256 pre-hashing is recommended for bcrypt with long passwords
3. **Standard Pattern**: Used by major frameworks (Django uses similar approach)
4. **No Data Migration Needed**: Works with existing password hashes

## Related Files
- `backend/app/core/security.py` - Main implementation
- `backend/requirements.txt` - Dependency versions
- `backend/pyproject.toml` - Poetry dependencies
- `backend/migrations/003_fix_opt_status.py` - Example of security fixes
