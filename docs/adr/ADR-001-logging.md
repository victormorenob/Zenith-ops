# ADR-001: Structured Logging con structlog

**Estado:** Aprobado
**Fecha:** 2026-06-15
**Autor:** Víctor Moreno
**Stack:** Python 3.12, structlog 25.5+, FastAPI

---

## Decisión

Adoptar **`structlog`** como librería única de logging estructurado, con niveles, correlation IDs por request, y formato legible en desarrollo (conmutable a JSON).

---

## Detalles técnicos

| Aspecto | Decisión |
|---------|----------|
| Librería | `structlog` (ya incluida en `pyproject.toml`) |
| Niveles | DEBUG, INFO, WARNING, ERROR, CRITICAL |
| Logger por módulo | `structlog.get_logger(__name__)` — nombre del módulo automático |
| Correlation ID | UUID v4 generado por middleware, inyectado en `request.state` |
| Formato desarrollo | Consola legible con colores (`ConsoleRenderer`) |
| Formato producción | JSON (`JSONRenderer`) — activado vía `LOG_FORMAT=json` |
| Log por request | `request_completed` con: `method`, `endpoint`, `status`, `duration_ms`, `correlation_id` |
| Protección datos sensibles | Pospuesto — no hay PII en el sistema actualmente |
| Rotación de archivos | Pospuesto — se configurará en deploy con Docker/systemd |

---

## Alternativas descartadas

| Alternativa | Motivo del descarte |
|-------------|---------------------|
| `logging` estándar | Poco estructurado, difícil de parsear en sistemas centralizados |
| `loguru` | Maduro pero no añade ventaja significativa sobre structlog para el caso de uso actual |
| `picologging` | Más rápido en benchmarks pero menos integrado con el ecosistema Python |

---

## Migración desde logging estándar

Todo código nuevo usa `structlog.getLogger(__name__)`.

El código existente que use `logging.getLogger()` se migrará progresivamente. No hay convivencia forzada: structlog puede capturar logs de terceros vía `structlog.stdlib.LoggerFactory`.

---

## Checklist

- [ ] `structlog` está en dependencias
- [ ] Configuración centralizada en `core/logging_config.py`
- [ ] Middleware agrega `correlation_id` a `request.state`
- [ ] Logger por módulo con `structlog.get_logger(__name__)`
- [ ] Log por request con todos los campos acordados
- [ ] Tests validan estructura del log

---

## Referencias

- [structlog docs](https://www.structlog.org/)
- DDD-001: Arquitectura de Zenith-ops
