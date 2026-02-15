# Code Review Fixes TODO

## Critical Issues (RUNTIME ERRORS)

- [ ] 1. Fix import uuid in models.py - Move import to top of file
- [ ] 2. Fix roles/router.py - Fix /blueprint/create endpoint parameter mismatch
- [ ] 3. Fix security.py - Replace deprecated datetime.utcnow() with datetime.now(timezone.utc)

## Frontend Issues

- [ ] 4. Fix api.ts - Auth state bug after login (organization_id not set)
- [ ] 5. Fix api.ts - Add token refresh logic in 401 interceptor

## Performance & Quality Issues

- [ ] 6. Fix session.py - get_sync_db() creates new engine on every call
- [ ] 7. Fix inefficient COUNT queries in multiple repositories/services

