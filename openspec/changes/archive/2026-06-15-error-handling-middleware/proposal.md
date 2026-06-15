# Proposal: Error Handling Middleware

## Intent

Unhandled exceptions (outside the 3 domain handlers) crash the request and FastAPI returns a generic HTML 500 page — inconsistent JSON, no logging, no correlation ID in responses. Clients can't correlate errors back to server logs.

## Scope

### In Scope
- Global catch-all middleware wrapping the entire request cycle
- Log unhandled errors with full context (correlation_id, method, endpoint, traceback)
- Return consistent JSON error response: `{"error": "internal_error", "message": "..."}`
- X-Correlation-ID response header on every response

### Out of Scope
- Changes to existing domain exception handlers (work correctly)
- Sensitive data protection (pospuesto)
- Log rotation (pospuesto)

## Capabilities

### New Capabilities
- `error-handling`: global middleware catching unhandled `Exception`, logging with traceback, returning consistent JSON error responses

### Modified Capabilities
- `logging`: correlation ID spec extended to require `X-Correlation-ID` response header on every response

## Approach

1. **Catch-all middleware** — register a second `@app.middleware("http")` that wraps `call_next` in try/except. On `Exception`: log via structlog (incl. traceback), return `JSONResponse(status_code=500, content={"error": "internal_error", "message": "Internal server error"})`
2. **Response header** — modify existing `log_requests` middleware to set `response.headers["X-Correlation-ID"] = correlation_id` before returning
3. **Order** — catch-all registers after `log_requests`, FastAPI runs them outer-to-inner: catch-all first, then correlation middleware

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `src/zenith_ops/__init__.py` | Modified | Add global error middleware + X-Correlation-ID header |
| `openspec/specs/error-handling/spec.md` | New | New capability spec |
| `openspec/specs/logging/spec.md` | Modified | Add X-Correlation-ID response header requirement |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Catch-all swallows domain handler leaks | Low | Domain handlers registered on `app.exception_handler` — Fire run FIRST. Catch-all only catches what escapes them |
| Wrong middleware order | Low | Register catch-all AFTER correlation middleware to ensure header is always set |

## Rollback Plan

1. Remove the catch-all `@app.middleware("http")` block
2. Revert `log_requests` to not set `X-Correlation-ID`
3. Delete `openspec/specs/error-handling/spec.md` if created
4. No config or dependency changes to revert

## Dependencies

None.

## Success Criteria

- [ ] Unhandled `Exception` returns `{"error": "internal_error", "message": "Internal server error"}` with 500
- [ ] Stacktrace appears in logs but NOT in response body
- [ ] Every response includes `X-Correlation-ID` header with the request's UUID
- [ ] Existing domain handlers (404, 503, 500) still work unchanged
- [ ] All existing tests pass
