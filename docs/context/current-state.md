# Estado actual del proyecto — 2026-05-11

**Nota (2026-05-14):** el repositorio quedó en una sola raíz (`pyproject.toml` y `Justfile` al mismo nivel); se eliminó la carpeta duplicada `Zenith-ops/Zenith-ops/`.

## Completado

- [x] Entorno Python 3.12 con UV (`pyproject.toml`, `uv.lock`)
- [x] Herramientas de calidad en proyecto: Ruff, mypy strict, pytest + coverage mínimo 70%
- [x] `.cursorrules` y reglas por carpeta `.cursor/rules/*.mdc`
- [x] Memory Bank: `docs/context/*`, plantilla y SPEC-000 en `docs/specs/`
- [x] Ajustes de workspace en `.vscode/settings.json` (editor, Ruff, intérprete `.venv`)

## En progreso

- [ ] Estructura de código `src/api`, `src/core`, `src/db` según Specs
- [ ] Primera API vertical (serving / health) acordada en Spec

## Pendiente (roadmap orientativo)

- [ ] Fase 1: Model Serving API completa según Specs
- [ ] Fase 1: Model Registry persistido
- [ ] Fase 2+: MLflow, observabilidad, drift (según ADRs)

## Dependencias

Ver `[project]` y `[dependency-groups]` en `pyproject.toml`.

## Notas para la IA

- El paquete instalable actual es `zenith_ops` bajo `src/`; la guía SDD describe layout `api/v1`, `core`, `db` como objetivo: seguir la Spec activa para rutas concretas.
- Los tests pueden estar aún mínimos: crear casos según criterios de aceptación de cada Spec.
- La base de datos se configura con `DATABASE_URL` (ver `.env.example`); hasta que haya migraciones y Spec, no asumir tablas concretas.
