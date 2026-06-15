# Delta for Logging

## MODIFIED Requirements

### Requirement: Correlation ID Middleware

Every HTTP request MUST receive a UUID v4 correlation ID attached to `request.state.correlation_id`. On completion, the middleware MUST log a `request_completed` event. Every response MUST include the `X-Correlation-ID` response header set to the request's UUID v4 value.
(Previously: every HTTP request gets a correlation_id and a log event, but no response header)

#### Scenario: Per-request log on completion

- GIVEN a request arrives at any endpoint
- WHEN the response is sent
- THEN a log line at INFO level contains `method`, `endpoint`, `status`, `duration_ms`, and `correlation_id`

#### Scenario: Valid UUID v4 format

- GIVEN a request with a `correlation_id` assigned
- WHEN any log is emitted for that request
- THEN `correlation_id` matches UUID v4 regex `^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$`

#### Scenario: X-Correlation-ID on success response

- GIVEN a successful request to any endpoint
- WHEN the response is returned
- THEN the response MUST include the `X-Correlation-ID` header
- AND the header value MUST equal the request's `correlation_id`

#### Scenario: X-Correlation-ID on error response

- GIVEN a request that raises an unhandled exception
- WHEN the catch-all middleware returns the 500 response
- THEN the response MUST include the `X-Correlation-ID` header
- AND the header value MUST equal the request's `correlation_id`
