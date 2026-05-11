# Zenith-Ops — Task Runner
# Uso: just <comando>  |  just (sin args muestra la lista)

# Lista todos los comandos disponibles
default:
    @just --list

# ── Setup ─────────────────────────────────────────────────
# Instala dependencias y configura el entorno
setup:
    uv sync
    uv run pre-commit install
    uv run pre-commit install --hook-type commit-msg
    cp -n .env.example .env || true
    @echo "✅ Setup completo. Edita .env con tus valores locales."

# ── Desarrollo ────────────────────────────────────────────
# Levanta el stack completo en local
start:
    docker compose -f infra/docker/docker-compose.dev.yml up -d
    @echo "🚀 Stack local levantado"

# Para el stack local
stop:
    docker compose -f infra/docker/docker-compose.dev.yml down

# Logs del stack local en tiempo real
logs:
    docker compose -f infra/docker/docker-compose.dev.yml logs -f

# ── Calidad de código ─────────────────────────────────────
# Linter sin modificar archivos
lint:
    uv run ruff check src/ tests/
    uv run mypy src/

# Formatea el código
format:
    uv run ruff format src/ tests/
    uv run ruff check --fix src/ tests/

# ── Tests ─────────────────────────────────────────────────
# Todos los tests con coverage
test:
    uv run pytest tests/ --cov=src --cov-report=term-missing -v

# Solo tests unitarios (rápido, sin infraestructura)
test-unit:
    uv run pytest tests/unit/ -v

# Solo tests de integración
test-integration:
    uv run pytest tests/integration/ -v

# ── Base de datos ─────────────────────────────────────────
# Aplica migraciones pendientes
migrate:
    uv run alembic upgrade head

# Crea nueva migración: just migration "descripcion del cambio"
migration name:
    uv run alembic revision --autogenerate -m "{{name}}"

# Revierte la última migración
rollback:
    uv run alembic downgrade -1

# Resetea la BBDD de desarrollo (¡destructivo!)
db-reset:
    uv run alembic downgrade base
    uv run alembic upgrade head

# ── Docker ────────────────────────────────────────────────
# Construye la imagen de producción
build:
    docker build -f infra/docker/Dockerfile -t ZenithOps-engine:local .
    docker image ls ZenithOps-engine:local

# ── Limpieza ──────────────────────────────────────────────
# Elimina artefactos de build y caché
clean:
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    rm -f .coverage coverage.xml
    @echo "Limpieza completada"
