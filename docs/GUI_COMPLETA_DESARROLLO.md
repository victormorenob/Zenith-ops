# 🌟 GUÍA COMPLETA DE DESARROLLO — Zenith-ops
### MLOps Portfolio Engine · Víctor · 2026

> *"La diferencia entre un proyecto que existe y uno que no existe es un repositorio con un README."*
>
> *"Un sistema sin proceso no escala. Un proceso sin sistema no arranca."*
>
> *"Los seniors no saben más. Tienen más superficie de contacto con la complejidad y saben gestionarla sin pánico."*

---

**No leas esto como documentación técnica. Léelo como si te lo explicara un amigo senior en un café.**

Este documento fusiona todo lo que necesitas saber sobre Zenith-ops: la visión, el stack, cada decisión arquitectónica, el setup del entorno, el flujo de desarrollo, el estado actual del proyecto, las fases planificadas, la teoría esencial, y cómo trabajar con la IA. No es un resumen. Es la guía completa al nivel de detalle que los roadmaps de `Docs_Claude/` merecen.

---

## Índice

1. [¿Qué es Zenith-ops?](#1-qué-es-zenith-ops)
   - 1.1 El proyecto en una frase
   - 1.2 ¿Para qué existe?
   - 1.3 ¿Qué hace el sistema?
   - 1.4 El problema real que resuelve
   - 1.5 La diferencia con un tutorial
   - 1.6 Fases del proyecto
   - 1.7 ¿Qué vas a aprender en cada fase?
2. [Stack Tecnológico Completo](#2-stack-tecnológico-completo)
   - 2.1 Lenguajes
   - 2.2 Backend
   - 2.3 Base de datos
   - 2.4 Infraestructura y DevOps
   - 2.5 Observabilidad
   - 2.6 ML y datos
   - 2.7 Herramientas de desarrollo
   - 2.8 Servicios cloud gratuitos
3. [Configuración del Entorno (Estado Actual)](#3-configuración-del-entorno-estado-actual)
   - 3.1 Shell: Zsh + Starship + plugins
   - 3.2 Herramientas CLI esenciales
   - 3.3 UV — gestión de Python
   - 3.4 Git + GitHub
   - 3.5 IDE: VS Code + extensiones
4. [Estructura del Proyecto](#4-estructura-del-proyecto)
   - 4.1 Árbol completo de directorios
   - 4.2 ¿Qué hace cada archivo clave?
   - 4.3 Archivos de configuración
   - 4.4 Justfile — el panel de control
5. [Decisiones Arquitectónicas — ADRs](#5-decisiones-arquitectónicas--adrs)
   - 5.1 ¿Qué es un ADR y por qué importa?
   - 5.2 ADR-001: Model Registry en PostgreSQL
   - 5.3 ADR-002: Serving monolítico modular
   - 5.4 ADR-003: Drift y data quality en Fase 2
   - 5.5 ADR-004: Docker Compose → k3s en Hetzner
   - 5.6 ADR-005: MLflow self-hosted
    - 5.7 ADR-006: Prometheus + Grafana + Loki
    - 5.8 ADR-007: Terraform para IaC
    - 5.9 Template de ADR para futuras decisiones
    - 5.10 DDD-001: El documento que las consolida
6. [Flujo de Desarrollo Completo](#6-flujo-de-desarrollo-completo)
    - 6.1 El ciclo: Idea → Archivo
    - 6.2 SDD: Spec-Driven Development
    - 6.3 Git: branches, commits, PRs
    - 6.4 CI/CD: GitHub Actions
    - 6.5 Revisión y merge
    - 6.6 SDLC — Ciclo de Vida del Software
7. [Fases del Proyecto (con estado real)](#7-fases-del-proyecto-con-estado-real)
   - 7.1 FASE 0 — Setup y fundamentos ✅
   - 7.2 FASE 1 — MVP: API + Model Registry 🔧
   - 7.3 FASE 2 — MLOps Real 📝
   - 7.4 FASE 3 — Infraestructura Completa 📝
   - 7.5 Tabla resumen: estado de cada objetivo
8. [Teoría Esencial](#8-teoría-esencial)
   - 8.1 ¿Qué es una API REST?
   - 8.2 ¿Qué es un endpoint?
   - 8.3 Async / Await en Python
   - 8.4 Pydantic y validación de datos
   - 8.5 Cache en memoria
   - 8.6 Idempotencia
   - 8.7 Health checks: liveness vs readiness
   - 8.8 Flujo completo de POST /v1/predict
   - 8.9 Códigos de estado HTTP
   - 8.10 ¿Qué es un UUID?
9. [Cómo Trabajar con la IA](#9-cómo-trabajar-con-la-ia)
   - 9.1 Roles claros
   - 9.2 Cómo pedir cosas
   - 9.3 Cómo revisar el código que genera la IA
   - 9.4 Cómo saber si estás aprendiendo (señales)
    - 9.5 Señales de que estamos yendo muy rápido
    - 9.6 Qué NO delegar a la IA (nunca)
    - 9.7 Flujo SDD con IA — Paso a paso
    - 9.8 El contrato con la IA
10. [Carril B — Aprendizaje Paralelo](#10-carril-b--aprendizaje-paralelo)
    - 10.1 Filosofía de selección
    - 10.2 AWS Solutions Architect (SAA-C03)
    - 10.3 CKAD — Certified Kubernetes Application Developer
    - 10.4 Deep Learning / Fast.ai
    - 10.5 System Design
    - 10.6 Proyección Salarial y Fases de Carrera
    - 10.7 Preparación para Entrevistas
11. [Glosario](#11-glosario)

---

# 1. ¿QUÉ ES ZENITH-OPS?

## 1.1 El proyecto en una frase

Zenith-ops es una **API que sirve predicciones de Machine Learning en producción**, con todo lo que necesita para funcionar de verdad: base de datos, monitoreo, detección de errores, despliegue automático y capacidad de escalar.

Pero eso es el QUÉ. El POR QUÉ es más importante.

## 1.2 ¿Para qué existe?

Tú trabajas en Indra con Kubernetes, pero **quieres pasar a un rol de MLOps Engineer**. El problema es que:

- En tu trabajo tocas K8s, pero no disenas el sistema — aplicas configs que ya existen.
- No tienes experiencia real con **modelos de ML en producción**, que es el core de MLOps.
- Un reclutador de MLOps necesita ver que entiendes **todo el ciclo de vida**: desde que un científico de datos entrena un modelo hasta que ese modelo está en producción siendo monitoreado.

Este proyecto **cierra esa brecha**. No es un curso, no es un tutorial — es **el sistema que vas a poder mostrar en una entrevista y decir "esto lo diseñé y construye yo"**.

## 1.3 ¿Qué hace el sistema? Visto desde afuera

Imaginate que sos un cliente (o un científico de datos) que quiere usar Machine Learning sin tener que saber de infraestructura.

Con Zenith-ops puedes:

1. **Registrar un modelo** — subes los metadatos de tu modelo (nombre, versión, métricas)
2. **Hacer predicciones** — llamas a un endpoint con datos y recibes un resultado
3. **Versionar modelos** — tienes staging, producción, archivado; puedes promover versiones
4. **Monitorear rendimiento** — ves en un dashboard: latencia, tasa de error, cantidad de predicciones
5. **Detectar degradación** — el sistema te avisa si el modelo empieza a dar resultados raros (drift)
6. **Reentrenar automáticamente** — cuando se detecta degradación, el sistema puede entrenar un nuevo modelo solo

Todo expuesto como una API REST, documentada automáticamente, con tests, CI/CD, y despliegue en la nube.

## 1.4 El problema real que resuelve

No alcanza con un endpoint que devuelva una predicción. En MLOps, el modelo es solo una parte. Un endpoint de predicción sin monitoreo no sirve en producción porque:

- **No sabes si está funcionando** hasta que un usuario se queja
- **No sabes si el modelo se está degradando** — los modelos de ML empeoran con el tiempo porque los datos cambian
- **No tienes trazabilidad** — si algo sale mal, no sabes qué versión del modelo respondió
- **No tienes rollback** — si despliegas una versión mala, no puedes volver atrás fácilmente

Zenith-ops resuelve todo eso. No es "una API con un modelo", es **un sistema de producción para ML**.

## 1.5 La diferencia con un tutorial

Un tutorial te da código y dices "ah, mira, funciona". Pero en una entrevista:

> **"¿Por qué elegiste FastAPI y no Flask?"**
>
> *Tutorial: no te prepara para esto.*
>
> **Zenith-ops:** "En el ADR-001 documento que FastAPI tiene soporte nativo de async, validación con Pydantic, documentación OpenAPI automática, y mejor rendimiento que Flask para carga de inferencia. Consideré Flask por su simplicidad, pero el proyecto necesita manejar requests concurrentes de predicción sin bloquear el event loop."

Esa diferencia se nota en 10 segundos en una entrevista.

## 1.6 Fases del proyecto

| Fase | Qué se construye | Estado |
|------|------------------|--------|
| **Fase 0** | Python + setup del entorno + fundamentos | ✅ Completada |
| **Fase 1** | MVP: API REST + Model Registry + CI/CD + Deploy | ✅ Completada (2026-06-26) |
| **Fase 2** | MLOps: MLflow + Prometheus + Grafana + Drift Detection | 📝 Planeada |
| **Fase 3** | Infraestructura: Kubernetes + Terraform + Portfolio | 📝 Planeada |

### Lo que está FUERA del alcance del proyecto

| Tecnología | Por qué no entra |
|---|---|
| Autenticación/Auth | No es un producto SaaS, es un portfolio técnico. Auth añade complejidad sin valor demostrable. |
| Frontend UI | El proyecto es API-first. La UI no aporta valor de portfolio MLOps. |
| Streaming en tiempo real (Kafka) | Kafka merece un proyecto aparte. Para este stack, las colas simples (Redis/Celery) alcanzan. |
| Multi-tenancy | No tenemos múltiples clientes. No aporta valor al objetivo del proyecto. |

## 1.7 ¿Qué vas a aprender en cada fase?

**Después de Fase 1:**
- Diseñar y construir una API REST en Python con FastAPI
- Escribir tests unitarios y de integración con pytest
- Configurar CI/CD con GitHub Actions
- Desplegar una aplicación en la nube
- Escribir ADRs documentando decisiones técnicas
- Implementar patrones de producción: health checks, idempotencia, caché, structured logging

**Después de Fase 2:**
- Integrar MLflow para tracking de experimentos
- Exponer métricas de negocio con Prometheus
- Construir dashboards en Grafana
- Implementar detección de drift con Evidently AI
- Automatizar reentrenamiento de modelos

**Después de Fase 3:**
- Diseñar Helm charts desde cero
- Provisionar infraestructura con Terraform
- Desplegar y operar Kubernetes en un VPS real
- Documentar un sistema completo como portfolio

---

# 2. STACK TECNOLÓGICO COMPLETO

Cada herramienta acá tiene un propósito único y está justificada. No hay duplicados ni tecnología por moda.

### 2.1 Lenguajes

| Lenguaje | Rol | ¿Por qué este y no otro? |
|---|---|---|
| **Python 3.12+** | Backend, ML, scripting | Omnipresente en IA/ML. FastAPI es el framework más eficiente por productividad/rendimiento para APIs. Sin alternativa real en el mundo de modelos. |
| **Bash/Shell** | Automatización, CI/CD, scripts | Un engineer que no puede leer o escribir un script de bash es dependiente de interfaces gráficas. Inaceptable en MLOps. |

### 2.2 Backend

| Componente | Tecnología | ¿Por qué? |
|---|---|---|
| Web framework | **FastAPI** | Async-first, tipado, validación con Pydantic, documentación OpenAPI automática, rendimiento benchmarkeable con Go. No es Flask — es el framework moderno de Python. |
| Servidor ASGI | **Uvicorn** | Corre la aplicación FastAPI. Maneja conexiones concurrentes con event loop. |
| Validación | **Pydantic v2** | Runtime type system. Define schemas de entrada/salida, valida automáticamente, genera errores 422 con el campo exacto que falló. |
| Task queue | **Celery + Redis** (Fase 2) | Para tareas asíncronas como reentrenamiento. |
| API design | **REST primero** | El estándar más universal. GraphQL solo cuando el grafo de datos lo justifique. |

### 2.3 Base de datos

| Componente | Tecnología | ¿Por qué? |
|---|---|---|
| Base de datos | **PostgreSQL 16** | Ninguna base NoSQL reemplaza el conocimiento de SQL avanzado. CTEs, window functions, índices, JSONB. El 80% de los sistemas de producción tienen una BD relacional en el core. |
| ORM | **SQLAlchemy async** | Mapea tablas a objetos Python de forma asíncrona. No bloquea el event loop mientras espera a la BD. |
| Driver | **asyncpg** | Driver nativo de PostgreSQL para asyncio. El más rápido del ecosistema Python. |
| Migraciones | **Alembic** | Control de versiones de la BD. Cada cambio al schema es una migración versionada, no un DROP TABLE. |

### 2.4 Infraestructura y DevOps

| Componente | Tecnología | Uso |
|---|---|---|
| Contenedores | **Docker + Docker Compose** | Desarrollo local. PostgreSQL + app en contenedores. |
| Orquestación | **Kubernetes (k3s)** (Fase 3) | Ya lo conoces de Indra. Acá lo disenas tú desde cero. |
| CI/CD | **GitHub Actions** | Tests automáticos en cada PR. Build + Deploy en merge a main. |
| Container registry | **GHCR** (GitHub Container Registry) | Gratuito, integrado con GitHub. |
| IaC | **Terraform / OpenTofu** (Fase 3) | Infraestructura como código. Estándar de la industria. |

### 2.5 Observabilidad

| Componente | Tecnología | Cuándo |
|---|---|---|
| Experiment tracking | **MLflow** (self-hosted OSS) | Fase 2 |
| Métricas | **Prometheus** | Fase 2 |
| Dashboards | **Grafana** | Fase 2 |
| Logs | **Loki** | Fase 2 |
| Drift detection | **Evidently AI** | Fase 2 |
| Error tracking | **Sentry** | Fase 1 (final) |
| Alertas | **Alertmanager** | Fase 2 |

> Un sistema sin observabilidad no es un sistema en producción. Es un sistema que espera fallar en silencio.

### 2.6 ML y datos

| Componente | Tecnología | ¿Por qué? |
|---|---|---|
| ML Framework | **scikit-learn** (ahora), **PyTorch 2.x** (Fase 2) | Ahora modelos clásicos. Después deep learning. |
| Serialización | **joblib** | Formato estándar para serializar modelos sklearn. |
| Procesamiento | **Pandas 2.x** → **Polars** (cuando los datasets crezcan) | Polars está escrito en Rust, usa Apache Arrow, es lazy por defecto y 5-20x más rápido que Pandas. |
| Vectores | **pgvector** (en PostgreSQL) | Embeddings en la misma BD que los metadatos. Sin infraestructura extra. |

### 2.7 Herramientas de desarrollo

| Herramienta | Propósito | Configuración |
|---|---|---|
| **UV** | Gestor de entornos y dependencias Python | Reemplaza pip + venv + pyenv + pip-tools. Escrito en Rust, 100x más rápido. |
| **Ruff** | Linter + formatter | Reemplaza black + flake8 + isort. Configurado en `pyproject.toml`. |
| **Mypy** | Type checker estático | `strict = true` en `pyproject.toml`. |
| **Pytest** | Framework de tests | Con `pytest-asyncio`, `pytest-cov`, `pytest-httpx`. |
| **Pre-commit** | Hooks automáticos antes de cada commit | Ruff + mypy + commitizen. |
| **Commitizen** | Conventional Commits forzados | `cz commit` en lugar de `git commit`. |
| **Just** | Task runner | `just test`, `just lint`, `just start`. |
| **Delta** | git diff mejorado | Syntax highlighting en diffs. |

### 2.8 Servicios cloud gratuitos

| Servicio | Uso | Cuándo |
|---|---|---|
| **GitHub** | Repo, CI/CD, Container Registry | Desde el día 1 |
| **Fly.io** | Deploy de la API (3 VMs compartidas gratis) | Fase 1 |
| **Neon** | PostgreSQL serverless 500 MB gratis | Fase 1 |
| **Upstash** | Redis gestionado (10K cmd/día gratis) | Fase 2 |
| **Cloudflare Workers** | Edge functions, rate limiting | Fase 2+ |
| **Hetzner VPS** | Servidor de producción (~5€/mes) | Fase 3 |
| **Sentry** | Error tracking (tier gratuito) | Fase 1 (final) |

---

# 3. CONFIGURACIÓN DEL ENTORNO (ESTADO ACTUAL)

Esto ya está configurado. No necesitas repetirlo. Está acá para que entiendas qué tienes y por qué.

### 3.1 Shell: Zsh + Starship + plugins

El shell por defecto es Zsh con Oh My Zsh y Starship como prompt. Los plugins activados:

| Plugin | Función |
|---|---|
| `zsh-autosuggestions` | Sugerencias de comandos basadas en el historial (mientras escribes, te aparece gris lo que probablemente quieres escribir) |
| `zsh-syntax-highlighting` | Colorea comandos válidos en verde, inválidos en rojo |
| `zsh-completions` | Autocompletado extendido para Docker, kubectl, git |

**Aliases activos:**

```bash
alias ls='eza --icons --git'
alias ll='eza -la --icons --git'
alias cat='bat'
alias grep='rg'
alias cd='z'          # zoxide: cd inteligente
alias lg='lazygit'
alias dc='docker compose'
alias py='python3'
```

Si ves que un alias no te funciona, revisa `~/.zshrc`.

### 3.2 Herramientas CLI esenciales

| Herramienta | Reemplaza a | Para qué la usas en el proyecto |
|---|---|---|
| **eza** | `ls` | Ver estructura del proyecto con árbol (`eza --tree`) |
| **bat** | `cat` | Leer archivos con syntax highlighting |
| **fd** | `find` | Buscar archivos (mucho más rápido) |
| **ripgrep (rg)** | `grep` | Buscar texto en el código |
| **fzf** | — | Fuzzy search: Ctrl+R en historial, Ctrl+T en archivos |
| **zoxide** | `cd` | Navegar con `z proyecto` en vez de la ruta completa |
| **lazygit** | `git` CLI | Gestión visual de Git desde terminal |
| **delta** | `git diff` | Diffs con syntax highlighting |
| **httpie** | `curl` | Testear endpoints de forma legible |
| **just** | `make` | Task runner del proyecto |

### 3.3 UV — gestión de Python

UV es el gestor de paquetes y entornos. Reemplaza a pip + venv + pyenv + pip-tools. Está escrito en Rust, todo es sensiblemente más rápido.

**Comandos que usas todo el tiempo:**

```bash
uv sync              # Instalar/actualizar dependencias del proyecto
uv run pytest        # Ejecutar un comando dentro del entorno del proyecto
uv run python script.py
uv add requests      # Añadir una dependencia al proyecto
uv remove requests   # Eliminar una dependencia
uv lock              # Actualizar el lockfile
```

`.venv/` es el entorno virtual. No se commitea (está en `.gitignore`). `uv.lock` SÍ se commitea — es el lockfile que asegura que todos tienen las mismas versiones.

### 3.4 Git + GitHub

**Configuración:** SSH key vinculada a GitHub. Rama por defecto: `main`. Commits firmados con GPG (opcional pero recomendado para portfolio profesional).

**Secretos de CI/CD (en GitHub → Settings → Secrets and variables → Actions):**
- `FLY_API_TOKEN` — token para deployar en Fly.io
- Otros se añaden según se necesiten (nunca en el código)

### 3.5 IDE: VS Code + extensiones

**Extensiones instaladas:**

| Extensión | Función |
|---|---|
| `ms-python.python` | Soporte Python |
| `charliermarsh.ruff` | Linter + formatter al guardar |
| `eamodio.gitlens` | Blame inline, historial de archivos |
| `mhutchie.git-graph` | Árbol visual de commits |
| `ms-azuretools.vscode-docker` | Docker desde el IDE |
| `redhat.vscode-yaml` | YAML con validación |

**Configuración clave:**

```json
"editor.formatOnSave": true,
"editor.codeActionsOnSave": {
    "source.fixAll.ruff": "explicit"
},
"[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff"
}
```

Esto significa: cuando guardas un archivo Python, Ruff lo formatea automáticamente. No piensas en el formato nunca más.

**Nota sobre Cursor → VS Code:**

La guía original de `Docs_Claude/` estaba escrita para Cursor IDE. Ahora usas VS Code. El cambio más importante: **Cursor indexa automáticamente todo el proyecto** (puede leer cualquier archivo sin que se lo pidas). En VS Code necesitas herramientas explícitas para darle contexto a la IA.

| Capacidad | Cursor | VS Code + OpenCode |
|---|---|---|
| Indexar todo el proyecto | Automático | Explícito — herramientas de archivos como `glob`, `grep`, `read` |
| Reglas de IA por carpeta | `.cursorrules` + Project Rules | `AGENTS.md` global + Skills por tarea |
| Contexto persistente | Automático entre sesiones (con indexado) | Engram — `mem_save`/`mem_search` (comandos explícitos) |
| Commands inline | `Ctrl+K` en cualquier archivo | `/ask`, `/task` en OpenCode |
| Modelos múltiples | Integrados en el IDE | Configurables en `opencode.json` |

**Conclusión:** VS Code requiere más comunicación explícita. Le tienes que decir qué archivos leer, qué Skills cargar, y guardar manualmente el contexto (Memory Bank). Pero las Skills (`angular-core`, `sdd-propose`, etc.) estandarizan el comportamiento, y no pierdes nada de calidad.

---

# 4. ESTRUCTURA DEL PROYECTO

### 4.1 Árbol completo de directorios

```
Zenith-ops/
│
├── .github/
│   └── workflows/          ← CI/CD pipelines
│
├── docs/
│   ├── adr/                ← Architecture Decision Records
│   │   └── DDD-001-arquitectura.md
│   ├── context/            ← Documentación del contexto
│   ├── diagrams/           ← Diagramas de arquitectura
│   ├── runbooks/           ← Cómo operar el sistema
│   └── specs/              ← Especificaciones técnicas
│       ├── SPEC-000-project-conventions.md
│       ├── SPEC-001-predict-endpoint.md
│       └── _TEMPLATE.md
│
├── openspec/               ← Artefactos SDD (Spec-Driven Development)
│   ├── config.yaml
│   ├── changes/
│   │   ├── health-checks/  ← Tasks + verify report de health checks
│   │   └── archive/        ← Cambios archivados
│   └── specs/
│       └── predict/spec.md
│
├── infra/
│   ├── docker/             ← Dockerfiles + docker-compose (dev + prod)
│   ├── helm/               ← Fase 3+, no implementado
│   └── terraform/          ← Fase 3+, no implementado
│
├── models/                 ← Modelos .joblib (NO versionados)
│   └── iris-classifier.joblib
│
├── scripts/                ← Scripts de utilidad
│
├── src/
│   ├── db/migrations/      ← Alembic (alembic.ini → script_location)
│   ├── monitoring/.gitkeep ← Fase 2+, no implementado
│   ├── training/.gitkeep   ← Fase 2+, no implementado
│   └── zenith_ops/         ← Paquete Python instalable
│       ├── __init__.py      → App FastAPI + exception handlers
│       ├── api/
│       │   ├── schemas/
│       │   │   └── predict.py
│       │   └── v1/
│       │       ├── health.py        → GET /health/live, /health/ready
│       │       ├── predict.py       → POST /v1/predict
│       │       ├── models.py        → CRUD model registry
│       │       ├── test_feature.py  → Endpoint de prueba (temporal)
│       │       └── schemas/
│       │           └── models.py
│       ├── core/
│       │   ├── exceptions.py          → Errores de dominio
│       │   ├── model_registry.py      → Interfaz del registry
│       │   ├── model_registry_db.py   → Implementación PostgreSQL
│       │   ├── model_builders.py        → Builders para tests/seed
│       │   ├── dummy_model.py         → Modelo falso para tests
│       │   ├── settings.py            → Config desde variables de entorno
│       │   ├── logging_config.py      → structlog
│       │   └── sentry_config.py       → Sentry (opcional)
│       ├── db/                        ← ORM SQLAlchemy (sin migraciones aquí)
│       │   ├── base.py
│       │   ├── session.py
│       │   └── models/
│       │       ├── model_registry.py
│       │       └── prediction_metadata.py
│       └── services/
│           └── predictor.py           → InferenceService (inferencia + caches)
│
├── tests/
│   ├── unit/               ← Tests sin I/O externo
│   │   ├── test_feature.py
│   │   ├── test_health.py
│   │   ├── test_inference_service.py
│   │   ├── test_model_builders.py
│   │   ├── test_postgres_model_registry.py
│   │   └── test_smoke.py
│   └── integration/        ← Tests contra FastAPI real
│       ├── conftest.py
│       ├── test_health.py
│       ├── test_predict_endpoint.py
│       ├── test_model_registry_api.py
│       └── test_error_handling.py
│
├── .env.example            ← Variables de entorno (sin valores reales)
├── .gitignore              ← .env, .venv, __pycache__, etc.
├── .pre-commit-config.yaml
├── .python-version          ← Versión de Python del proyecto
├── Justfile                ← Task runner
├── pyproject.toml          ← Configuración centralizada del proyecto
├── uv.lock                 ← Lockfile de dependencias (se commitea)
└── README.md               ← Portada del proyecto
```

**ORM vs migraciones:** modelos y sesión en `zenith_ops/db/`; revisiones Alembic en `src/db/migrations/`.

### 4.2 ¿Qué hace cada archivo clave?

#### `src/zenith_ops/__init__.py` — La app FastAPI

```python
app = FastAPI()

# Exception handlers: atrapan errores de dominio y los convierten a HTTP
@app.exception_handler(ModelNotFoundError)   → 404
@app.exception_handler(InferenceTimeoutError) → 503
@app.exception_handler(InferenceError)        → 500

# Routers registrados
app.include_router(health_router)   # /health/live, /health/ready
app.include_router(predict_router)  # POST /v1/predict
app.include_router(feature_router)  # POST /v1/test-feature (temporal)
```

#### `src/zenith_ops/core/exceptions.py` — Errores de dominio

Son excepciones Python puras, sin HTTP. La capa de API las traduce a códigos HTTP:

```
ModelNotFoundError     → 404
InferenceTimeoutError  → 503
InferenceError         → 500
```

**¿Por qué separar errores de HTTP?** Porque `core/` no debe saber que existe HTTP. Si mañana cambias FastAPI por otro framework, los errores de dominio siguen funcionando.

#### `src/zenith_ops/services/predictor.py` — El cerebro

Hace tres cosas:

1. **Carga modelos lazy** — solo cuando los pides (no al arrancar)
2. **Cachea modelos en memoria** — para no leer el disco cada vez
3. **Ejecuta inferencia con timeout** — 5 segundos máximo

```python
class InferenceService:
    _models: dict[str, Any] = {}               # Caché de modelos cargados
    _idempotency_cache: dict[str, tuple] = {}   # Caché de resultados repetidos

    @classmethod
    async def predict(cls, model_id, features, idempotency_key=None):
        # 1. Si hay idempotency_key y ya fue procesada → devolver cache
        # 2. Si no → cargar modelo (de caché o disco vía ModelRegistry)
        # 3. Ejecutar model.predict(features) con timeout
        # 4. Medir latencia con time.monotonic()
        # 5. Guardar en caché de idempotencia
        # 6. Devolver (resultado, tipo_resultado, latencia_ms)
```

#### `src/zenith_ops/api/v1/predict.py` — El endpoint

1. Recibe JSON → Pydantic lo valida → si inválido: 422
2. Si hay `idempotency_key` en caché → devuelve respuesta guardada
3. Si no → llama a `InferenceService.predict()`
4. Arma `PredictResponse` con `prediction_id` (UUID único)
5. Guarda en caché de idempotencia
6. Devuelve 200

#### `src/zenith_ops/api/v1/health.py` — Health checks

- `GET /health/live` → 200 inmediato, sin tocar BD ni disco. Verifica que el proceso está vivo.
- `GET /health/ready` → chequea PostgreSQL + caché de modelos. 200 si todo bien, 503 si algo falla.

#### `src/zenith_ops/core/settings.py` — Config del sistema

```python
class Settings(BaseSettings):
    DATABASE_URL: PostgresDsn
```

Lee variables de entorno (o `.env`). Pydantic valida que la URL tenga formato correcto.

### 4.3 Archivos de configuración

| Archivo | Qué contiene |
|---|---|
| `pyproject.toml` | Metadatos del proyecto, dependencias, Ruff, Mypy, Pytest, Commitizen |
| `.pre-commit-config.yaml` | Hooks que corren automáticamente antes de cada commit |
| `.env.example` | Lista de variables de entorno necesarias (sin valores reales) |
| `.github/workflows/*.yml` | Pipelines de CI/CD |
| `Justfile` | Comandos del proyecto |

### 4.4 Justfile — el panel de control

No memorices comandos. Usa `just`:

```bash
just setup             # Instala dependencias
just test              # Todos los tests con coverage
just test-unit         # Tests unitarios (rápidos)
just test-integration  # Tests de integración
just lint              # Ruff + mypy
just format            # Formatea el código
just start             # Levanta el stack local
just stop              # Para el stack local
just build             # Construye imagen Docker
just logs              # Logs en tiempo real
just migrate           # Aplica migraciones
just migration "msg"   # Crea nueva migración
```

---

# 5. DECISIONES ARQUITECTÓNICAS — ADRs

### 5.1 ¿Qué es un ADR y por qué importa?

Un ADR (Architecture Decision Record) documenta una decisión técnica importante: qué elegiste, qué alternativas descartaste y por qué.

**¿Cuándo se escribe un ADR?**
- Cuando eliges un framework sobre otro
- Cuando eliges una base de datos
- Cuando decides una estrategia de despliegue
- Cuando cambias una decisión anterior

**¿Por qué importan tanto para tu portfolio?**

> **"¿Por qué elegiste PostgreSQL y no MongoDB?"**
>
> *Candidato sin ADRs:* "Porque es el estándar."
>
> *Candidato con ADRs:* "Documenté la decisión en ADR-001: necesitaba integridad referencial (foreign keys), consultas ad-hoc con joins entre modelos y predicciones, y JSONB para métricas flexibles. MongoDB ganaba en escalabilidad horizontal, pero no la necesito para este volumen. Evalué ambas y PostgreSQL ganaba en 3 de 4 criterios."

La segunda respuesta es la de un senior.

Actualmente hay **7 ADRs documentados** en `docs/adr/DDD-001-arquitectura.md` y decisiones adicionales.

### 5.2 ADR-001: Model Registry en PostgreSQL

**Decisión:** Almacenar metadatos del Model Registry en PostgreSQL (SQLAlchemy async). Artefactos .joblib en filesystem.

**Alternativas descartadas:**
| Alternativa | Por qué se descartó |
|---|---|
| MongoDB | Los metadatos de modelo son datos estructurados (nombre, versión, estado, fecha). No necesitamos documentos anidados. PostgreSQL con JSONB da la flexibilidad de esquema cuando la necesitamos. |
| SQLite | No soporta conexiones concurrentes. En producción con múltiples requests, serializa todo. Inviable. |
| Archivos JSON en disco | Sin integridad referencial, sin consultas eficientes, sin migraciones. Es la opción "funciona en mi máquina". |

### 5.3 ADR-002: Serving monolítico modular

**Decisión:** Elegimos monolito modular (FastAPI con paquetes `api/`, `core/`, `db/`) con extracción a microservicios planificada cuando un dominio requiera escalado independiente.

**Alternativas descartadas:**
| Alternativa | Por qué se descartó |
|---|---|
| Microservicios desde el día 1 | Multiplican infraestructura (Dockerfiles, CI/CD, secretos, service discovery). Para 1 desarrollador, el overhead operacional supera cualquier beneficio. |
| Monolito sin estructura | Sin separación de capas, el código se mezcla y es imposible testear, extraer servicios, o mantener. La estructura `api/` → `core/` → `db/` es la línea roja mínima. |

### 5.4 ADR-003: Drift y data quality en Fase 2

**Decisión:** Great Expectations (calidad de datos) + Evidently AI (drift estadístico) pospuestos a Fase 2.

Son complementarios, no intercambiables:
- **Great Expectations:** mide validez de datos entrantes (nulos, rangos, tipos)
- **Evidently AI:** mide drift distribucional (PSI, KS, Jensen-Shannon)

Ninguno es necesario para el MVP de Fase 1.

### 5.5 ADR-004: Docker Compose → k3s en Hetzner

**Decisión:** Fase 1 con Docker Compose local, salto a k3s auto-gestionado en Hetzner en Fase 3.

| Alternativa | Por qué se descartó |
|---|---|
| Fly.io | Es más fácil pero no se aprende K8s de verdad. No prepara para el CKAD. |
| AWS EKS | Demasiado caro para 1 dev (~70€/mes mínimo). k3s en Hetzner cuesta ~4€/mes. |

### 5.6 ADR-005: MLflow self-hosted

**Decisión:** MLflow self-hosted (open source, local) para tracking de experimentos.

W&B y Neptune cuestan $50+/user/mes. Para proyecto individual sin financiación, MLflow cubre todo (params, métricas, artefactos, comparación de runs) sin costo.

**Trade-off:** UI más básica que W&B, sin colaboración en tiempo real.

### 5.7 ADR-006: Prometheus + Grafana + Loki

**Decisión:** Stack OSS Prometheus + Grafana + Loki para observabilidad.

Stack completo (métricas + logs + dashboards), auto-hosteable, sin licencias. Es el estándar de la industria y lo que más pesa en portfolio técnico.

### 5.8 ADR-007: Terraform para IaC

**Decisión:** Terraform con provider hcloud (Hetzner) para Infrastructure as Code.

Es el estándar de la industria, el provider Hetzner está maduro, y el proyecto es para aprender. Pulumi (Python) sería más cómodo pero no aporta el mismo valor de portfolio.

### 5.9 Template de ADR para futuras decisiones

Cada ADR se guarda en `docs/adr/ADR-NNN-titulo-breve.md`. Usa este template:

```markdown
# ADR-NNN: [Titulo corto — decision concreta]

**Estado:** Aceptada | Propuesta | Deprecada
**Fecha:** YYYY-MM-DD
**Contexto:** [Issue / discusion que origino la decision]

---

## Contexto

[El problema que enfrentamos y por que requeria una decision explicita.
No describas la solucion, describi el problema y las fuerzas en juego.
2-4 frases. Inclui el contexto de negocio si aplica.]

## Decision

[Que decidimos hacer. Una frase clara.]

## Alternativas consideradas

| Alternativa | Por que se descarto (o se eligio) |
|---|---|
| [Nombre de la opcion] | [Razon concreta. No "no nos gusto", sino "no cumple el requerimiento X"] |
| [Otra opcion] | [Misma precision] |

## Consecuencias

### Positivas
- [Beneficio 1]
- [Beneficio 2]

### Negativas / trade-offs
- [Riesgo o coste 1]
- [Riesgo o coste 2]

## Referencias

- [Enlace a issue, spec, o documento relevante]
- [Enlace a PR donde se implemento]
```

**Cuando NO escribir ADR:**
- Cuando es una implementacion obvia (ej: "usar FastAPI para el endpoint REST")
- Cuando es una decision reversible en 5 minutos
- Cuando la alternativa descartada no tiene sentido real
- La linea roja: si no podrias explicar la decision en una entrevista sin preparacion, no es ADR

**Cuando ACTUALIZAR un ADR existente:**
- Cuando cambia la decision original (nuevo ADR que depreca el anterior)
- Cuando aparece una alternativa que no se considero y cambia el balance
- Cuando el contexto cambia sustancialmente (nuevo requisito, nuevo stack)

### 5.10 DDD-001: El documento que las consolida

Todas las ADRs anteriores estan consolidadas en `docs/adr/DDD-001-arquitectura.md`. Es el documento de referencia para cualquier decision arquitectonica del proyecto.

---

# 6. FLUJO DE DESARROLLO COMPLETO

### 6.1 El ciclo: Idea → Archivo

```
IDEA → DISCUSIÓN → PROPUESTA → SPEC → TASKS → IMPLEMENTACIÓN → PR → CI → VERIFY → ARCHIVE
  TÚ    TÚ + IA    IA         TÚ     IA      IA + REVISIÓN    TÚ   AUTO  IA       IA
```

Cada cambio sigue este ciclo. No se salta pasos.

### 6.2 SDD: Spec-Driven Development

SDD significa que **primero se escribe la especificación, después el código**. El flujo exacto:

1. **`/sdd-new <change>`** — Arrancas un cambio nuevo. La IA explora el codebase, te hace preguntas de negocio, y escribe una propuesta.
2. **Propuesta** — La IA te pregunta sobre el problema, las reglas de negocio, casos edge, alcance. Tú respondes, la IA refina.
3. **Spec** — La IA escribe la especificación detallada con Given/When/Then.
4. **Design** — La IA propone la arquitectura técnica.
5. **Tasks** — La IA divide la spec en tareas atómicas, cada una completable en una sesión.
6. **Apply** — La IA implementa las tasks una por una, con tests primero (TDD).
7. **Verify** — La IA verifica que la implementación cumple la spec.
8. **Archive** — Se cierra el cambio y se persisten los artefactos.

**Strict TDD:** Cuando el proyecto soporta tests, el modo Strict TDD está activo. Esto significa que la IA escribe el test ANTES del código de producción. No hay código sin test que lo valide.

### 6.3 Git: branches, commits, PRs

**Convención de ramas:**

| Tipo | Prefijo | Ejemplo |
|---|---|---|
| Nueva funcionalidad | `feat/` | `feat/prediction-endpoint` |
| Corrección | `fix/` | `fix/null-model-id` |
| Documentación | `docs/` | `docs/adr-001-choice` |
| Infraestructura | `infra/` | `infra/add-prometheus` |

**Flujo diario:**

```bash
git pull origin main                    # Sincronizar
git checkout -b feat/nombre-feature     # Crear rama
# ... trabajar ...
git add -p                              # Añadir cambios selectivamente
git commit -m "feat: descripción"       # Conventional commit
git push origin feat/nombre-feature     # Subir rama
gh pr create --fill                     # Crear PR
```

**Reglas de commits:**
- Usar **conventional commits**: `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`, `ci:`, `infra:`
- Un commit = una unidad lógica. No commits gigantes.
- El mensaje explica QUÉ y POR QUÉ, no CÓMO (para eso está el código)

**Reglas de PRs:**
- Título = mismo formato que commit
- Descripción: qué cambia, por qué, cómo testear
- Si el diff > 400 líneas → considerar dividir en PRs más chicos
- No mergees sin CI verde

### 6.4 CI/CD: GitHub Actions

Cuando creas un PR, GitHub Actions corre automáticamente:

1. **Ruff check** — linter
2. **Ruff format --check** — formateo
3. **Mypy src/** — type checker
4. **Pytest tests/ --cov=src --cov-report=term-missing** — tests + cobertura (>70%)
5. **Construcción de imagen Docker** (solo en push a main)
6. **Deploy a Fly.io** (solo en push a main)

Si algo falla → fix → commit → push → CI corre de nuevo.

### 6.5 Revisión y merge

Cuando CI está verde:

```bash
gh pr merge --squash --delete-branch
```

`--squash` aplasta todos los commits del branch en uno solo al mergear a main. Así main tiene commits limpios.

---

### 6.6 SDLC — Ciclo de Vida del Software aplicado al proyecto

Cada fase del roadmap (Fase 0, 1, 2, 3) es un ciclo completo de SDLC con estas etapas:

```
PLANIFICACIÓN → DISEÑO → IMPLEMENTACIÓN → TESTING → DESPLIEGUE → MONITORIZACIÓN → REVISIÓN
      ↑                                                                                  |
      └──────────────────────────────────────────────────────────────────────────────────┘
```

#### 6.6.1 PLANIFICACIÓN

**Qué se hace aquí:**
- Definir exactamente qué se construye en las próximas 2 semanas (no más)
- Abrir los Issues en GitHub con la descripción del trabajo
- Priorizar en el Project Board
- Estimar el esfuerzo en horas reales (no "lo hago el fin de semana")

**Señal de que lo estás haciendo bien:** Sabes exactamente qué vas a hacer el próximo sábado antes de sentarte a trabajar.

**Señal de que lo estás haciendo mal:** Abres el editor el sábado y decides qué hacer en ese momento.

#### 6.6.2 DISEÑO

**Qué se hace aquí:**
- Definir la arquitectura de la feature antes de escribir código
- Escribir el ADR si la decisión es relevante
- Diseñar el schema de BBDD si aplica
- Diseñar los contratos de la API (qué endpoints, qué request/response) antes de implementarlos
- Diagramar el flujo si es complejo (Mermaid o Excalidraw)

**Señal de que lo estás haciendo bien:** Cuando empiezas a codificar, ya sabes exactamente qué interfaces vas a crear.

**Señal de que lo estás haciendo mal:** Disennas mientras codificas y refactorizas tres veces la misma cosa.

#### 6.6.3 IMPLEMENTACIÓN

**Qué se hace aquí:**
- Crear una rama desde `main`: `feat/model-registry-api` o `fix/connection-pool-timeout`
- Escribir código en incrementos pequeños y coherentes
- Hacer commits frecuentes (cada bloque lógico completo, no al final del día)
- Seguir Conventional Commits en cada commit

**Por qué `git add -p` y no `git add .`:** Te fuerza a revisar cada cambio antes de commitarlo. Detectas errores, archivos de debug olvidados y cambios no relacionados que deberían ir en otro commit. Es el hábito más infravalorado de Git.

#### 6.6.4 TESTING

**Antes de abrir cualquier PR, estos checks deben pasar:**

| Tipo | Qué valida | Tiempo |
|---|---|---|
| **Unitarios** | Lógica de negocio aislada, sin BD ni servicios externos | < 1s |
| **Integración** | Componentes funcionando juntos: API contra BD real | < 5s |
| **Coverage** | Porcentaje del código cubierto (mínimo 70%) | — |

**Qué testear y qué no:**
- ✅ Lógica de negocio, validaciones, manejo de errores, transformaciones de datos
- ❌ Código de frameworks (FastAPI ya está testeado), getters/setters triviales, código de terceros

**Estructura de un test bien escrito:**
- **Arrange:** Prepara el estado inicial (datos, mocks)
- **Act:** Ejecuta la acción que se testea
- **Assert:** Verifica el resultado esperado
- **Cleanup:** Limpia el estado (fixtures de pytest lo hacen automáticamente)

#### 6.6.5 DESPLIEGUE

El despliegue nunca es manual. Desde la Fase 1, todo deploy se hace a través del pipeline de CI/CD.

| Entorno | Cómo se despliega | Dónde |
|---|---|---|
| **Local** | `just start` | Docker Compose local |
| **Production** | Merge a `main` + CI verde | Fly.io / Hetzner VPS |

#### 6.6.6 GESTIÓN DEL PROYECTO — GitHub Projects

Configurá un tablero Kanban en GitHub Projects con estas columnas:

| Columna | Qué contiene |
|---|---|
| **Icebox** | Ideas sin priorizar, cosas para el futuro |
| **Backlog** | Issues priorizados, listos para ser trabajados |
| **In Progress** | Lo que estás haciendo ahora (máximo 2 items) |
| **In Review** | PR abierto, esperando merge |
| **Done** | Completado y mergeado |

**Regla:** Máximo 2 items en "In Progress" al mismo tiempo. Si hay 3, algo está bloqueado. Desbloquealo antes de empezar algo nuevo.

**Cómo convertir el roadmap en Issues:**
- Cada checkpoint del roadmap es un milestone en GitHub
- Cada tarea concreta dentro de un checkpoint es un Issue
- Cada Issue tiene: descripción clara, criterios de aceptación (cómo sabes que está hecho), estimación en horas

#### 6.6.7 REVISIÓN SEMANAL

**Protocolo de fin de semana (sábado después de codificar):**

1. Commit de todo lo que esté funcional (aunque no esté terminado)
2. Push de la rama
3. Actualizar el Project Board
4. Anotar en el Issue qué quedó pendiente y cuál es el siguiente paso

**Protocolo de inicio de semana (antes de codificar):**
1. `git pull origin main` — sincronizar
2. Revisar el Project Board: ¿qué está en "In Progress"?
3. Crear la rama del Issue que vas a trabajar
4. Empezar a codificar

#### 6.6.8 Memory Bank — El contexto de la IA

Para que la IA tenga contexto continuo entre sesiones, existen estos archivos en `docs/context/`:

| Archivo | Qué contiene | Quién lo actualiza | Frecuencia |
|---|---|---|---|
| `architecture.md` | Diagrama de arquitectura, decisiones clave, estructura del proyecto | IA (cuando cambia algo) | Por cambio arquitectónico |
| `conventions.md` | Convenciones de código, nombres, estilos | IA + Tú | Cuando se establece una nueva convención |
| `current-state.md` | Estado actual del proyecto, qué está hecho y qué falta | IA (después de cada cambio) | Después de cada sesión |
| `active-context.md` | En qué estás trabajando ahora, qué obstáculos tienes, cuál es el siguiente paso | IA | Cada vez que cambias de tarea |

El **README.md** es la entrada al Memory Bank. Debe contener:
```markdown
# Zenith-ops

> Repositorio para documentar el estado actual del proyecto.

## Stack
Python 3.12, FastAPI, SQLAlchemy async, Pydantic v2, Pytest, UV, Ruff, Mypy

## Estado actual
Ver [docs/context/current-state.md](docs/context/current-state.md)

## Arquitectura
Ver [docs/context/architecture.md](docs/context/architecture.md)

## Convenciones
Ver [docs/context/conventions.md](docs/context/conventions.md)

## Contexto activo
Ver [docs/context/active-context.md](docs/context/active-context.md)
```

**Templates para cada archivo:**

**`architecture.md`** — no describas el código, describe el mapa:
```markdown
# Arquitectura de Zenith-ops

## Principios arquitectónicos
- Separación estricta api/core/db
- Async en toda la capa de I/O
- Testabilidad como requisito, no como lujo

## Estructura del proyecto
src/zenith_ops/
  api/v1/        ← Capa de entrada (routers, schemas, dependencias)
  core/          ← Capa de dominio (registry, settings, excepciones)
  db/            ← Capa de datos (ORM SQLAlchemy; sin migraciones)
  services/      ← Servicios de aplicación (inferencia)
src/db/migrations/  ← Alembic (separado del ORM)

## Decisiones clave (resumen de ADRs)
- ADR-001: PostgreSQL para Model Registry → integridad referencial + JSONB
- ADR-002: Monolito modular → microservicios solo cuando escalen
- ADR-003: Drift detection en Fase 2 → no en MVP
```

**`conventions.md`** — el archivo que evita que tengas que pensarlo dos veces:
```markdown
# Convenciones

## Python
- type hints obligatorios en toda función pública
- docstrings solo si la lógica no es obvia
- Pydantic v2 para schemas de entrada/salida
- SQLAlchemy 2.0 style (no legacy query API)

## Git
- Conventional Commits: feat:, fix:, docs:, refactor:, test:, chore:
- Ramas: desde el Issue de GitHub
- PRs: squash merge a main

## Tests
- pytest con fixtures para infraestructura
- tests unitarios + tests de integración
- cobertura mínima: 80%
```

**`current-state.md`** — un snapshot que responde "¿qué pasó la última vez?"
```markdown
# Estado actual

## Última sesión: [YYYY-MM-DD]
- Avanzamos [feature X] hasta [punto Y]
- Quedó pendiente [problema Z]
- Próximo paso: [acción concreta]

## Features completadas
- [ ] Model Registry CRUD
- [ ] Endpoint predict /v1/models/{model_name}/predict
- [ ] Health checks liveness + readiness

## Features en progreso
- [ ] CI/CD pipeline (Issue #NN)
- [ ] Fly.io deploy (Issue #NN)

## Próximos pasos
1. Terminar CI/CD
2. Desplegar en Fly.io
3. Empezar Fase 2
```

**`active-context.md`** — el archivo que la IA debería leer primero cada sesión:
```markdown
# Contexto activo

## Tarea actual
- Issue: #NN — [título]
- Rama: feat/nombre-cambio
- Estado: spec aprobada, empezando implementación

## Obstáculos conocidos
- [El test de integración falla porque la BD no arranca limpia]

## Siguiente acción atómica
1. [Archivo X] — agregar el endpoint POST
2. [Archivo Y] — conectar con el servicio
3. Correr tests

## Notas
- [Cualquier cosa que la IA deba saber antes de tocar código]
```

**Reglas del Memory Bank:**
1. Si un archivo no existe, la IA pregunta si debe crearlo. **No lo crees sin preguntar.**
2. `current-state.md` se actualiza al final de cada sesión
3. `active-context.md` se actualiza cada vez que cambias de tarea
4. `architecture.md` solo se actualiza cuando la arquitectura cambia, no por cada commit
5. El README es el índice — todo lo demás es detalle

---

### 6.7 Template de Spec (para features nuevas)

Cada feature nueva necesita una Spec antes de codificar. Este es el template que se usa:

```markdown
# SPEC-NNN: [Nombre de la feature]

**Estado:** Borrador | En revisión | Aprobada | Implementada
**Issue:** #[número]
**ADR relacionado:** ADR-NNN (si aplica)
**Dependencias:** SPEC-NNN (specs que deben estar implementadas antes)

---

## Contexto

[Qué existe ahora. Qué problema resuelve esta feature.
Qué partes del sistema toca. 2–4 frases.]

---

## Comportamiento esperado

### Input
[Tipos exactos, restricciones]

### Output
[Tipos exactos, formato]

### Casos de error
| Caso | Código HTTP | Respuesta |
|---|---|---|
| [caso] | [código] | [respuesta] |

---

## Contrato de API (si aplica)

**Método:** GET | POST | PUT | DELETE
**Endpoint:** /v1/[ruta]

**Request body:**
```json
{
  "campo": "tipo y descripción"
}
```

**Response (200):**
```json
{
  "campo": "tipo y descripción"
}
```

**Errores:**
```json
{"error": "código", "message": "descripción", "detail": {}}
```

---

## Schema de Base de Datos (si aplica)

[Tablas nuevas o modificadas. Columnas, tipos, constraints.]

---

## Reglas de negocio

1. [Regla 1 — verificable]
2. [Regla 2 — verificable]

---

## Criterios de aceptación (binarios)

- [ ] [Criterio 1 — con valores concretos]
- [ ] [Tests pasan]
- [ ] [Lint pasa]
- [ ] [Coverage > 70%]

---

## Fuera de scope

- No incluye [X]
- No modifica [Y]
- [Z] se implementa en SPEC-MMM


---

# 7. FASES DEL PROYECTO (CON ESTADO REAL)

### 7.1 FASE 0 — Setup y fundamentos ✅ COMPLETADA

**Duración:** Semanas 1–3 (en la práctica, se completó como parte del setup inicial)

**Objetivo:** Dominar Python como lenguaje principal, configurar el entorno, tener el repo en GitHub con estructura y CI verde.

**Checklist completado:**
- [x] WSL2 + Ubuntu 24.04
- [x] Zsh + Oh My Zsh + Starship
- [x] UV como gestor de Python
- [x] Git con SSH key en GitHub
- [x] Estructura de carpetas del proyecto
- [x] `pyproject.toml` con Ruff, Mypy, Pytest
- [x] `Justfile` funcional
- [x] Pre-commit hooks configurados
- [x] CI/CD pipeline verde (Ruff + Mypy + Pytest)
- [x] Primer commit + PR mergeado

---

### 7.2 FASE 1 — MVP: API + Model Registry 🔧 EN PROGRESO

**Duración:** Semanas 4–10 · ~50h totales

**Objetivo:** API en producción real con CI/CD, tests y documentación completa.

#### Estructura BD planificada para Fase 1

La Fase 1 tiene **2 tablas** en PostgreSQL (checkpoint). `health_checks` queda para Fase 1.5+ (ver nota en checkpoint).

**Tabla 1: `model_registry`**
```sql
CREATE TABLE model_registry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    version VARCHAR(50) NOT NULL,
    framework VARCHAR(50) NOT NULL,
    artifact_path TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'staging',
    metrics JSONB,
    created_at TIMESTAMPTZ DEFAULT now(),
    deployed_at TIMESTAMPTZ,
    UNIQUE (name, version)
);
```

**Tabla 2: `prediction_metadata`**
```sql
CREATE TABLE prediction_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id UUID NOT NULL UNIQUE,
    model_id UUID NOT NULL,
    status VARCHAR(20),
    error_message TEXT,
    latency_ms INT,
    created_at TIMESTAMPTZ DEFAULT now(),
    FOREIGN KEY (model_id) REFERENCES model_registry(id)
);
```

**Tabla 3: `health_checks`** *(Fase 1.5+ — no blocker de checkpoint)*

```sql
CREATE TABLE health_checks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    check_type VARCHAR(50),
    status VARCHAR(20),
    error_message TEXT,
    checked_at TIMESTAMPTZ DEFAULT now()
);
```

---

#### Semana 4–5 — Model Serving API (v0.1)

**Presupuesto:** 20h · **Estado:** 2/6 completado

| Issue | Estado |
|-------|--------|
| feat: health check endpoints (live + ready) | ✅ #13 |
| feat: prediction endpoint v1 | ✅ #16 |
| feat: structured logging with correlation IDs | ⬜ #11 |
| feat: global error handling middleware | ⬜ |
| test: unit tests for prediction logic | ⬜ |
| docs: ADR-001 — logging library choice | ⬜ |

**Qué ya está implementado:**

- `POST /v1/predict` con validación Pydantic → 422 si campos inválidos, idempotency key opcional
- `GET /health/live` → 200 sin depender de nada
- `GET /health/ready` → 200 solo si BBDD responde + modelo cargado

**Lo que falta:**

- **Structured logging:** correlation_id UUID por request, formato JSON, log de cada request con model_id + latency + status
- **Error handling middleware:** global try/except que devuelva JSON consistente, no stacktraces
- **Unit tests de predicción:** probar la lógica de negocio sin levantar la API
- **ADR-001:** documentar qué logger se usa y por qué

**Verificación:**
```bash
just start
http POST localhost:8000/v1/predict model_id="test-model" features:='{"f1": 1.0}'
http localhost:8000/health/ready
http localhost:8000/health/live
```

#### Semana 6–7 — Model Registry en PostgreSQL (v0.2)

**Presupuesto:** 20h · **Estado:** 0/6 pendiente

| Issue | Estado |
|-------|--------|
| feat: database connection (SQLAlchemy async + connection pool) | ⬜ |
| feat: model registry table + Alembic migration | ⬜ |
| feat: CRUD endpoints for model registry | ⬜ |
| feat: activate/deactivate model version endpoint | ⬜ |
| test: integration tests for registry (against real PostgreSQL) | ⬜ |
| docs: ADR-002 — database schema decisions | ⬜ |

**Decisiones de diseño a documentar en ADR-002:**
- ¿UUID o serial integer como PK?
- ¿Versionado semver string vs entero incremental?
- ¿Status como enum de PostgreSQL o string con CHECK?
- ¿Métricas en JSONB o columnas separadas?

**Tests de integración:** contra PostgreSQL real. Docker Compose en local, servicio de GitHub Actions en CI. Sin mocks ni SQLite.

#### Semana 8–9 — CI/CD con GitHub Actions

**Presupuesto:** 12h · **Estado:** 1/6 completado

| Issue | Estado |
|-------|--------|
| ci: quality pipeline (lint + type-check) for all pushes | ✅ |
| ci: test pipeline with postgres service for integration tests | ⬜ |
| ci: Docker build and push to GHCR on main merge | ⬜ |
| ci: deploy to Fly.io on main merge | ⬜ |
| docs: runbook-001 — manual deploy procedure | ⬜ |
| docs: runbook-002 — rollback procedure | ⬜ |

**Pipeline deseado (4 jobs encadenados):**
1. **Quality** — Ruff + Mypy. Si falla → STOP
2. **Tests** — PostgreSQL como servicio, Alembic upgrade, pytest con coverage > 70%
3. **Build** — Docker multi-stage → GHCR (solo en push a main)
4. **Deploy** — `flyctl deploy` (solo en push a main)

**Configurar Fly.io:**
```bash
flyctl launch
# App: mlops-engine | Region: mad | PostgreSQL: no (via Neon)
flyctl auth token
# GitHub repo → Settings → Secrets → FLY_API_TOKEN
```

#### Semana 10 — Dockerfile de producción

**Presupuesto:** 8h · **Estado:** 0/4 pendiente

| Issue | Estado |
|-------|--------|
| infra: production Dockerfile (multi-stage, non-root user) | ⬜ |
| infra: add Sentry error tracking | ⬜ |
| docs: update README with architecture diagram + quick start | ⬜ |
| docs: ADR-003 — containerization strategy | ⬜ |

**El Dockerfile debe tener:**
- **Multi-stage:** builder (UV, dependencias) + runtime (solo .venv y src/). Imagen < 200MB
- **Seguridad:** usuario no-root, envs en runtime nunca en la imagen
- **Caché:** `pyproject.toml` y `uv.lock` antes que `src/` para no invalidar layers de dependencias

**Verificar:**
```bash
just build
docker image ls mlops-engine:local
# SIZE < 200MB
```

---

#### Checkpoint de Fase 1 — todo esto debe estar VERDE antes de pasar a Fase 2

```bash
# Predict endpoint
curl -X POST http://localhost:8000/v1/predict \
  -H "Content-Type: application/json" \
  -d '{"model_id": "iris-classifier", "features": {"sepal_length": 5.1}}'
# → 200

# Registry CRUD
curl -X POST http://localhost:8000/v1/models/register \
  -d '{"name": "test", "version": "0.1.0", "framework": "sklearn", "artifact_path": "..."}'
# → 201

# Health checks
curl http://localhost:8000/health/live   # → 200
curl http://localhost:8000/health/ready  # → 200

# En producción (HTTP en VPS; HTTPS → Fase 1.5+, no blocker)
curl http://167.233.116.195:8000/health/ready  # → 200

# Coverage
uv run pytest tests/ --cov=src --cov-report=term-missing
# TOTAL: >= 70%

# Documentación
ls docs/adr/ | wc -l       # >= 3
ls docs/runbooks/ | wc -l  # >= 2
# README con diagrama de arquitectura y link a API desplegada
```

> **Nota (2026-06-26):** Tabla `health_checks` y HTTPS/TLS están **fuera** del checkpoint de Fase 1 — post-MVP / Fase 1.5+, no blockers para pasar a Fase 2.

---

### 7.3 FASE 2 — MLOps Real 📝 PLANEADA

**Duración:** Semanas 11–20 · ~75h totales · 7-8h/semana

**Objetivo:** Añadir tracking de experimentos, observabilidad completa y detección de drift. Al final de esta fase el proyecto es portfolio de nivel mid/senior real.

**Horas totales:** ~75h · 7-8h/semana

#### Estructura BD Fase 2 — Tablas adicionales

Las 2 tablas de Fase 1 (checkpoint) permanecen sin cambios. Se añaden:

**Tabla 4: `experiments`**
```sql
CREATE TABLE experiments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    status VARCHAR(20),           -- pending | running | completed | failed
    model_id UUID REFERENCES model_registry(id),
    metrics JSONB,                -- {"accuracy": 0.92, "val_loss": 0.15}
    parameters JSONB,             -- {"lr": 0.001, "epochs": 100}
    created_at TIMESTAMPTZ DEFAULT now(),
    completed_at TIMESTAMPTZ
);
CREATE INDEX idx_experiments_status ON experiments(status);
```
> **¿Por qué ahora?** MLflow genera experimentos. Necesitas registrarlos con su estado y métricas.

**Tabla 5: `model_versions`**
```sql
CREATE TABLE model_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_id UUID NOT NULL REFERENCES model_registry(id),
    experiment_id UUID REFERENCES experiments(id),
    mlflow_run_id VARCHAR(255),
    metrics JSONB,
    artifacts_uri TEXT,
    created_at TIMESTAMPTZ
);
```
> **¿Por qué ahora?** Cada entrenamiento crea una versión nueva. MLflow los gestiona, pero registras en BBDD.

**Tabla 6: `prediction_logs`**
```sql
CREATE TABLE prediction_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_id UUID NOT NULL REFERENCES model_registry(id),
    features JSONB NOT NULL,
    prediction FLOAT,
    confidence FLOAT,
    created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_logs_model ON prediction_logs(model_id);
CREATE INDEX idx_logs_created ON prediction_logs(created_at);
```
> **¿Por qué ahora?** Para drift detection necesitas historial de features. En Fase 1 no hay drift, así que no hacía falta.

#### Objetivo 2.1: MLflow Integration (Semanas 11–13)

**Qué hace:**
- Script de entrenamiento registra experimentos en MLflow
- Endpoint de predicción carga modelos desde MLflow registry (no archivo local)
- MLflow corre en Docker Compose con PostgreSQL como backend de metadata

**El flujo completo:**
```
Entrenas un modelo localmente
    → MLflow registra: parámetros, métricas, artefacto (.pkl o .pt)
    → El modelo queda en estado "None" en MLflow

Promueves el modelo a Staging
    → Tu API puede cargarlo y servirlo en modo staging

Promueves el modelo a Production
    → Tu API lo sirve en el endpoint principal
    → La versión anterior queda en "Archived"
```

**Decisiones de diseño a documentar en ADR:**
- ¿El backend de MLflow comparte la misma instancia de PostgreSQL que la API o tiene la suya propia?
- ¿Los artefactos van en un volumen Docker (simple) o en S3/object storage (producción real)?
- ¿Cómo gestiona la API el reload de modelos cuando se promueve una nueva versión?

**Checklist 2.1:**
- [ ] MLflow en docker-compose, accesible en http://localhost:5000
- [ ] Script de entrenamiento registra experimentos (parámetros + métricas + artefacto)
- [ ] API puede cargar modelos desde MLflow registry
- [ ] Transición staging → production funciona
- [ ] Tests unitarios del integración con MLflow
- [ ] ADR-005 documentado

#### Objetivo 2.2: Prometheus + Grafana (Semanas 14–16)

**Qué hace:**
- Endpoint `/metrics` expone métricas de negocio
- Dashboard Grafana con 6 paneles mínimos
- Prometheus scrapea la API cada 15s

**Métricas a exponer:**

| Métrica | Tipo | Qué mide |
|---|---|---|
| `mlops_prediction_requests_total` | Counter | Total de predicciones (por modelo, versión, estado) |
| `mlops_prediction_latency_seconds` | Histogram | Distribución de latencia (P50/P90/P99) |
| `mlops_prediction_confidence` | Histogram | Distribución de confianza de las predicciones |
| `mlops_active_models` | Gauge | Modelos activos en producción |
| `mlops_model_load_time` | Histogram | Tiempo de carga del modelo |
| `mlops_errors_total` | Counter | Tasa de errores por tipo |

**El dashboard de Grafana (6 paneles, en este orden):**

El orden no es estético, es narrativo — cuenta la historia del sistema:

1. **Request Rate** (req/min) — ¿se usa el sistema?
2. **Latency P50/P90/P99** — ¿responde bien?
3. **Error Rate** — ¿hay problemas?
4. **Confidence Distribution** — ¿el modelo está seguro de sus predicciones?
5. **Active Models in Production** — ¿cuántos modelos hay activos?
6. **Inference Throughput** — ¿cuántas predicciones/segundo soporta?

> Exporta el dashboard como JSON y commitealo en `/infra/grafana/dashboards/`. Así el dashboard es reproducible.

**Checklist 2.2:**
- [ ] Endpoint `/metrics` expone al menos 6 métricas
- [ ] Prometheus scrapea correctamente
- [ ] Dashboard Grafana con 6 paneles mostrando datos reales
- [ ] Dashboard exportado como JSON en el repo
- [ ] ADR-006 documentado

#### Objetivo 2.3: Drift Detection (Semanas 17–19)

**Qué hace:**
- Endpoint `/v1/monitoring/drift/{model_id}` calcula drift con Evidently AI
- Detecta cambios en distribución de features (data drift) y predicciones (prediction drift)

**Tipos de drift a detectar:**
- **Data drift:** las distribuciones de las features de entrada cambian respecto al conjunto de entrenamiento
- **Prediction drift:** la distribución de las predicciones cambia (el modelo empieza a dar resultados diferentes para inputs similares)

**Arquitectura del componente:**

Para detectar drift necesitas:
1. **Almacenar los inputs de producción:** cada predicción guarda las features en `prediction_logs`
2. **Datos de referencia:** el dataset de entrenamiento, o las predicciones del primer periodo estable
3. **Job periódico de análisis:** compara la distribución de las últimas N predicciones contra los datos de referencia
4. **Sistema de alertas:** si el drift supera un threshold configurable, genera una alerta

**Decisiones de diseño a documentar:**
- ¿Con qué frecuencia corre el job? (cada hora, cada día, on-demand)
- ¿Cuál es el threshold de drift que dispara una alerta? ¿Es fijo o configurable?
- ¿Cómo se persisten los resultados del análisis de drift? (BBDD, logs, métrica de Prometheus)
- ¿El job corre dentro de la API (como background task) o como un proceso separado?

**Checklist 2.3:**
- [ ] Inputs de predicción se almacenan en `prediction_logs`
- [ ] Endpoint de drift devuelve resultados coherentes
- [ ] Al menos un tipo de drift detectado con datos reales o simulados
- [ ] Documentado en ADR-006

#### Objetivo 2.4: Reentrenamiento Automático (Semana 20)

**Qué hace:**
- GitHub Actions workflow que corre de forma programada (nightly) o es disparado por drift
- Si hay drift: ejecuta el script de entrenamiento, registra el nuevo modelo en MLflow
- Si supera las métricas del modelo actual: promueve automáticamente a producción

**La pregunta de diseño más importante:** ¿Cuándo se debe promover automáticamente un modelo y cuándo requiere aprobación manual?

**Checklist 2.4:**
- [ ] Workflow de reentrenamiento se ha ejecutado al menos una vez
- [ ] Promoción automática documentada con criterios claros
- [ ] Runbook de reentrenamiento escrito

#### PRUEBA DE TRANSICIÓN FASE 2 → FASE 3

```bash
# 1. MLflow tiene 3+ experimentos
curl http://localhost:5000  # UI de MLflow con experimentos visibles

# 2. Grafana dashboard funciona
curl http://localhost:3000  # Login y visualiza 6 paneles

# 3. Drift detection funciona
curl http://localhost:8000/v1/monitoring/drift/iris-classifier
# {"drift_detected": false, "drift_score": 0.05}

# 4. Tests siguen pasando
just test  # Coverage > 70%

# 5. Deploy sigue automático
git push origin main  # CI/CD funciona
```

---

### 7.4 FASE 3 — Infraestructura Completa 📝 PLANEADA

**Duración:** Semanas 21–32 · ~80h totales · 7-8h/semana

**Objetivo:** Todo el sistema corre en Kubernetes con infraestructura declarada como código. Este nivel justifica "MLOps Engineer" en el CV.

#### Objetivo 3.1: Kubernetes + Helm (Semanas 21–26)

**Qué hace:** Stack completo corre en k3s con Helm chart propio.

**Diferencias clave entre Indra y esto:**
- En Indra aplicas manifests existentes. Acá disenas la estructura del chart.
- En Indra el Helm chart lo ha escrito otro. Acá defines los `values.yaml` y los templates.
- En Indra no sabes por qué los recursos tienen esos limits. Acá los calibras tú.

**Decisiones de diseño del Helm chart:**
- ¿Qué configuraciones van en `values.yaml` (sobreescribibles) y cuáles están hardcodeadas?
- ¿Cómo gestionas los secretos? (Kubernetes Secrets, external-secrets-operator)
- ¿Cuántas réplicas en producción y con qué recursos? (CPU/memoria requests y limits)
- ¿Cómo haces el rolling update sin downtime?

**Resource limits — cómo calcularlos:** Desplegá con limits generosos, observa el consumo real en Grafana durante una semana, ajusta a 1.5x el percentil 95 de uso. No adivines.

**Checklist 3.1:**
- [ ] k3s instalado en Hetzner VPS con `kubectl` funcionando
- [ ] Helm chart propio desplegado con al menos 2 réplicas
- [ ] Liveness y readiness probes configuradas (usan `/health/live` y `/health/ready`)
- [ ] HPA configurado y verificado bajo carga (usa `hey` o `k6`)
- [ ] Rolling update funciona sin downtime

#### Objetivo 3.2: Terraform IaC (Semanas 27–28)

**Qué hace:** Toda la infra (VPS, firewall, networking) declarada en código Terraform.

**Principios a aplicar:**
- **State remoto:** en Cloudflare R2 o Backblaze B2 (tier gratuito)
- **Variables para todo:** región, tipo de servidor, IPs permitidas. Nada hardcodeado.
- **Outputs documentados:** IP del servidor, DNS, etc.
- **Módulos separados:** un módulo para el servidor, otro para el firewall, otro para DNS

**La prueba definitiva:** Destruí toda la infra con `terraform destroy`. Ejecuta `terraform apply`. El sistema debe volver a estar operativo en < 15 minutos sin intervención manual.

**Checklist 3.2:**
- [ ] Provider Hetzner configurado
- [ ] `terraform apply` provisiona VPS desde cero
- [ ] State remoto configurado (no en local)
- [ ] Firewall rules como código
- [ ] ADR-007 documentado
- [ ] Verificado: `terraform destroy` + `terraform apply` funciona

#### Objetivo 3.3: Portfolio Final (Semanas 29–32)

**Qué hace:** Documentación completa, video demo, post LinkedIn.

**Actividades por semana:**

**Semana 29 — Documentación:**
- Revisar todos los ADRs: ¿reflejan las decisiones reales?
- Actualizar todos los runbooks con la operativa actual
- Completar el diagrama de arquitectura final

**Semana 30 — MkDocs:**
- Configurar MkDocs Material
- Organizar toda la documentación en un site navegable
- Desplegar en GitHub Pages (gratis, automático con GitHub Actions)

**Semana 31 — Demo y README final:**
- Grabar un video de 5 minutos mostrando el sistema funcionando en vivo
- Guión del video: qué problema resuelve → arquitectura → demo del endpoint de predicción → dashboard de Grafana → drift detection en acción → reentrenamiento automático
- README final: incorpora el video, badges actualizados, arquitectura completa

**Semana 32 — LinkedIn y entrevistas:**
- Publicar un post en LinkedIn describiendo el proyecto (qué problema resuelve, qué decisiones tomaste, qué aprendiste). No un tutorial. Un análisis de ingeniería.
- Preparar 5 situaciones STAR usando el proyecto como referencia

**Checklist 3.3:**
- [ ] Helm chart propio desplegado en k3s con 2+ réplicas
- [ ] Toda la infra reproducible con `terraform apply` desde cero
- [ ] MkDocs site desplegado en GitHub Pages
- [ ] Video demo de 5 minutos publicado y enlazado en README
- [ ] Post de LinkedIn publicado
- [ ] Todos los ADRs revisados y actualizados (mínimo 8)
- [ ] Al menos 4 runbooks completos

#### PRUEBA FINAL FASE 3 (PORTFOLIO COMPLETADO)

```bash
# 1. Terraform construye toda la infra
cd infra/terraform
terraform apply
# En ~10 minutos: VPS, firewall, networking

# 2. Helm deploy
helm upgrade --install mlops-engine ./infra/k8s/helm/mlops-engine
kubectl port-forward svc/mlops-engine 8000:8000
curl http://localhost:8000/health/ready  # 200

# 3. Video demo publicado en README
# 4. Post LinkedIn publicado
# 5. Todos los ADRs actualizados (8+)
# 6. Runbooks completos y verificados
ls -la docs/runbooks/
# deploy.md, rollback.md, drift-response.md, k8s-troubleshooting.md
```

---

### 7.5 Calendario Semanal Recomendado

**Distribución de horas (ideal):**

| Día | Bloque | Actividad | Horas |
|---|---|---|---|
| **Sábado mañana** | 09:00–12:00/13:00 | Proyecto: código, implementación, tests | 3–4h |
| **Domingo mañana** | 09:00–11:00 | Carril B: AWS / Fast.ai / CKAD | 2h |
| **Martes o miércoles noche** | 21:00–22:30 | Proyecto: ADRs, docs, CI/CD, review | 1–2h |
| **Jueves o viernes noche** | 21:00–22:00 | ByteByteGo / revisión de conceptos | 1h |

**Total semanal: 7–9h**

**Reglas de prioridad:**
1. Si solo tienes tiempo para una cosa: es el proyecto
2. El carril B se puede pausar 1–2 semanas. El proyecto, no.
3. Si el sábado no produces código: el domingo va también al proyecto
4. Las noches de semana son para documentación y revisión, no para código nuevo

---

### 7.6 Checkpoints por mes (criterios de honestidad)

**Checkpoint Mes 1 — Semana 4**

| Criterio | Cómo verificarlo |
|---|---|
| Python: endpoint FastAPI tipado con tests en < 45 min | Cronometrarlo de verdad |
| Repositorio en GitHub con estructura completa | Ver el repo públicamente |
| Pre-commit bloqueando commits mal formados | Intentar commitear sin formato |
| CI verde con lint + type check | Ver Actions en GitHub |
| ADR-000 escrito | Ver `/docs/adr/ADR-000-*.md` |

**Checkpoint Mes 3 — Semana 10**

| Criterio | Cómo verificarlo |
|---|---|
| API desplegada en VPS con CI/CD (HTTPS → Fase 1.5+) | Llamar al endpoint desde el móvil |
| CI/CD: falla si falla un test | Romper un test, verificar pipeline |
| Coverage > 70% en `src/` | Badge en README |
| 3 ADRs escritos | Ver `/docs/adr/` |
| Imagen Docker en GHCR < 200MB | Ver Container Registry en GitHub |

**Checkpoint Mes 5 — Semana 20**

| Criterio | Cómo verificarlo |
|---|---|
| MLflow registra experimentos reales | Abrir UI de MLflow en producción |
| Dashboard Grafana con datos reales (no fake) | Hacer predicciones y ver dashboard |
| Drift detection devuelve resultado coherente | Llamar al endpoint |
| Reentrenamiento automático ejecutado 1+ vez | Ver historial en GitHub Actions |

**Checkpoint Mes 8 — Semana 32**

| Criterio | Cómo verificarlo |
|---|---|
| Helm chart propio: destruir y redesplegar en < 10 min | Cronometrarlo |
| Terraform: `terraform destroy` + `apply` restaura todo | Ejecutarlo y verificar |
| MkDocs site accesible en GitHub Pages | Abrir la URL |
| Video demo de 5 min publicado | Ver README |
| 8+ ADRs escritos y actualizados | Ver `/docs/adr/` |

**Señales de alerta — el proyecto está muriendo si:**
- El último commit de código (no docs) tiene más de 2 semanas
- El README no ha cambiado en más de 1 mes
- Tienes más Issues en "In Progress" que en "Done"
- Has estado "planificando" o "investigando" más de 1 semana sin código

**Señales de alerta — el aprendizaje se desconecta si:**
- Llevas más de 3 semanas estudiando sin aplicar nada al repo
- El carril B consume más tiempo que el proyecto
- Tienes notebooks con experimentos que nunca llegan al proyecto

---

### 7.7 Tabla resumen: estado de cada objetivo

| Objetivo | Estado | PRs mergeados | Spec |
|---|---|---|---|
| Fase 0: Setup | ✅ | #1, #2, #3 | — |
| 1.1: POST /v1/predict | ✅ | #16, #17 | SPEC-001 |
| 1.2: Health Checks | ✅ | #13 | SPEC-002 |
| 1.3: Idempotency Key | ✅ | #20 | SPEC-001 |
| 1.4: CI/CD | ✅ | #14, #18 | — |
| 1.5: Model Registry CRUD | 📝 Pendiente | — | — |
| 1.6: Deploy Fly.io | 📝 Pendiente | — | — |
| Fase 2: MLOps | 📝 Planeada | — | — |
| Fase 3: Infraestructura | 📝 Planeada | — | — |

---

# 8. TEORÍA ESENCIAL

### 8.1 ¿Qué es una API REST?

API = **Application Programming Interface**. Es el "menú" del sistema: dices qué quieres y te dan una respuesta. Punto importante: no es el código fuente, no es la base de datos, no es el servidor. Es LA INTERFAZ — la capa que hace de traductora entre el mundo exterior y tu lógica interna.

REST = un **estilo** de diseño, no un estándar ni un protocolo. No existe "REST certificado" (a diferencia de SOAP, que sí es un protocolo estricto). Los principios REST son más bien una filosofía con 6 restricciones:

1. **Cliente-servidor** — separas quien pide (frontend, otro servicio, curl) de quien sirve (tu API)
2. **Stateless** — cada request contiene toda la info necesaria. El servidor no guarda sesión entre requests. Si necesitas sesión, la manejas del lado del cliente (cookies, tokens)
3. **Cacheable** — las respuestas pueden marcarse como cacheadas para evitar pedir lo mismo dos veces
4. **Interfaz uniforme** — los recursos se identifican con URLs, se manipulan con verbos HTTP (GET, POST, PUT, DELETE), y llevan metadatos (headers Content-Type, Accept)
5. **Sistema por capas** — puedes meter proxies, load balancers, caches entre el cliente y el servidor sin que ninguno de los dos lo sepa
6. **Código bajo demanda** (opcional) — el servidor puede mandar código ejecutable al cliente (JS, applets). Casi no se usa.

**En la práctica, del REST teórico solo aplicamos los puntos 1, 2, 4.**

**Cómo se traduce a nuestro proyecto:**

```
Verbo    URL                    Qué hace
POST     /v1/predict            Ejecuta una predicción (crea un resultado nuevo)
GET      /v1/predict/{id}       Obtiene el resultado de una predicción hecha antes
POST     /v1/models             Registra un modelo nuevo
GET      /v1/models             Lista modelos disponibles
GET      /v1/models/{name}      Obtiene detalle de un modelo
```

**¿Qué NO es REST en nuestro proyecto?**
- Usar GET para ejecutar acciones con efectos secundarios (ej: `GET /predict?features=...` → esto es RPC, no REST)
- Usar URLs con verbos incrustados (`/api/getPrediction` en vez de `GET /predictions/{id}`)
- Ignorar códigos de estado HTTP y devolver siempre 200 con un campo `error: true`

**Ejemplo concreto de REST bien hecho:**
```
POST /v1/predict
Body: {"model_id": "iris-classifier", "features": {...}}
→ Response 200: {"prediction_id": "uuid", "result": 0.0, "latency_ms": 12.5}
```

Acá POST crea un recurso (la predicción). El servidor no guarda estado del cliente entre requests. La URL identifica el recurso, no la acción.

**Error común:** pensar que REST es solo "JSON sobre HTTP". No lo es. Si usas siempre POST con un body JSON para TODO, eso es RPC, no REST. No está mal (RPC funciona perfecto), pero no es REST.

**Pregunta de entrevista:** "¿Qué diferencia hay entre REST y RPC?" — Ahora sabes que REST identifica recursos con URLs y usa verbos. RPC llama a funciones. Google Maps API es REST. Slack API es RPC.

### 8.2 ¿Qué es un endpoint?

Un endpoint es una URL específica que acepta requests. Pensalo como un **número de teléfono**: llamas a ese número (haces POST a `/v1/predict`) y alguien del otro lado atiende y te responde.

Cada endpoint es una función Python con un decorador que le dice a FastAPI "cuando alguien llegue a esta URL, ejecuta esto":

```python
@router.get("/health/live")
async def liveness():
    return {"status": "up"}
```

FastAPI se encarga de todo lo que pasa entre que llega la request y se ejecuta tu función:
- Parsear el JSON del body
- Validar los tipos con Pydantic
- Extraer parámetros de la URL, query string, headers
- Serializar la respuesta a JSON
- Setear los headers correctos (Content-Type, CORS, etc.)

**Lo que NO hace FastAPI (y tienes que hacer tú):**
- No gestiona la sesión de base de datos por ti (tienes que abrir/cerrar conexiones)
- No cachea respuestas (salvo que lo configures)
- No maneja autenticación por defecto
- No protege contra ataques (rate limiting, DDoS, inyección)

**La estructura de un endpoint en el proyecto:**

```python
# src/zenith_ops/api/v1/predict.py
from fastapi import APIRouter

from zenith_ops.api.schemas.predict import PredictRequest, PredictResponse
from zenith_ops.services.predictor import InferenceService

router = APIRouter()

@router.post("/v1/predict", status_code=200)
async def predict(request: PredictRequest) -> PredictResponse:
    result, result_type, latency_ms = await InferenceService.predict(
        model_id=request.model_id,
        features=request.features,
        idempotency_key=request.idempotency_key,
    )
    return PredictResponse(
        prediction_id=...,
        model_id=request.model_id,
        result=result,
        result_type=result_type,
        latency_ms=latency_ms,
    )
```

Cada parte importa:
- `"/v1/predict"` en el decorador — después puedes tener `/v2/predict` sin romper `/v1/`
- `PredictRequest` / `PredictResponse` en `zenith_ops/api/schemas/` — contratos Pydantic compartidos
- `InferenceService` en `zenith_ops/services/predictor.py` — classmethods con cache de clase (`_models`); no hace falta instanciar ni inyectar con `Depends` en v0.1

**Error común:** Olvidarse de `await` en una función async. Si llamas a `InferenceService.predict(...)` sin `await`, obtienes una coroutine en lugar del resultado. Y FastAPI te devuelve `RuntimeWarning: coroutine was never awaited`.

**Pregunta de entrevista:** "¿Qué diferencia hay entre un endpoint y un route?" Técnicamente: el route es el mapeo URL → función. El endpoint es la función que ejecuta. Pero en la práctica se usan como sinónimos y está bien.

### 8.3 Async / Await en Python

Esto es **EL concepto** más importante de todo el backend moderno. Si entiendes async de verdad, entiendes cómo funciona FastAPI, cómo funciona Django Channels, cómo funciona Node.js, cómo funciona todo.

FastAPI es **asíncrono**. Esto significa que mientras una request espera a la BD, el servidor puede atender otras requests en lugar de quedarse mirando el techo.

```python
async def predict(request):               # "esta función puede pausarse"
    result = await service.predict(...)    # "pausame hasta que esto termine"
    return result                          # mientras espera, atiende otras requests
```

**Los dos conceptos clave:**

1. **`async def`** — declara que la función puede pausarse en algún punto. No la hace más rápida. No ejecuta en paralelo. Solo le da permiso a Python para interrumpirla cuando encuentre un `await`.

2. **`await`** — el punto donde la función se pausa. "Llamo a esta función async, me quedo esperando, pero mientras tanto el event loop sigue atendiendo a otros". Sin `await`, la función async no se ejecuta — devuelves una `coroutine` (un objeto que promete ejecutarse después).

**¿Qué es el event loop?** Es un "gestor de tareas" que corre en un solo hilo. Su trabajo: cuando una tarea hace `await`, la pausa, mete la siguiente tarea que esté lista, y así sucesivamente. No es paralelismo (no usa múltiples CPUs). Es **concurrencia**: múltiples tareas progresan intercaladas en un solo hilo.

**¿Dónde NO sirve async?** En operaciones de CPU intensiva. Si tu código hace `for i in range(10_000_000): x += 1`, eso NO tiene `await`, NO se pausa, y mientras corre, el event loop se congela. Ahí necesitas `multiprocessing` o `run_in_executor`.

**El caso del modelo ML:**

El `model.predict()` del modelo ML es una operación sincrónica que puede tardar (especialmente si el modelo es grande o los datos son complejos).

```python
# Esto congela el servidor:
async def predict(request):
    result = model.predict(features)  # ← BLOQUEA el event loop por segundos
    return result
```

Por eso usamos `run_in_executor()`:
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

_executor = ThreadPoolExecutor(max_workers=4)

async def predict(request):
    loop = asyncio.get_running_loop()
    # Ejecuta model.predict en un hilo separado, lo espera con await
    result = await loop.run_in_executor(_executor, model.predict, features)
    return result
```

Esto mueve `model.predict()` a un hilo del pool. Mientras el hilo calcula, el event loop principal sigue atendiendo otras requests. No es paralelismo real para la inferencia (sigue en un hilo), pero al menos el servidor no se congela.

**Los límites del `run_in_executor`:**
- No puedes cancelar la operación una vez que arrancó (a menos que cooperes)
- Los hilos comparten el GIL (Global Interpreter Lock). Para ML puro (NumPy, scikit-learn) funciona porque liberan el GIL. Para Python puro, no gana nada.
- `max_workers=4` significa que NO ejecutas más de 4 inferencias en paralelo. La 5ta espera. Es intencional para no saturar la CPU.

**Por qué `time.monotonic()` para medir latencia:**
```python
import time

start = time.monotonic()  # ← time.monotonic(), NO time.time()
result = await service.predict(request)
latency = time.monotonic() - start
```

`time.time()` puede saltar hacia adelante o atrás si el sistema ajusta el reloj (NTP, cambio de hora). `time.monotonic()` cuenta segundos reales desde un punto arbitrario y nunca retrocede. Para medir rendimiento, siempre usa `monotonic`.

**Error común: mezclar async con blocking I/O**
```python
# MUY MAL — bloquea el event loop:
async def get_model():
    with open("model.joblib", "rb") as f:  # ← I/O bloqueante
        data = f.read()                     # ← congela el servidor
    return data
```

El `open()` y `f.read()` son I/O **bloqueante**. Si estás en una función async y necesitas leer archivos, usa `aiofiles` o `run_in_executor`. Sino, estás anulando el beneficio de async.

**Analogía del camarero (completa):**

Imagínate un camarero (el servidor). Sin async, el camarero toma tu pedido, se queda parado en la cocina esperando a que la comida esté lista, y mientras tanto IGNORA a todos los demás clientes. Con async, el camarero toma tu pedido, lo pasa a la cocina, y mientras la cocina trabaja, atiende a otros clientes. Cuando la comida está lista, la lleva a tu mesa.

El `run_in_executor` es como mandar el plato a una cocina secundaria con 4 cocineros. El camarero principal (event loop) no cocina — solo reparte platos entre las cocinas y los clientes.

**Pregunta de entrevista:** "¿Cuál es la diferencia entre concurrencia y paralelismo?" — Concurrencia: varias tareas progresan intercaladas en un hilo (async). Paralelismo: varias tareas se ejecutan SIMULTÁNEAMENTE en múltiples hilos/núcleos (multiprocessing, threading para CPU). La concurrencia NO hace que tu código corra más rápido. Hace que ESPERE de manera más eficiente.

### 8.4 Pydantic y validación de datos

Pydantic v2 es la biblioteca que define **la forma de los datos** en tu API. Cada request, cada response, cada configuración del sistema pasa por Pydantic. Entenderlo bien te ahorra errores en runtime.

**Un schema de Pydantic declara CONTRATO:**

```python
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime

class PredictRequest(BaseModel):
    model_id: str                                          # obligatorio, tipo string
    features: dict[str, float]                             # obligatorio, dict string→float
    idempotency_key: str | None = None                     # opcional, default None
```

Cada campo es una declaración:
- `model_id: str` — si mandan un número, Pydantic lo rechaza
- `features: dict[str, float]` — si mandan `{"color": "red"}`, Pydantic rechaza porque "red" es string, no float
- `idempotency_key: str | None = None` — no es obligatorio, pero si lo mandan, debe ser string

**Lo que Pydantic valida por ti AUTOMÁTICAMENTE:**
- Tipos (int, float, str, bool, UUID, datetime, ...)
- Anidación (schemas dentro de schemas)
- Optional / Nullable (`str | None`)
- Listas, dicts, sets con tipos genéricos (`list[str]`, `dict[str, float]`)
- Enums (campos que solo aceptan ciertos valores)
- Regex (si usas `Field(pattern=r"...")`)
- Rangos numéricos (si usas `Field(ge=0, le=100)`)
- Longitud de strings (si usas `Field(min_length=1, max_length=100)`)

**Validaciones más detalladas con `Field`:**

```python
from pydantic import BaseModel, Field

class PredictRequest(BaseModel):
    model_id: str = Field(
        min_length=1,
        max_length=100,
        pattern=r"^[a-z0-9-]+$",        # solo minúsculas, números y guiones
        examples=["iris-classifier"],    # para la documentación de Swagger
        description="ID único del modelo"
    )
    features: dict[str, float] = Field(
        min_length=1,                    # al menos 1 feature
        description="Features de entrada"
    )
```

Si mandan `model_id: ""` (vacio), Pydantic dice: `"String should have at least 1 character"`. Si mandan `model_id: "Modelo #1"`, Pydantic dice: `"String should match pattern '^[a-z0-9-]+$'"`.

**El error 422 — cómo leerlo:**

Cuando Pydantic rechaza datos, FastAPI devuelve 422 automáticamente. El body del error dice EXACTAMENTE qué pasó:

```json
{
  "detail": [
    {
      "type": "float_parsing",
      "loc": ["body", "features", "color"],
      "msg": "Input should be a valid number, unable to parse string as a number",
      "input": "red"
    }
  ]
}
```

- `type`: el tipo de error (`float_parsing`, `missing`, `string_pattern_mismatch`, etc.)
- `loc`: dónde está el error (`body` → `features` → `color`)
- `msg`: explicación legible
- `input`: qué mandaron (útil para depuración)

**Model Config — comportamientos globales:**

```python
class ModelResponse(BaseModel):
    model_config = {
        "from_attributes": True,     # permite crear desde objetos SQLAlchemy
        "json_schema_extra": {       # metadatos para Swagger
            "example": {
                "name": "iris-classifier",
                "version": "1.0.0"
            }
        }
    }
    name: str
    version: str
```

`from_attributes=True` es CLAVE para devolver datos de BD. Sin esto, no podrías hacer `ModelResponse.model_validate(db_model)`.

**Validadores custom — cuándo y cómo:**

A veces necesitas validaciones que van más allá de tipos. Pydantic v2 ofrece `@field_validator` y `@model_validator`:

```python
from pydantic import BaseModel, field_validator

class PredictRequest(BaseModel):
    model_id: str
    features: dict[str, float]

    @field_validator("features")
    @classmethod
    def validate_features_not_empty(cls, v: dict[str, float]) -> dict[str, float]:
        if len(v) == 0:
            raise ValueError("features dict cannot be empty")
        return v

    @field_validator("model_id")
    @classmethod
    def validate_model_id(cls, v: str) -> str:
        v = v.strip().lower()
        if " " in v:
            raise ValueError("model_id must not contain spaces")
        return v
```

Estos validadores corren DESPUÉS de la validación de tipos. Si `model_id` no es string, ni siquiera llegan al validador.

**Diferencia clave Pydantic v1 vs v2:**
- En v1 los validadores se escribían con `@validator` (ya no existe)
- En v2 los validadores son `@field_validator` y deben ser `@classmethod`
- En v2 el rendimiento es 5-10x mejor (está escrito en Rust)
- En v2 hay `model_config` en vez de `Config` class anidada

**Error común: confundir validación con coerción:**
```python
# Pydantic puede COERCIÓNAR tipos (convertir automáticamente):
class Example(BaseModel):
    count: int

Example(count="42")  # → count=42 (Pydantic convirtió el string a int)
```

Esto es útil pero PELIGROSO. Si quieres rechazar coerciones, usas:
```python
class Example(BaseModel):
    model_config = {"coerce_numbers_to_str": False}
    count: int

Example(count="42")  # → Error 422, esperaba int, recibió string
```

**Pregunta de entrevista:** "¿Qué ventajas tiene Pydantic sobre TypeScript types (Zod) o sobre dataclasses de Python?" — Pydantic valida en RUNTIME (no solo en compilación), genera schemas OpenAPI automáticos, maneja serialización/deserialización, y tiene validación anidada. Zod es el equivalente en TypeScript. Las dataclasses de Python no validan nada.

### 8.5 Cache en memoria

**El problema que resuelve:** Cada vez que llega una request de predicción, el servidor necesita el modelo ML en memoria. Si cada request carga el modelo de disco, es lentísimo (un modelo joblib puede pesar 50-500MB). La solución: cargarlo una vez y mantenerlo en memoria para las siguientes requests.

**Cómo se implementó en el proyecto — atributos de clase:**

```python
# src/zenith_ops/services/predictor.py
from functools import lru_cache
from pathlib import Path
import joblib

class InferenceService:
    _models: dict[str, Any] = {}    # ← atributo de CLASE, no de instancia

    @classmethod
    async def load_model(cls, model_id: str) -> Any:
        """Carga un modelo de disco y lo cachea en memoria."""
        if model_id in cls._models:
            logger.debug(f"Model {model_id} found in cache")
            return cls._models[model_id]

        model_path = Path(f"models/{model_id}.joblib")
        if not model_path.exists():
            raise HTTPException(status_code=404, detail=f"Model {model_id} not found")

        loop = asyncio.get_running_loop()
        model = await loop.run_in_executor(None, joblib.load, model_path)
        cls._models[model_id] = model
        return model
```

**¿Por qué atributo de clase y no de instancia?**

```python
# SIN cache (cada instancia carga de nuevo):
service1 = InferenceService()
model = service1.load_model("iris-classifier")  # → carga de disco (2 segundos)

service2 = InferenceService()
model = service2.load_model("iris-classifier")  # → carga de disco OTRA VEZ (2 segundos)

# CON cache (atributo de clase):
# _models se comparte entre TODAS las instancias de InferenceService
service1.load_model("iris-classifier")  # → caché miss → carga de disco
service2.load_model("iris-classifier")  # → caché HIT → instantáneo
```

**¿Qué pasa si dos requests intentan cargar el mismo modelo al mismo tiempo?**

Es el problema de **cache stampede** o **thundering herd**. Request A revisa el cache → no encuentra → empieza a cargar. Request B revisa el cache → no encuentra → empieza a cargar también. Ahora tienes dos cargas simultáneas del mismo modelo.

**Solución en el código actual (no implementada aún — para Fase 2):**

```python
# src/zenith_ops/services/predictor.py
import asyncio

class InferenceService:
    _models: dict[str, Any] = {}
    _loading: dict[str, asyncio.Lock] = {}  # ← lock por modelo

    async def load_model(self, model_id: str) -> Any:
        if model_id in self._models:
            return self._models[model_id]

        if model_id not in self._loading:
            self._loading[model_id] = asyncio.Lock()

        async with self._loading[model_id]:  # ← solo UNO carga, los otros esperan
            # Doble check: otro hilo pudo haberlo cargado mientras esperábamos el lock
            if model_id in self._models:
                return self._models[model_id]

            loop = asyncio.get_running_loop()
            model = await loop.run_in_executor(None, joblib.load, f"models/{model_id}.joblib")
            self._models[model_id] = model
            return model
```

Esto se llama **double-checked locking**. Es el patrón estándar para evitar cache stampede.

**Límites de la cache en memoria:**

| Límite | Riesgo | Solución futura |
|---|---|---|
| No hay límite de tamaño | Memoria infinita si cargas 100 modelos | `@lru_cache(maxsize=10)` o `cachetools.TTLCache` |
| Se pierde al reiniciar el servidor | Los modelos se recargan de disco | Cache persistente: Redis o filesystem |
| No expira automáticamente | El modelo en memoria puede ser viejo | TTL (time-to-live) o versionado |

**Analogía:** La cache en memoria es como tu mochila. Llevas lo que necesitas hoy. Si no cargas el modelo en la mochila, cada vez que lo necesitas tienes que ir al placard (disco). Pero la mochila no es infinita — cuando se llena, algo tiene que salir.

**Pregunta de entrevista:** "¿Cómo harías una cache distribuida que sobreviva a reinicios del servidor?" — Redis es la respuesta estándar. Usas Redis como backend de cache con TTL. El servidor pregunta a Redis antes de cargar de disco. Si Redis se cae, caes de nuevo a disco (degradación controlada).

### 8.6 Idempotencia

**El problema real:**

El cliente llama a `POST /v1/predict`. La request llega al servidor. El servidor ejecuta la inferencia y guarda el resultado. Pero la **respuesta se pierde en la red** (timeout, problema de DNS, el cliente se cayó). El cliente no sabe si su request se procesó o no. Así que **reintenta**.

Sin idempotencia: el servidor ejecuta la inferencia DOS veces → dos resultados distintos (porque los modelos pueden tener componentes aleatorios o data drift) → el cliente recibe dos predicciones para la misma entrada → inconsistencia.

**La solución — idempotency key:**

El cliente genera un UUID único (típicamente UUID v4) antes de la primera llamada y lo envía como `idempotency_key`. Si la llamada falla, reintenta con la **misma key**. El servidor:

1. Si NO conoce la key → ejecuta la inferencia → guarda resultado + key → responde
2. Si SÍ conoce la key → devuelve el resultado guardado SIN ejecutar la inferencia

```
Cliente 1er intento:
  POST /v1/predict {idempotency_key: "abc-123"}
  → servidor: no conoce "abc-123"
  → ejecuta inferencia
  → guarda {"abc-123": {"result": 0.0, "latency_ms": 12.5}}
  → responde 200
  → (respuesta se pierde en la red)

Cliente 2do intento:
  POST /v1/predict {idempotency_key: "abc-123"}
  → servidor: "abc-123" existe
  → devuelve resultado guardado
  → SIN ejecutar inferencia otra vez
```

**¿Dónde se guarda la idempotency key?**

En el proyecto actual v0.1: **cache en memoria** (diccionario con TTL):

```python
from time import monotonic
from dataclasses import dataclass

@dataclass
class IdempotencyRecord:
    result: dict
    created_at: float

class IdempotencyCache:
    def __init__(self, ttl_seconds: int = 3600):
        self._cache: dict[str, IdempotencyRecord] = {}
        self._ttl = ttl_seconds

    def get(self, key: str) -> dict | None:
        record = self._cache.get(key)
        if record is None:
            return None
        # Expirar entradas viejas
        if monotonic() - record.created_at > self._ttl:
            del self._cache[key]
            return None
        return record.result

    def set(self, key: str, result: dict) -> None:
        self._cache[key] = IdempotencyRecord(result, monotonic())
```

**El TTL es importante:**
- Muy corto (< 1 minuto): el cliente no tiene tiempo de reintentar si hay latencia de red
- Muy largo (> 24h): la cache crece innecesariamente
- Valor razonable: 1 hora para predicciones, 24h para operaciones destructivas

**Casos borde de idempotencia:**

| Situación | Qué pasa |
|---|---|
| Misma key, features diferentes | El servidor devuelve el resultado ORIGINAL, no sobreescribe. Si el cliente quiere otra predicción, debe usar otra key. |
| Key expiró, reintento tardío | La cache limpió la entrada. El servidor ejecuta la inferencia de nuevo y guarda con la misma key. El cliente recibe un resultado NUEVO (que puede diferir del original). |
| Dos clientes distintos usan la misma key | El primero que llega ejecuta. El segundo recibe el resultado del primero. No es un bug — es que el cliente debe garantizar keys únicas (UUID). |
| Servidor se reinicia | Toda la cache en memoria se pierde. Los reintentos post-reinicio ejecutan inferencia de nuevo. |

**¿Por qué no usar la BD para idempotencia?**

Es tentador guardar la idempotency key en PostgreSQL. Pero:
- Cada POST haría un INSERT/SELECT a la BD → latencia extra
- Para v0.1 con poca carga, no importa. Para producción, quieres evitar hits a BD
- La solución ideal es Redis + TTL (porque Redis expira solo)

**Analogía:** La idempotency key es como un número de ticket. Cuando entras a un restaurante, te dan un ticket. Si pierdes tu comida y reclamas, muestras el mismo ticket y te dan la misma comida sin tener que cocinarla de nuevo. Sin ticket, el cocinero no sabe si ya cocinó para ti.

**Pregunta de entrevista:** "¿Cómo harías un endpoint POST que sea naturalmente idempotente sin usar idempotency keys?" — Usando UPSERT. Si el recurso tiene un identificador único (ej: `order_id = "ORD-123"`), un `PUT /orders/ORD-123` es idempotente por naturaleza: mandar los mismos datos produce el mismo resultado sin importar cuántas veces se ejecute. POST no es idempotente por definición (crea un recurso nuevo cada vez). PUT sí lo es.

### 8.7 Health checks: liveness vs readiness

**El problema que resuelven:** En producción, los servidores fallan. La BD se cae, el disco se llena, el proceso se cuelga. El orquestador (Kubernetes, Docker Compose, cualquier sistema de orquestación) necesita saber cuándo un servicio está sano y cuándo no. Los health checks son los **latidos del sistema**.

En Kubernetes (y en operaciones en general), hay **dos tipos distintos** de health checks, y confundirlos es uno de los errores más comunes en equipos que arrancan con K8s:

| Check | Pregunta | Si falla |
|---|---|---|
| **Liveness** | ¿El proceso está vivo? | Kubernetes reinicia el pod (force kill + recreate) |
| **Readiness** | ¿El proceso puede recibir tráfico? | Kubernetes NO le manda tráfico (lo saca del Service) |

**¿Por qué dos? Porque "estar vivo" no es lo mismo que "estar listo para trabajar".**

- Una app que arranca y tarda 30 segundos en conectar a la BD: está viva al segundo 1, pero no está lista hasta el 30.
- Un proceso que perdió conexión con la BD pero podría recuperarse: está vivo (el proceso corre), pero no está listo (no puede servir requests).
- Un proceso en deadlock: no está vivo (no responde al liveness), necesita reinicio.

**Nuestros endpoints:**

```python
# src/zenith_ops/api/v1/health.py
from zenith_ops.services.predictor import InferenceService

@router.get("/health/live")
async def liveness():
    """
    Liveness check: responde 200 inmediato.
    NO toca BD, NO toca disco, NO carga modelos.
    Solo verifica que el proceso FastAPI está corriendo.
    """
    return {"status": "up"}

@router.get("/health/ready")
async def readiness():
    """
    Readiness check: verifica que el sistema puede recibir tráfico.
    - ¿PostgreSQL responde?
    - ¿Hay al menos un modelo cargado en InferenceService._models?
    Si algo falla, responde 503.
    """
    db_status = await check_database()       # SELECT 1 vía SQLAlchemy async
    model_cached = bool(InferenceService._models)

    all_ok = db_status == "up" and model_cached
    return JSONResponse(
        content={
            "status": "up" if all_ok else "down",
            "components": {"database": db_status, "model_cached": model_cached},
        },
        status_code=200 if all_ok else 503,
    )
```

**¿Por qué SELECT 1 en la BD?** Porque es la consulta más liviana posible. No toca tablas, no necesita permisos especiales, no bloquea. Verifica que la conexión TCP está viva, que PostgreSQL responde, y que el pool de conexiones del app funciona.

**¿Qué más debería checkear readiness en el futuro?**
- Redis conecta (cuando agreguemos cache externa)
- Espacio en disco disponible (< 90%)
- MLflow responde (cuando esté integrado)
- Versión del modelo en memoria vs versión registrada

**¿Qué NO debe checkear liveness?** NUNCA chequees dependencias externas en liveness. Si PostgreSQL está caído y liveness chequea BD, Kubernetes reinicia el pod. Pero el pod no tiene la culpa — la BD está caída para todos. Ahora tienes un pod reiniciándose en loop sin necesidad.

**Error clásico que vi en producción:**

```python
# MAL: liveness checkeando la BD
@router.get("/health/live")
async def bad_liveness(db: AsyncSession = Depends(get_db)):
    await db.execute(text("SELECT 1"))  # ← Si la BD falla, K8s reinicia el pod
    return {"status": "up"}
```

Cuando la BD se cae por mantenimiento, este health check falla → Kubernetes reinicia todos los pods → ahora todos los pods están reiniciándose sin que la BD esté disponible → el sistema entero colapsa por algo que no es culpa de los pods.

**En la práctica:**
- Liveness: solo verifica que `uvicorn` (o el proceso Python) responde al puerto
- Readiness: verifica todo lo que el servicio necesita para funcionar

**Analogía del semáforo:**
- Liveness: el semáforo existe y tiene electricidad (el proceso está vivo)
- Readiness: el semáforo está en verde y la calle está despejada (puede recibir tráfico)

**Pregunta de entrevista:** "Diseñá un health check para un microservicio que depende de 3 servicios externos. ¿Cómo evitas cascading failures?" — Usas health checks en dos niveles: liveness (solo proceso interno) y readiness (dependencias externas). Si un servicio externo falla pero el proceso puede funcionar en modo degradado, devuelves 200 con `status: "degraded"` y el cliente decide si acepta latencia extra o rechaza la request.

### 8.8 Flujo completo de POST /v1/predict

Este es el **endpoint más importante** del proyecto. Entenderlo entero te da comprensión de cómo funciona el sistema de punta a punta.

**Diagrama temporal completo:**

```
CLIENTE (curl/browser)                     SERVIDOR (FastAPI)
        │                                        │
        │  1. POST /v1/predict                   │
        │     Headers: {Content-Type, Accept}     │
        │     Body: {model_id, features}          │
        │────────────────────────────────────────>│
        │                                        │
        │                             2. MIDDLEWARE: CORS, Logging
        │                             3. ROUTER: coincide con /v1/predict
        │                                        │
        │                             4. ROUTER resuelve el endpoint
        │                               InferenceService: cache a nivel de clase
        │                                        │
        │                             5. PYDNATIC VALIDA (request)
        │                               ✔ model_id: str
        │                               ✔ features: dict[str, float]
        │                               ✔ idempotency_key: str | None
        │                               ✗ Si inválido → 422 inmediato
        │                                        │
        │                             6. ¿idempotency_key existe?
        │                               cache.get(idempotency_key)
        │                               Sí → responde 200 con cache
        │                                        │
        │                             7. INFERENCE SERVICE
        │                               7a. Buscar modelo en _models cache
        │                                 Miss → load_model()
        │                                   loop.run_in_executor(joblib.load)
        │                                 Hit → usar modelo en memoria
        │                                        │
        │                               7b. Ejecutar model.predict(features)
        │                                 loop.run_in_executor(pool, model.predict, features)
        │                                 Timeout: 5 segundos
        │                                 ⏱️ time.monotonic() mide latencia
        │                                        │
        │                             8. GUARDAR en idempotency cache
        │                               cache.set(key, result, ttl=3600)
        │                                        │
        │                             9. MIDDLEWARE: Log latency
        │                                        │
        │  10. Response 200                      │
        │      {prediction_id, result,            │
        │       result_type, latency_ms}          │
        │<────────────────────────────────────────│
```

**Los detalles que no se ven en el diagrama:**

**Paso 2 — Middleware:**
```python
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.monotonic()
    response = await call_next(request)
    latency = time.monotonic() - start
    logger.info(f"{request.method} {request.url.path} → {response.status_code} ({latency:.3f}s)")
    return response
```
Cada request pasa por este middleware primero. Loggea método, URL, status code y latencia. Sin tener que poner un log en cada endpoint.

**Paso 4 — Servicio de inferencia (classmethod):**
```python
# src/zenith_ops/api/v1/predict.py
from zenith_ops.services.predictor import InferenceService

@router.post("/v1/predict", status_code=200)
async def predict(request: PredictRequest) -> PredictResponse:
    result, result_type, latency_ms = await InferenceService.predict(
        model_id=request.model_id,
        features=request.features,
        idempotency_key=request.idempotency_key,
    )
```

`InferenceService` vive en `zenith_ops/services/predictor.py`. Usa atributos de clase (`_models`, `_idempotency_cache`) compartidos entre todas las requests — equivalente práctico a un singletón sin `Depends`. En fases posteriores, si hace falta inyectar un registry mock en tests, se puede envolver con `Depends`.

**Paso 7b — Timeout en la inferencia:**
```python
import asyncio

async def predict_with_timeout(model, features, timeout=5.0):
    loop = asyncio.get_running_loop()
    try:
        result = await asyncio.wait_for(
            loop.run_in_executor(_executor, model.predict, features),
            timeout=timeout
        )
        return {"result": result, "timed_out": False}
    except asyncio.TimeoutError:
        logger.error(f"Prediction timed out after {timeout}s")
        raise HTTPException(
            status_code=503,
            detail="Prediction timed out"
        )
```

`asyncio.wait_for` envuelve cualquier awaitable con un timeout. Si se pasa el tiempo, lanza `TimeoutError`. Esto evita que un modelo colgado ocupe el thread pool para siempre.

**¿Qué pasaría sin `wait_for`?** Una inferencia que se cuelga (modelo corrupto, bug en feature engineering) ocuparía un slot del thread pool para siempre. Después de 4 requests así, el pool de 4 workers está saturado. Todas las requests nuevas esperan. El servidor parece caído pero no lo está — solo está esperando.

**Paso 9 — ¿Cómo se loggea correctamente?**

```python
import structlog
logger = structlog.get_logger()

# Log estructurado (NO print, NO logging básico)
logger.info("prediction_completed",
    model_id=request.model_id,
    latency_ms=latency_ms,
    idempotent=bool(request.idempotency_key)
)
```

Un log estructurado tiene **campos**, no solo texto. Esto permite filtrar, buscar y hacer métricas sobre los logs. `"prediction_completed"` es un evento, `model_id`, `latency_ms`, `idempotent` son propiedades.

**Pregunta de entrevista:** "Si tuvieras que hacer que este endpoint maneje 1000 requests/segundo, ¿qué cambiarías?" — Respuesta: (1) Cache externa con Redis en vez de memoria local (persistencia entre reinicios), (2) Pool de workers de inferencia más grande con cola de prioridad, (3) Rate limiting por IP, (4) Connection pooling de BD optimizado, (5) Lecturas de BD en réplicas de solo lectura.

### 8.9 Códigos de estado HTTP

Los códigos de estado HTTP son la forma estándar de decirle al cliente qué pasó. No son solo números — cada código tiene un significado específico que el cliente (sea un browser, otro servicio, o curl) entiende sin necesidad de leer el body.

**Los 4 que más vas a ver:**

| Código | Significado | Cuándo lo usamos | En el proyecto |
|---|---|---|---|
| **200** | OK | Todo funcionó correctamente | `POST /v1/predict` → predicción exitosa |
| **201** | Created | Se creó un recurso nuevo | `POST /v1/models` → modelo registrado |
| **404** | Not Found | El recurso pedido no existe | `model_id` inválido, recurso inexistente |
| **422** | Unprocessable Entity | Los datos son inválidos (semánticamente) | Pydantic validation falló |

**Los que verás menos pero importan:**

| Código | Significado | Cuándo lo usamos |
|---|---|---|
| **400** | Bad Request | La request está mal formada (JSON inválido, encoding incorrecto). Diferencia con 422: 400 es error de SINTÁXIS, 422 es error de SEMÁNTICA (los tipos están bien pero los valores no tienen sentido) |
| **409** | Conflict | El recurso ya existe (mismo `name + version` duplicado) |
| **429** | Too Many Requests | Rate limiting — el cliente excedió el límite de requests/minuto. Para Fase 2. |
| **500** | Internal Server Error | Error inesperado del lado del servidor. ALGO explotó y no sabemos qué. |
| **503** | Service Unavailable | El servicio no puede responder AHORA (timeout de inferencia, BD caída, mantenimiento) |
| **502** | Bad Gateway | El servidor actuó como proxy y recibió respuesta inválida del upstream (típico de load balancers) |

**La diferencia entre 404 y 422 (sutil pero importante):**

```python
# 404: el recurso NO existe
GET /v1/models/iris-classifier
→ 404: "Model 'iris-classifier' not found"
# El modelo nunca fue registrado. El error es del modelo, no de la request.

# 422: la request está mal formada
POST /v1/predict
Body: {"model_id": "", "features": {}}
→ 422: "model_id: String should have at least 1 character"
# Los campos están mal. El error es del cliente, la corrección es del cliente.
```

**La diferencia entre 500 y 503 (crítica para depuración):**

```python
# 500: el servidor explotó por algo inesperado
@app.post("/predict")
async def predict():
    raise ValueError("something went wrong")  # ← ERROR DE CÓDIGO
# Esto es un BUG. Hay que fixear el código.

# 503: el servidor no puede responder porque algo EXTERNO falló
@app.get("/health/ready")
async def ready():
    if not database_is_up():
        return JSONResponse(status_code=503, content={"status": "degraded"})
# Esto es una CONDICIÓN OPERACIONAL. La BD se cayó, no el código.
```

Si ves muchos 503, revisa infraestructura (BD, Redis, red). Si ves muchos 500, revisa el código (excepciones no manejadas, bugs).

**Códigos que NO debes usar (aunque veas a otros hacerlo):**

```python
# MAL: siempre 200 con error en el body
return {"status": 200, "error": "something went wrong"}
# Esto obliga al cliente a parsear el body para saber si falló.
# Rompe el contrato HTTP. Los proxies, caches, load balancers no entienden esto.

# BIEN: código HTTP real
raise HTTPException(status_code=404, detail="Model not found")
# El cliente ve 404 inmediato, sin parsear body.
```

**Error común en entrevistas:** "¿Qué código devuelves cuando el cliente no está autenticado?" → 401 (Unauthorized). "¿Y cuando no tiene permisos?" → 403 (Forbidden). 401 = no sé quién sos. 403 = sé quién sos pero no tienes permiso.

### 8.10 ¿Qué es un UUID?

UUID = **Universally Unique Identifier**. Es un identificador de 128 bits que es **prácticamente imposible que se repita**.

Formato: `3fa85f64-5717-4562-b3fc-2c963f66afa6` (8-4-4-4-12 hex, total 36 caracteres)

**Las 4 versiones que más importan:**

| Versión | Cómo se genera | Propiedades | Dónde se usa |
|---|---|---|---|
| **UUID v4** | Aleatorio (122 bits aleatorios + 6 bits de versión) | Máxima entropía, imposible de predecir | `prediction_id`, `idempotency_key` — donde NUNCA quieres colisiones |
| **UUID v7** | Timestamp + aleatorio | Ordenable por tiempo, sin exponer info sensible | Alternativa moderna a v4 cuando necesitas orden cronológico |
| **UUID v1** | MAC address + timestamp | Ordenable PERO expone MAC address y momento exacto | Evitarlo por seguridad |
| **UUID v5** | Hash de namespace + nombre | Determinístico: mismo input → mismo UUID | Identificadores basados en datos (no usado acá) |

**En Python:**

```python
from uuid import uuid4, UUID

# Generar un UUID v4
prediction_id = uuid4()  # → UUID("3fa85f64-5717-4562-b3fc-2c963f66afa6")

# Convertir a string
str(prediction_id)  # → "3fa85f64-5717-4562-b3fc-2c963f66afa6"

# Pydantic acepta UUID automáticamente
class PredictResponse(BaseModel):
    prediction_id: UUID  # ← Pydantic valida que sea UUID válido
```

**¿Qué pasa si dos servidores generan el mismo UUID?**

Probabilidad: ~1 en 5.3 × 10³⁶ (5.3 trillion trillion trillion). Para ponerlo en perspectiva: si generas 1 billón de UUIDs por segundo durante 100 años, la probabilidad de una colisión es ~50%. Para este proyecto, es más probable que te caiga un rayo mientras ganas la lotería.

**¿Por qué UUID y no auto-increment (1, 2, 3)?**

| Auto-increment | UUID |
|---|---|
| Revela cuántos registros tienes (el ID 1000 = 1000 modelos) | No revela información |
| Secuencial: competencia por el próximo ID | Independiente: cada servicio genera el suyo |
| Fácil de adivinar: /v1/predictions/1234 | Imposible de adivinar |
| Requiere una BD central que asigne IDs | Funciona offline, distribuido |
| Compatible con índices B-tree (rápido) | Fragmenta índices (más lento en tablas gigantes) |

**¿Qué usamos acá y por qué?** UUIDs para todo. No tenemos el volumen de datos que justifique optimizar índices (cuando tengas 10 millones de predicciones, reconsideralo). La seguridad y la posibilidad de generar IDs sin consultar la BD pesan más.

**Generación de UUID en PostgreSQL (para la BD):**

```sql
-- PostgreSQL tiene uuid_generate_v4() en la extensión uuid-ossp
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_id VARCHAR(100) NOT NULL,
    result DOUBLE PRECISION,
    latency_ms DOUBLE PRECISION,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

Pero en el código Python generamos los UUIDs del lado de la app (con `uuid4()`) y los mandamos a la BD. Así el control de la generación está en el código, no en la BD.

**Pregunta de entrevista:** "¿Qué pasa si usas UUID como primary key en una tabla de millones de filas?" — Los UUIDs no son secuenciales, así que los inserts fragmentan el índice B-tree (cada nuevo UUID va a una página distinta del índice). Para tablas grandes (>10M filas), esto causa degradación. Soluciones: (1) UUID v7 que es ordenable por tiempo, (2) usar auto-increment como PK interna + UUID como exposed ID, (3) usar `ulid` (lexicográficamente ordenable).

---

# 9. CÓMO TRABAJAR CON LA IA

### 9.1 Roles claros

| Situación | Quién hace |
|---|---|
| Definir qué construir | **VOS** (decides) |
| Responder preguntas de negocio | **VOS** (el que sabe el dominio) |
| Escribir specs / ADRs | **VOS** (con ayuda de la IA) |
| Dividir en tareas | **IA** (mecánico) |
| Git: branch, commit, PR | **VOS** |
| Escribir código | **IA** (guiada por tus specs) |
| Revisar código | **VOS** (validas que cumpla la spec) |
| Tests | **IA** (primero, TDD) |
| CI / Merge | **VOS** |
| Decisiones finales | **VOS** (siempre) |

### 9.2 Cómo pedir cosas

**Mal:** "Hazme el structured logging"

**Bien:** "Quiero structured logging con correlation_id. ¿Qué opciones tengo? ¿Dónde debería vivir? Dame las alternativas con pros/cons para decidir."

**Perfecto:** "He pensado en poner el correlation_id como middleware. ¿Te parece que use `request.state` de Starlette o prefiero un context var? ¿Cuál es la diferencia?"

La diferencia entre "mal" y "bien" es **comprensión del problema**. No hace falta que sepas la respuesta, pero sí que sepas QUÉ estás pidiendo.

### 9.3 Cómo revisar el código que genera la IA

Cuando la IA te pasa código para revisar, preguntate:

1. **¿Entiendo qué hace cada línea?** Si no, pregunta. No sigas.
2. **¿Esto resuelve el problema que definimos?** Si no, no lo mergees.
3. **¿Puedo explicar esta decisión en una entrevista?** Si no, repensala.
4. **¿Hay tests para esto?** Si no, no está terminado.

### 9.4 Cómo saber si estás aprendiendo (señales)

Señales de que **estás aprendiendo**:
- Empiezas a predecir qué va a decir la IA antes de que lo diga
- Lees código y entiendes el flujo sin que te lo expliquen
- Encuentras bugs o problemas antes de que te los marquen
- Puedes explicarle a alguien más lo que hace el proyecto

### 9.5 Señales de que estamos yendo muy rápido

Señales de que **estamos yendo demasiado rápido**:
- No entiendes por qué tomamos cierta decisión técnica
- Sientes que el código es magia negra que "funciona pero no sé cómo"
- No sabrías explicar qué hace `InferenceService._models` sin mirarlo

### 9.6 Qué NO delegar a la IA (nunca)

Hay cosas que la IA hace mal, y si se las delegas, vas a perder tiempo y calidad.

| Tarea | Quién la hace | Por qué no delegarla |
|---|---|---|
| **Diseño de arquitectura** | TÚ | La IA no entiende el contexto de tu carrera, ni qué skills quieres mostrar en una entrevista. El diseño arquitectónico define el portfolio. |
| **Decisiones de stack** | TÚ | La IA tiene sesgo hacia lo que conoce. Si le preguntas "¿qué BD uso?", te va a decir PostgreSQL porque es el default. No porque haya evaluado opciones con TU contexto. |
| **Qué construir (scope)** | TÚ | La IA no sabe cuánto tiempo tienes, qué quieres aprender, ni qué pesa en una entrevista. Siempre va a sugerir "más features". |
| **Revisión final del código** | TÚ | La IA puede generar código que funciona pero no entiendes. Si no entiendes, no puedes mantenerlo, no puedes explicarlo en una entrevista, y no puedes saber si está bien. |
| **Validación de negocio** | TÚ | "¿Esto resuelve el problema que definimos?" solo lo puede responder alguien que entiende el problema original. |
| **Escribir ADRs** | TÚ (con ayuda) | Los ADRs documentan TU razonamiento. Si los escribe la IA, no son tuyos. En una entrevista no vas a poder defenderlos. |
| **Mensajes de commit** | VOS | El mensaje de commit explica QUÉ y POR QUÉ. La IA sabe el QUÉ (porque lo acaba de escribir) pero no el POR QUÉ (contexto de decisión). |

**Señales de que estás sobredelegando:**
- La IA te pregunta algo y le dices "haz lo que creas mejor"
- Mergeas código que no entiendes del todo
- No sabrías replicar una decisión técnica sin la IA
- El archivo `.gitignore` lo escribió la IA (y no sabes por qué están esas entradas)

### 9.7 Flujo SDD con IA — Paso a paso

Este es el flujo exacto para cada cambio:

1. **Discusión (TÚ + IA):** Hablas del problema. La IA te pregunta sobre reglas de negocio, casos edge, alcance. Sin código todavía.

2. **Propuesta (IA):** La IA escribe una propuesta con: qué se construye, por qué, qué no entra. La lees y la apruebas (o pides cambios).

3. **Spec (IA + TÚ):** La IA escribe la Spec detallada con Given/When/Then. Tú revisas que refleje lo que quieres.

4. **Design (IA):** La IA propone la arquitectura técnica: qué archivos crear, qué patrones usar, cómo se conecta con lo existente.

5. **Tasks (IA):** La IA divide en tareas atómicas, cada una completable en una sesión (< 400 líneas).

6. **Implementación (IA + TDD):** La IA escribe tests primero, después código. Tú revisas cada PR.

7. **Verify (IA):** La IA verifica que la implementación cumple la spec. Corre tests, lint, type check.

8. **Archive (IA):** Se persisten los artefactos. Tú mergeas.

**En cada paso, si no entiendes algo, PARA y pregunta. No sigas hasta que esté claro.**

### 9.8 El contrato con la IA

```
- TÚ defines QUÉ y POR QUÉ
- La IA define CÓMO (pero tú puedes cuestionarlo)
- TÚ revisas y decides si está bien
- Lo que no entiendes, NO lo mergeas
- Los ADRs y specs son TUYOS — los escribes o revisas
- El código es de los dos — la IA lo genera, tú lo validas
```

Si estás en esta columna, **PARAMOS**. No hay apuro. El proyecto es TU portfolio, no mi deadline.

---

# 10. CARRIL B — APRENDIZAJE PARALELO

**Regla fundamental:** El proyecto es siempre la prioridad. El carril B se pausa si el proyecto se retrasa. El proyecto nunca se pausa por el carril B.

**Presupuesto máximo:** 2–3h/semana de las 7–10 totales.

### 10.1 Filosofía de selección

Una formación entra en esta lista si y solo si cumple al menos dos de estas tres condiciones:
1. Es **reconocida por reclutadores técnicos** como señal de competencia real
2. El proceso de preparación enseña conceptos que se usan en producción
3. El examen es suficientemente difícil como para que tenerlo en el CV comunique algo

**Formaciones que NO merecen tu tiempo:**
| Formación | Por qué no |
|---|---|
| Udemy / Platzi / cursos con certificado automático | No hay examen real, cualquiera puede obtenerlo |
| Google Professional Data Engineer | Excesivamente orientado a GCP. Menos transferible. |
| MongoDB University | MongoDB ha perdido adopción frente a PostgreSQL con extensiones |
| Certificaciones de Scrum/PMP | Indican gestión, no ingeniería. No añaden valor técnico. |

### 10.2 AWS Solutions Architect (SAA-C03)

| Atributo | Detalle |
|---|---|
| **Coste** | ~150€ examen |
| **Dificultad** | ⭐⭐⭐ |
| **Tiempo de prep** | 80–120 horas |
| **ROI** | Aparece en el 60–70% de ofertas DevOps/Backend senior en España |
| **Recurso recomendado** | Adrian Cantrill (cantrill.io) — ~65 USD. El más riguroso. |
| **Por qué no el Practitioner** | El Practitioner solo demuestra que leíste la documentación. El Associate demuestra que puedes tomar decisiones de arquitectura. |

**Cuándo:** Durante Fase 1 y principio de Fase 2.

**Plan de estudio semanal (integrado con el proyecto):**

| Semana | Módulo de Cantrill | Práctica recomendada |
|---|---|---|
| 1–2 | IAM: usuarios, roles, policies, SCP | Crear un usuario IAM con mínimos permisos para el CI/CD del proyecto |
| 3–4 | EC2, Auto Scaling, Load Balancers | Comparar con los recursos equivalentes en Kubernetes |
| 5–6 | S3, CloudFront, Route 53 | Configurar S3-compatible como backend de Terraform state |
| 7–8 | RDS, Aurora, ElastiCache | Comparar con PostgreSQL + Redis de tu stack |
| 9–10 | VPC, subnets, NACLs, Security Groups | Diseñar la VPC que usarías si desplegases en AWS |
| 11–12 | Lambda, API Gateway, SQS/SNS | Pensar cómo el reentrenamiento se modelaría en Lambda |
| 13–14 | ECS, EKS, Fargate | Comparar EKS con k3s propio: tradeoffs reales |
| 15–16 | Simulacros completos | 2 simulacros con review de respuestas incorrectas |
| **Semana 16** | **EXAMEN SAA-C03** | |

**Cómo integrar con el proyecto:** Por cada servicio AWS que estudies, preguntate: ¿qué componente de mi proyecto hace algo similar? ¿qué ganaría y qué perdería si usase este servicio AWS en lugar de lo que tengo?

### 10.3 CKAD — Certified Kubernetes Application Developer

| Atributo | Detalle |
|---|---|
| **Coste** | ~395 USD (incluye un retake gratuito) |
| **Dificultad** | ⭐⭐⭐⭐ — examen práctico en terminal, sin opción múltiple |
| **Tiempo de prep** | 60–80 horas |
| **ROI** | Obligatorio en equipos con K8s. El hecho de ser práctico lo hace más creíble que cualquier cert teórica. |
| **Recurso recomendado** | Killer.sh (simulacros más difíciles que el examen real) |
| **Por qué CKAD sobre CKA** | CKAD cubre el trabajo del día a día (desplegar, depurar, configurar apps). CKA cubre administración del clúster. CKAD primero. |

**Cuándo:** Durante Fase 3 (cuando el proyecto ya corre en K8s).

**Estrategia de preparación:**
- 6 semanas antes del examen: 2h/semana en laboratorios de killer.sh
- 2 semanas antes: 1 simulacro completo por semana, revisar cada pregunta fallada
- La semana del examen: repasar comandos más frecuentes (no conceptos, velocidad de ejecución)

**Lo que ya sabrás del proyecto que te da ventaja:**
- Escribir manifests YAML desde cero
- Configurar liveness y readiness probes (como las que ya tenemos en `/health/`)
- Gestionar ConfigMaps y Secrets
- Escalar deployments
- Debuggear pods que no arrancan

### 10.4 Deep Learning / Fast.ai

**Cuándo:** Durante Fase 2.

| Atributo | Detalle |
|---|---|
| **Coste** | ~50€/mes (5 cursos, completable en 3-4 meses) |
| **Dificultad** | ⭐⭐⭐ — los assignments son los que importan |
| **ROI** | Base teórica que todo ML Engineer debe tener. Sin esto, todo es copy-paste. |

Fast.ai no es teoría abstracta. Cada lección produce al menos un commit en el proyecto:

| Lección | Qué aprendes | Integración con el proyecto |
|---|---|---|
| Lesson 1 — Is it a bird? | Entrenamiento básico, transfer learning | Entrena este modelo y registralo en MLflow |
| Lesson 2 — Production | Despliegue, edge cases, datos reales | Aplicá las lecciones al endpoint de predicción |
| Lesson 3 — Neural net foundations | Backpropagation, SGD, loss functions | Entiende las métricas de evaluación que logueas |
| Lesson 4 — Natural Language | NLP básico, embeddings | Añadí un segundo modelo NLP al registry |
| Lesson 5–8 | Arquitecturas avanzadas, fine-tuning | Alimentá el drift detection con modelos más complejos |

**Regla:** Cada lección produce al menos un commit en el proyecto. Sin integración, no cuenta.

### 10.5 System Design

**No es un curso. Es un hábito.**

| Recurso | Formato | Por qué |
|---|---|---|
| **System Design Interview Vol. 1 & 2** — Alex Xu | Libro | El referente del sector para pensar en escala. Cada capítulo es un sistema real (URL shortener, YouTube, Uber). |
| **ByteByteGo** (newsletter + YouTube) — Alex Xu | Gratuito | Los conceptos del libro en formato visual. 1 artículo/semana como hábito. |
| **Designing Data-Intensive Applications** — Martin Kleppmann | Libro | El libro técnico más importante de la última década para backend/data engineers. No es un curso, es una brújula. |

### 10.6 Proyección Salarial y Fases de Carrera

| Fase | Perfil | Rango salarial (España) | Skills clave |
|---|---|---|---|
| **F1** (ahora) | Backend Engineer | 27–35K€ | Python + FastAPI + SQL + Git |
| **F2** (post-proyecto) | DevOps / Platform | 35–42K€ | + CI/CD + Docker + K8s + Observabilidad |
| **F3** (post-cert) | MLOps Engineer | 42–52K€ | + MLflow + Drift + AWS + Terraform |
| **F4** (1–2 años) | Senior MLOps | 52–65K€ | + System Design + Team Leadership |
| **F5** (2–4 años) | Senior Híbrido | 65–75K€+ | + Go/Rust + Arquitectura + Open Source |

### 10.7 Preparación para Entrevistas

**Lo que los reclutadores técnicos miran (en orden):**
1. **El último commit** — Si el repo lleva 8 meses sin actividad, el proyecto está muerto
2. **El README** — Los primeros 200 caracteres. Si no enganchan, no siguen
3. **La estructura de carpetas** — Un proyecto con estructura caótica comunica caos mental
4. **Los tests** — Si hay `/tests` y hay cobertura real, ya estás en el top 20%
5. **El Dockerfile y CI/CD** — Si hay `.github/workflows/`, el proyecto está pensado para producción
6. **Los commits** — Conventional Commits vs "fix stuff"

**Método STAR para entrevistas:**

Para cada feature del proyecto, prepara una historia STAR:
- **S**ituation: contexto (ej: "necesitábamos un endpoint de predicción que no perdiera requests")
- **T**ask: problema concreto (ej: "la red puede perder respuestas, el cliente reintenta")
- **A**ction: qué hiciste (ej: "implementé idempotency key con caché en dos niveles")
- **R**esult: resultado medible (ej: "0% de procesamiento duplicado, reintentos seguros")

**Prepara estas 5 situaciones STAR con el proyecto:**
1. Idempotency key — decisión de diseño, implementación, tradeoffs
2. Health checks diferenciados — liveness vs readiness, por qué importan
3. Monolito modular — arquitectura, cuándo extraer a microservicios
4. Model Registry en PostgreSQL — por qué SQL y no NoSQL
5. CI/CD pipeline — qué falló, cómo lo arreglaste

---

# 11. GLOSARIO

| Término | Significado |
|---|---|
| **ADR** | Architecture Decision Record — documento que explica UNA decisión técnica |
| **API** | Interfaz pública del sistema (endpoints HTTP) |
| **Async** | Ejecución no bloqueante: mientras esperas, haces otra cosa |
| **Cache** | Guardar datos en memoria para no recalcular o leer de disco otra vez |
| **CI/CD** | Integración Continua / Despliegue Continuo — tests + deploy automáticos |
| **Conventional Commit** | Formato de commit: `tipo: mensaje` (feat, fix, chore, docs, etc.) |
| **Coverage** | Porcentaje del código cubierto por tests (mínimo 70%) |
| **Endpoint** | URL específica que acepta requests HTTP |
| **Feature** | Variable de entrada del modelo ML (ej: sepal_length) |
| **Idempotencia** | Propiedad de que una operación repetida produzca el mismo resultado |
| **Inferencia** | Ejecutar el modelo ML con datos para obtener una predicción |
| **JSONB** | Formato de datos JSON en PostgreSQL (binario, indexable) |
| **Liveness** | Health check que dice "el proceso está vivo" |
| **Middleware** | Función que se ejecuta en TODAS las requests (logs, auth, etc.) |
| **Modelo ML** | Archivo binario con un clasificador/regresor entrenado |
| **ORM** | Object-Relational Mapping — mapea tablas a objetos |
| **PR** | Pull Request — propuesta de cambio a revisar antes de mergear |
| **Pydantic** | Biblioteca que valida datos automáticamente en Python |
| **Readiness** | Health check que dice "el proceso puede recibir tráfico" |
| **REST** | Estilo de diseño de APIs (recursos + verbos HTTP) |
| **SDD** | Spec-Driven Development — escribir la spec ANTES del código |
| **Spec** | Especificación técnica de una feature |
| **STAR** | Situación-Tarea-Acción-Resultado — método para responder en entrevistas |
| **Status code** | Código numérico HTTP: 200=OK, 404=No encontrado, 422=Datos inválidos |
| **System Design** | Disciplina de diseñar sistemas a escala (no es un curso, es un hábito) |
| **TDD** | Test-Driven Development — escribir el test ANTES del código |
| **UUID** | Identificador único universal (ej: `3fa85f64-5717-4562`) |

---

> **Versión:** 2.0 — 2026-06-10
>
> *Este documento fusiona el contenido de los 7 documentos de `Docs_Claude/` con el estado real del proyecto Zenith-ops. Actualizalo cuando algo cambie.*
>
> Documentos fuente: `que-es-zenith-ops.md` · `roadmap_proyecto_aprendizaje.md` · `roadmap_granular_mlops_1.md` · `roadmap_elite_engineer.md` · `zenith-ops-ejecucion-granular.md` · `cursor_sdd_setup_guide.md` · `roadmap_granular_mlops.md`
