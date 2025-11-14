"""
Test password normalization for bcrypt 72-byte limit.
"""
import hashlib
import base64


def _normalize_password(password: str) -> str:
    """
    Normalize password for bcrypt (handle passwords > 72 bytes).

    This is the same function from app.core.security.
    """
    password_bytes = password.encode('utf-8')

    if len(password_bytes) > 72:
        sha_hash = hashlib.sha256(password_bytes).digest()
        return base64.b64encode(sha_hash).decode('ascii')

    return password


def test_short_password_unchanged():
    """Short passwords should pass through unchanged."""
    password = "admin123"
    result = _normalize_password(password)
    assert result == password
    assert len(result.encode('utf-8')) <= 72


def test_72_byte_password_unchanged():
    """Exactly 72-byte passwords should pass through unchanged."""
    password = "a" * 72
    result = _normalize_password(password)
    assert result == password
    assert len(result.encode('utf-8')) == 72


def test_long_password_normalized():
    """Passwords > 72 bytes should be SHA-256 hashed."""
    password = "a" * 100
    result = _normalize_password(password)

    # Result should be different from original
    assert result != password

    # Result should be base64 encoded (44 characters for SHA-256)
    assert len(result) == 44
    assert len(result.encode('utf-8')) < 72

    # Should be deterministic
    result2 = _normalize_password(password)
    assert result == result2


def test_unicode_password_normalized():
    """Unicode passwords > 72 bytes should be normalized."""
    # Chinese characters are 3 bytes each in UTF-8
    password = "密码" * 30  # 30 * 2 * 3 = 180 bytes
    password_bytes = password.encode('utf-8')

    assert len(password_bytes) > 72

    result = _normalize_password(password)

    # Result should be normalized
    assert result != password
    assert len(result.encode('utf-8')) < 72

    # Should be deterministic
    result2 = _normalize_password(password)
    assert result == result2


def test_edge_case_73_bytes():
    """Password of exactly 73 bytes should be normalized."""
    password = "a" * 73
    result = _normalize_password(password)

    assert result != password
    assert len(result.encode('utf-8')) < 72


def test_normalization_is_deterministic():
    """Same password should always produce same normalized result."""
    password = "x" * 100

    results = [_normalize_password(password) for _ in range(10)]

    # All results should be identical
    assert len(set(results)) == 1


if __name__ == "__main__":
    # Run tests
    test_short_password_unchanged()
    print("✅ test_short_password_unchanged")

    test_72_byte_password_unchanged()
    print("✅ test_72_byte_password_unchanged")

    test_long_password_normalized()
    print("✅ test_long_password_normalized")

    test_unicode_password_normalized()
    print("✅ test_unicode_password_normalized")

    test_edge_case_73_bytes()
    print("✅ test_edge_case_73_bytes")

    test_normalization_is_deterministic()
    print("✅ test_normalization_is_deterministic")

    print("\n✅ All password normalization tests passed!")
