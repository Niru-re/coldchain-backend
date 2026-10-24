"""Verify backend routes via OpenAPI schema."""
import sys
from pathlib import Path

# Add project root to path so we can import backend
project_root = Path('C:/Users/nirma/Downloads/FTL2-main')
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Now import from backend.submodule
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