# Logging Specification

## Purpose

Centralize structured logging with structlog, enable per-request correlation tracking via UUID v4, and switch between human-readable (dev) and machine-parseable (prod) output formats.

## Requirements

### Requirement: Log Format Configuration

The system MUST configure structlog at startup with env-aware renderer selection.

#### Scenario: Development format renders to console

- GIVEN `LOG_FORMAT` is unset or not `json`
- WHEN the application starts
- THEN structlog uses `ConsoleRenderer` with colorized, human-readable output

#### Scenario: JSON format for production

- GIVEN `LOG_FORMAT` is set to `json`
- WHEN the application starts
- THEN structlog uses `JSONRenderer` producing newline-delimited JSON records

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

### Requirement: Logger Per Module

Each module SHOULD obtain its logger via `structlog.get_logger(__name__)` to carry the module name automatically.

#### Scenario: Module-bound logger

- GIVEN a module at `zenith_ops.core.logging_config`
- WHEN `structlog.get_logger(__name__)` is called
- THEN the returned logger is bound to the module name `zenith_ops.core.logging_config`

### Requirement: Third-Party Log Capture

The logging configuration MUST capture stdlib log records from third-party libraries so they appear in the structured output.

#### Scenario: stdlib bridge active

- GIVEN a third-party library emits a log via `logging.getLogger()`
- WHEN the application logging config is loaded
- THEN that log record appears in structlog's pipeline with its original level and message

### Requirement: Log Level Support

The system MUST support the standard levels: DEBUG, INFO, WARNING, ERROR, CRITICAL. The default level SHOULD be INFO.

#### Scenario: Default level is INFO

- GIVEN no log level override
- WHEN the application starts
- THEN DEBUG messages are suppressed and INFO messages are emitted

#### Scenario: Level override via env var

- GIVEN `LOG_LEVEL` is set to `DEBUG`
- WHEN the application starts
- THEN DEBUG messages are emitted
