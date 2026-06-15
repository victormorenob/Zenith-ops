# Error Handling Specification

## Purpose

Prevent unhandled exceptions from leaking to the client as raw 500 HTML. Catch any `Exception` that escapes domain handlers, log with full context via structlog, and return a consistent JSON error.

## Requirements

### Requirement: Global Catch-All Middleware

The system MUST register a catch-all HTTP middleware wrapping every request. It MUST catch any `Exception` that is not handled by the existing domain exception handlers (`ModelNotFoundError`, `InferenceTimeoutError`, `InferenceError`).

The middleware MUST be registered after the `log_requests` middleware so it is the outermost layer.

#### Scenario: Unhandled exception returns consistent JSON 500

- GIVEN a request that raises an `Exception` not matching any domain exception
- WHEN the request is processed
- THEN the response MUST have status 500
- AND the body MUST be `{"error": "internal_error", "message": "An unexpected error occurred"}`

#### Scenario: Stacktrace is logged but not exposed to client

- GIVEN a request that raises an unhandled `Exception`
- WHEN the catch-all middleware catches it
- THEN the full traceback MUST appear in the structlog output
- AND the response body MUST NOT contain the traceback or the exception message

#### Scenario: Domain exception handlers take precedence

- GIVEN a request that raises `ModelNotFoundError`
- WHEN the request is processed
- THEN the existing `model_not_found_handler` runs
- AND the catch-all middleware is NOT triggered
- AND the response is 404 with `{"error": "model_not_found", "message": "..."}`

#### Scenario: InferenceTimeoutError still returns 503

- GIVEN a request that raises `InferenceTimeoutError`
- WHEN the request is processed
- THEN the existing `inference_timeout_handler` runs
- AND the catch-all middleware is NOT triggered
- AND the response is 503 with `{"error": "inference_timeout", "message": "..."}`

#### Scenario: InferenceError still returns 500 with domain message

- GIVEN a request that raises `InferenceError`
- WHEN the request is processed
- THEN the existing `inference_error_handler` runs
- AND the catch-all middleware is NOT triggered
- AND the response is 500 with `{"error": "inference_error", "message": "..."}`

#### Scenario: Catch-all is the outermost middleware

- GIVEN the middleware stack is registered
- WHEN any request arrives
- THEN the catch-all middleware MUST run before `log_requests`
- AND the `log_requests` middleware MUST run before the route handler

### Requirement: Error Logging with Request Context

The catch-all middleware MUST log unhandled exceptions via structlog with the request context.

#### Scenario: Log includes all required fields

- GIVEN a caught exception
- WHEN the catch-all middleware logs the error
- THEN the log MUST contain `correlation_id`, `method`, `endpoint`, and `traceback`
