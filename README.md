# Zenith-ops — Plataforma de serving y operaciones para modelos ML

**Qué es:** código y especificaciones para exponer modelos por API, guardar metadatos en base de datos y, más adelante, observabilidad y ciclo de vida en Kubernetes. **Para quién:** equipos que quieren un camino claro desde la spec hasta el despliegue, con convenciones fijas y revisiones predecibles.

---

## Respuesta corta (30 segundos)

| Pregunta | Respuesta |
|----------|-----------|
| ¿Qué problema resuelve? | Inferencia y operación de modelos con contratos claros (API + datos), sin improvisar estructura en cada feature. |
| ¿En qué está hoy? | Base Python 3.12 (FastAPI, SQLAlchemy async, Alembic), tareas con `just`, documentación de arquitectura y specs; varias capacidades están planificadas por fases. |
| ¿Por dónde empiezo? | `just setup` → `just test-unit` → leer `docs/context/architecture.md` si vas a tocar diseño. |

---

## Camino rápido (happy path)

1. **Requisitos:** Python ≥ 3.12, [uv](https://github.com/astral-sh/uv), [just](https://github.com/casey/just) y, si vas a levantar servicios locales, Docker.
2. **Instalar y comprobar calidad mínima** (desde la raíz del repositorio, junto a `pyproject.toml` y `Justfile`):

   ```bash
   just setup
   just test-unit
   ```

3. **Resultado esperado:** dependencias instaladas, `.env` creado desde `.env.example` si no existía, tests unitarios en verde.

4. **Stack opcional (Postgres, etc.):** `just start` usa `infra/docker/docker-compose.dev.yml`. Para detener: `just stop`.

---

## Detalles (solo lo que suele importar al entrar)

| Tema | Decisión en este repo |
|------|------------------------|
| API | FastAPI, entradas/salidas con Pydantic |
| Datos | PostgreSQL + SQLAlchemy async + migraciones Alembic |
| Logs | `structlog` (sin `print` operativo) |
| Calidad | Ruff, mypy estricto, pytest (`just lint`, `just test`) |
| Cómo se define el trabajo | Spec-Driven Development: specs en `docs/specs/`, convenciones globales en `SPEC-000` |
| Infra objetivo | k3s/Kubernetes + Helm/Terraform en fases posteriores (ver arquitectura) |

Componentes y fases (resumen): ver tabla en [`docs/context/architecture.md`](docs/context/architecture.md).

---

## Mapa del repositorio (dónde mirar)

| Si querés… | Abrí… |
|------------|--------|
| Visión de sistema y roadmap técnico | [`docs/context/architecture.md`](docs/context/architecture.md) |
| Patrones de código (capas, errores, DI) | [`docs/context/conventions.md`](docs/context/conventions.md) y [`docs/specs/SPEC-000-project-conventions.md`](docs/specs/SPEC-000-project-conventions.md) |
| Comandos disponibles | `just` (lista) o [`Justfile`](Justfile) |
| Variables locales | [`.env.example`](.env.example) |

---

## Checklist — “¿entendí el proyecto?”

- [ ] Sé que Zenith-ops apunta a **serving + operaciones** de modelos ML, no solo a un script suelto.
- [ ] Sé que las **convenciones** viven en docs/specs y que debo alinear nuevas features con ellas.
- [ ] Puedo correr **`just setup`** y **`just test-unit`** sin errores en mi máquina.
- [ ] Sé dónde está la **arquitectura** y las **convenciones** enlazadas arriba.

---

## Siguiente paso

Elegí una spec o issue concreta y leéla junto con **SPEC-000**. Si vas a proponer un cambio grande, conviene alinear primero el diseño en `docs/context/architecture.md` o en una spec nueva bajo `docs/specs/`.
