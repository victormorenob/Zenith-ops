# ADR-008: FileBasedModelRegistry como implementación inicial

**Estado:** Aprobado
**Fecha:** 2026-06-21
**Autor:** Víctor Moreno
**Stack:** Python 3.12, scikit-learn, joblib, FastAPI

---

## Decisión

Implementar `FileBasedModelRegistry` (registro de modelos basado en archivos `.joblib` con scan de directorio) como implementación inicial del Model Registry en Fase 1, postergando la migración a PostgreSQL a Fase 2.

---

## Contexto

La guía original planificaba Model Registry en PostgreSQL desde la Semana 6-7 (ADR-001 conceptual en `docs/GUI_COMPLETA_DESARROLLO.md` §5.2). Al comenzar la implementación evaluamos si tenía sentido arrancar con base de datos relacional o usar una estrategia más liviana.

En paralelo, ya existía infraestructura de base de datos configurada:
- `alembic.ini` con `script_location = src/db/migrations`
- `env.py` async con `Base.metadata` listo
- `async_session_factory` + `engine` en `zenith_ops/db/session.py`
- SQLAlchemy 2.0 + asyncpg + Alembic en dependencias
- `DATABASE_URL` en `.env`

Pero esta infraestructura estaba "pasiva": sin docker-compose para PostgreSQL local, sin modelos ORM definidos, sin migrations creadas, sin servicio PostgreSQL en CI.

---

## Motivación

El objetivo era reducir la fricción inicial y la complejidad del código, permitiendo implementar la lógica de negocio completa del Model Registry rápidamente. PostgreSQL habría añadido desde el día uno:

- Dependencia externa (necesitar PostgreSQL corriendo)
- Docker Compose para desarrollo local
- Migraciones de esquema con Alembic
- Servicio PostgreSQL en CI
- Complejidad de sesiones async, connection pooling, manejo de transacciones

Nada de eso es necesario para la lógica de negocio del registro de modelos. Usar archivos `.joblib` + scan de directorio permitió implementar el mismo `ModelRegistry(Protocol)` con la misma interfaz, pero sin acoplar el desarrollo a una BD externa.

Además, al versionar los modelos como archivos en el repo (`.joblib` en gitignore, metadatos trackeables), el registro tiene trazabilidad inherente por git.

---

## Consecuencias

### Positivas
- Prototipado rápido: lógica de negocio implementada sin esperar infraestructura de BD
- Misma interfaz `ModelRegistry(Protocol)` → intercambiable por PostgreSQL sin cambiar clientes
- `FileBasedModelRegistry.get_instance()` singleton con `scan()` automático
- Tests unitarios sin BD — rápidos, sin fixture externa
- Modelos versionados implícitamente por git (`.joblib` en gitignore, metadatos en código)
- 80 tests verdes, mypy 0 errores, cobertura 92.75%

### Negativas
- Sin concurrencia real — dos procesos escribiendo archivos simultáneamente pueden colisionar
- Sin transacciones — no hay rollback si falla una operación parcial
- Sin consultas eficientes — buscar por estado, framework o métricas requiere scan completo
- No escala horizontalmente — cada instancia tiene su propio filesystem
- Sin migraciones de esquema — cambiar el formato implica migración manual

---

## Plan de migración a PostgreSQL

Cuando se decida migrar, el checklist es:

- [ ] **Docker Compose**: agregar servicio PostgreSQL en `docker-compose.yml` para desarrollo local
- [ ] **Modelos ORM**: definir tablas (`model_registry`, `prediction_metadata`, `health_checks`) contra `Base` de SQLAlchemy
- [ ] **Migration Alembic**: crear `alembic revision --autogenerate` con las tablas
- [ ] **PostgreSQL en CI**: agregar `services.postgres` en `.github/workflows/ci.yml`
- [ ] **Nuevo `PostgresModelRegistry`**: implementar el mismo `ModelRegistry(Protocol)` con SQLAlchemy async
- [ ] **Migración de datos**: script que lea modelos existentes del filesystem y los inserte en PostgreSQL
- [ ] **Tests de integración**: tests contra PostgreSQL real (ya hay precedente en `tests/integration/`)
- [ ] **Deprecar `FileBasedModelRegistry`**: mantenerlo como fallback, documentar que está deprecado

La migración es segura porque el `Protocol` está definido: mientras `PostgresModelRegistry` implemente `register()`, `get_model()`, `list_models()`, el resto del sistema no cambia.

---

## Alternativas descartadas

| Alternativa | Motivo del descarte |
|-------------|---------------------|
| PostgreSQL desde Fase 1 | Añadía complejidad operacional innecesaria para el MVP. La infraestructura de BD existía pero estaba pasiva. Arrancar con archivos permitió entregar la feature completa sin depender de una BD externa. |
| MongoDB | Los metadatos de modelo son datos estructurados (nombre, versión, estado). No hay necesidad de documentos anidados. PostgreSQL con JSONB da la misma flexibilidad cuando se necesite. |
| SQLite | No soporta concurrencia real. Para un sistema que eventualmente servirá múltiples requests, no es una opción. |

---

## Referencias

- ADR-001 (conceptual): Model Registry en PostgreSQL — guía original que este ADR matiza
- DDD-001: Arquitectura de Zenith-ops
- `src/zenith_ops/core/model_registry.py` — `FileBasedModelRegistry`
- `src/db/` — infraestructura de base de datos (actualmente pasiva)
