"""Verify authentication library compatibility."""
import sys
from pathlib import Path

# Add backend and project root to path
backend_dir = Path(__file__).resolve().parent
project_root = backend_dir.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Test 1: PyJWT (jose) compatibility
print("=" * 60)
print("TEST 1: PyJWT / jose library compatibility")
print("=" * 60)
try:
    from jose import JWTError, jwt as j_wt
    import datetime
    
    # Test encode/decode as used in services/auth.py
    payload = {"sub": "test@example.com"}
    token = j_wt.encode(payload, "test-secret", algorithm="HS256")
    decoded = j_wt.decode(token, "test-secret", algorithms=["HS256"])
    assert decoded["sub"] == "test@example.com"
    print("  PASS: PyJWT jose.encode/decode works as in services/auth.py")
    
    # Test expired token
    import time
    expired_payload = {"sub": "test@example.com", "exp": int(time.time()) - 60}
    expired_token = j_wt.encode(expired_payload, "test-secret", algorithm="HS256")
    try:
        j_wt.decode(expired_token, "test-secret", algorithms=["HS256"])
        print("  FAIL: Expired token should be rejected")
    except JWTError:
        print("  PASS: Expired token correctly rejected")
        
except ImportError as e:
    print(f"  FAIL: PyJWT import failed: {e}")
except Exception as e:
    print(f"  FAIL: PyJWT test error: {e}")

# Test 2: passlib bcrypt compatibility
print()
print("=" * 60)
print("TEST 2: passlib bcrypt password hashing")
print("=" * 60)
try:
    from passlib.context import CryptContext
    
    # This matches the actual code in services/auth.py
    pwd_context = CryptContext(schemes=["bcrypt"], bcrypt__rounds=12)
    
    password = "test-password-123!"
    hashed = pwd_context.hash(password)
    verified = pwd_context.verify(password, hashed)
    
    assert verified, "Password verify should pass"
    wrong_verified = pwd_context.verify("wrong-password!", hashed)
    assert not wrong_verified, "Wrong password should be rejected"
    
    print("  PASS: passlib bcrypt hash/verify works as in services/auth.py")
    print(f"  Generated hash: {hashed[:40]}...")
    
except ImportError as e:
    print(f"  FAIL: passlib import failed: {e}")
except Exception as e:
    print(f"  FAIL: passlib test error: {e}")

# Test 3: SQLAlchemy 2.x session consistency
print()
print("=" * 60)
print("TEST 3: SQLAlchemy 2.x session factory consistency")
print("=" * 60)
try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from config import settings
    
    from pathlib import Path
    sys.path.insert(0, str(backend_dir))
    from db.session import engine, SessionLocal
    
    # Verify engine and session are configured
    assert engine is not None, "Engine should be initialized"
    assert SessionLocal is not None, "SessionLocal should be initialized"
    
    # Verify session factory properties
    assert SessionLocal.kw.get('autoflush') == False, "autoflush should be False"
    assert SessionLocal.kw.get('autocommit') == False, "autocommit should be False"
    assert SessionLocal.kw.get('bind') == engine, "bind should be engine"
    
    print("  PASS: SQLAlchemy 2.x engine/session configuration consistent")
    print(f"  Database configured: {settings.is_database_configured}")
    print(f"  Echo mode: {settings.DEBUG} (SQL logging {'ON' if settings.DEBUG else 'OFF'})")
    
except ImportError as e:
    print(f"  FAIL: SQLAlchemy import failed: {e}")
except Exception as e:
    print(f"  FAIL: SQLAlchemy test error: {e}")

# Test 4: FastAPI app imports and route registration
print()
print("=" * 60)
print("TEST 4: FastAPI app imports and OpenAPI route generation")
print("=" * 60)
try:
    from backend.app import app
    from fastapi.openapi.utils import get_openapi
    
    # Generate OpenAPI schema
    openapi_schema = app.openapi()
    assert openapi_schema is not None, "OpenAPI schema should generate"
    assert openapi_schema["info"]["title"] == "ColdChain 360 API"
    assert openapi_schema["info"]["version"] == "1.0.0"
    
    # Count routes
    paths = list(openapi_schema["paths"].keys())
    print(f"  PASS: FastAPI app generates OpenAPI schema")
    print(f"  Total routes in schema: {len(paths)}")
    
    # Check for key routes
    route_paths = [p for p in paths if p.startswith('/api/v1') or p in ('/', '/health', '/health/db')]
    print(f"  Key routes found: {len(route_paths)}")
    for r in sorted(route_paths):
        print(f"    - {r}")
        
except ImportError as e:
    print(f"  FAIL: FastAPI import failed: {e}")
except Exception as e:
    print(f"  FAIL: FastAPI test error: {e}")

print()
print("=" * 60)
print("AUTHENTICATION DEPENDENCY VERIFICATION COMPLETE")
print("=" * 60)