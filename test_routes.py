"""Verify backend routes via OpenAPI schema."""
import sys
from pathlib import Path

# Add backend directory and parent to path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
project_root = backend_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from app import app
except ImportError:
    from backend.app import app

# Generate OpenAPI schema and check routes
openapi = app.openapi()
paths = list(openapi["paths"].keys())
print('Total routes:', len(paths))
print()

# Find all /api/v1/ routes
api_v1_paths = [p for p in paths if '/api/v1/' in p]
print('API v1 routes:', len(api_v1_paths))
for p in sorted(api_v1_paths):
    print(' ', p)

# Find health routes
health_paths = [p for p in paths if 'health' in p.lower()]
print('Health routes:', len(health_paths))
for p in sorted(health_paths):
    print(' ', p)

# Find auth routes
auth_paths = [p for p in paths if 'auth' in p.lower()]
print('Auth routes:', len(auth_paths))
for p in sorted(auth_paths):
    print(' ', p)