# Getting Started

Guía rápida para clonar, instalar y correr el proyecto localmente.

## Requisitos

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (gestor de paquetes y entornos)
- PostgreSQL 16 (local o en contenedor)
- Git

## Clonar e instalar

```bash
git clone https://github.com/victormorenob/Zenith-ops.git
cd Zenith-ops
uv sync
```

Esto crea el entorno virtual en `.venv/` e instala todas las dependencias (producción y desarrollo).

## Configurar variables de entorno

Copiar y editar:

```bash
cp .env.example .env
```

Variables principales:

| Variable | Descripción | Valor por defecto |
|----------|------------|-------------------|
| `DATABASE_URL` | Conexión a PostgreSQL | `postgresql+asyncpg://user:pass@localhost:5432/zenith_ops` |
| `LOG_LEVEL` | Nivel de logging | `INFO` |

## Correr la aplicación

```bash
# Servidor de desarrollo con recarga automática
uv run uvicorn zenith_ops:app --reload --host 0.0.0.0 --port 8000

# O usando Just
just dev
```

## Ejecutar tests

```bash
# Todos los tests con cobertura
uv run pytest tests/ --cov=src --cov-report=term-missing -v

# Solo tests unitarios
uv run pytest tests/unit/ -v

# Solo tests de integración
uv run pytest tests/integration/ -v

# O usando Just
just test
```

## Calidad de código

```bash
# Linter y formatter
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/

# Type checking estricto
uv run mypy src/

# O todo junto
just lint
```
