# ZENITH-OPS — GUÍA ÚNICA
### Documento consolidado que unifica planificación + aprendizaje + ejecución
### Víctor · 2026 · MLOps Portfolio Engine

> Esta guía reemplaza: roadmap_granular_mlops.md, roadmap_granular_mlops_1.md,
> roadmap_proyecto_aprendizaje.md, zenith-ops-ejecucion-granular.md, y roadmap_elite_engineer.md.
> Si lees esto, no necesitás los otros.

---

## Índice

1. [¿Por qué esto vale más que un máster?](#1-por-qué-esto-vale-más-que-un-máster)
2. [Cómo usar esta guía](#2-cómo-usar-esta-guía)
3. [Las preguntas que responden a cada decisión](#3-las-preguntas-que-responden-a-cada-decisión)
4. [Setup del entorno (una vez)](#4-setup-del-entorno-una-vez)
5. [Estructura del repositorio](#5-estructura-del-repositorio)
6. [Fase 0 — Fundamentos Python (Sem 1–3)](#6-fase-0--fundamentos-python-sem-1-3)
7. [Fase 1 — MVP: API + Registry (Sem 4–10)](#7-fase-1--mvp-api--registry-sem-4-10)
8. [Fase 2 — MLOps real (Sem 11–20)](#8-fase-2--mlops-real-sem-11-20)
9. [Fase 3 — Infra completa (Sem 21–32)](#9-fase-3--infra-completa-sem-21-32)
10. [Templates](#10-templates)
11. [Mapa de carrera y certificaciones](#11-mapa-de-carrera-y-certificaciones)
12. [Matriz de decisión: tablas BD](#12-matriz-de-decisión-tablas-bd)

---

## 1. Por qué esto vale más que un máster

### El problema que vos mismo señalaste

> *"Me estoy fiando de la IA para elegir stack, herramientas, arquitectura. No es algo que sepa con certeza que me va a hacer avanzar y aprender de verdad."*

Esa frase es la diferencia entre un ingeniero que crece y uno que estanca. El hecho de que te la estés haciendo ya te separa del 90%.

### Por qué un máster NO resuelve esto

| Lo que creés que te da un máster | Lo que realmente pasa |
|---|---|
| Estructura externa que te fuerza a estudiar | Tu patrón es "Arquitecto que no Ejecuta" — la estructura externa es tu muleta, no tu motor |
| Un profesor que responde tus dudas | Te acostumbrás a que te digan qué hacer, justo lo contrario de lo que necesitás |
| Un título que abre puertas en RRHH | Ya estás en Indra con K8s. Tu próximo salto lo define tu portfolio, no otro papel |
| Aprendizaje "garantizado" por el programa | El 80% de lo que se aprende en un máster de ML nunca se usa en producción |

### Por qué Zenith-Ops SÍ resuelve esto

**Si lo hacés bien** — es decir, si no dejás que la IA elija por vos — esto te da lo que un máster no puede:

1. **Un sistema en producción real** con HTTPS, CI/CD, monitoreo, drift detection. No un notebook, no un proyecto localhost.
2. **Decisiones con tradeoffs reales** — cada herramienta la elegiste vos después de investigar alternativas, no porque el temario lo decía.
3. **Un portfolio que habla por sí solo** — en una entrevista, "mirá este dashboard de Grafana de mi pipeline en producción" pesa más que "tengo un título".
4. **El hábito de ejecutar** — que es lo único que te va a sacar del ciclo de 15-20 días de abandono.

### La regla de oro de esta guía

> **Cada vez que implementes algo sin entender el por qué, no estás aprendiendo.**
> Estás traduciendo instrucciones de IA a código.

Esta guía está diseñada para que en CADA fase te hagas las preguntas de la [Sección 3](#3-las-preguntas-que-responden-a-cada-decisión) **antes** de pedirle a la IA que escriba código. No después.

---

## 2. Cómo usar esta guía

### Estructura de cada fase

Cada fase tiene exactamente:

```
OBJETIVO → Qué aprendés → Preguntas de investigación → Qué construís → Validación binaria
```

### Flujo de trabajo para cada feature

```
1. INVESTIGÁ (30 min)
   → Leé las preguntas de la sección 3 para esta feature
   → Investigá las alternativas, no lo mejor, lo que tiene tradeoffs reales

2. ESCRIBÍ LA SPEC (30 min)
   → Usá el template de la sección 10
   → Definí contratos, errores, criterios de aceptación
   → SIN CÓDIGO todavía

3. IMPLEMENTÁ CON SDD (2-3h)
   → Pasá la Spec a la IA
   → Revisá CADA archivo que genera
   → Si no entendés algo, PARÁ y preguntá

4. VALIDÁ (15 min)
   → Tests: just test
   → Lint: just lint
   → Prueba binaria de la fase
```

### Cuándo usar SDD y cuándo NO

| Situación | Modo |
|---|---|
| Primer endpoint de un tipo nuevo | **Manual** — escribirlo vos para entender el patrón |
| Endpoints repetitivos (CRUD, registry) | **SDD** — la IA genera el boilerplate |
| Configuración de infra (Docker, CI/CD, K8s) | **Manual** — cada línea importa |
| Tests de integración con patrones conocidos | **SDD** — la IA genera sobre fixtures existentes |
| Diseño de arquitectura o decisión técnica | **Nunca IA** — es tu trabajo |

---

## 3. Las preguntas que responden a cada decisión

Estas son las preguntas que te aseguran que estás aprendiendo de verdad.
No las respondas de memoria. Investigá.

### Stack general

- **FastAPI**: ¿Por qué existe? ¿Qué problema resuelve sobre Flask? ¿Qué significa que sea async? ¿Cuándo NO conviene?
- **Pydantic v2**: ¿Qué cambió de v1 a v2? ¿Qué son los validated fields? ¿Qué diferencia hay entre `BaseModel` y un `TypedDict`?
- **SQLAlchemy async**: ¿Por qué async para base de datos? ¿Qué es una connection pool? ¿Qué pasa si tenés 100 requests concurrentes sin pool?
- **asyncpg**: ¿Qué lo hace más rápido que psycopg2? ¿Qué es el protocolo binario de PostgreSQL?
- **UV**: ¿Qué problema resuelve? ¿Por qué es más rápido que pip? ¿Qué es un lockfile determinista?

### Arquitectura

- **src-layout**: ¿Qué problema de imports resuelve? ¿Cómo se ve un `sys.path` sin src-layout?
- **Carpetas core/ api/ db/**: Sin mirar el código, definí qué vive en cada una. Si dos se pispean, está mal.
- **pyproject.toml**: ¿Qué reemplazó? ¿Qué es `[project.scripts]`? ¿Para qué sirve?
- **Justfile**: ¿Qué problema resuelve? ¿Por qué no alcanza con un script de bash?

### Infraestructura

- **Docker multi-stage**: ¿Por qué tener dos stages? ¿Cuánto achica la imagen final y por qué importa?
- **Hetzner vs AWS**: Buscá precios. Mismo servidor. ¿Qué sacrificás en cada uno?
- **Health checks**: ¿Cuál es la diferencia entre liveness y readiness? ¿Qué pasa si los confundís en K8s?
- **CI/CD**: ¿Qué diferencia hay entre CI y CD? ¿Qué es un pipeline? ¿Por qué deploy automático y no manual?

### ML / MLOps

- **Modelo hardcodeado**: ¿Por qué hardcodear en el MVP? ¿Qué estamos posponiendo y por qué es inteligente?
- **Feature store**: ¿Qué es? ¿Por qué existe como concepto separado?
- **MLflow**: ¿Qué problema resuelve? ¿Qué es experiment tracking? ¿Qué es model registry?
- **Drift detection**: ¿Qué tipos de drift existen? ¿Por qué importa más que la accuracy del modelo?
- **Evidently AI**: ¿Qué métricas calcula para detectar drift? ¿Cómo funciona estadísticamente?

### Testing

- **Test unitario**: ¿Qué es exactamente "unitario"? ¿Qué NO es?
- **Fixture**: ¿Qué problema resuelve? ¿Qué diferencia hay con setUp/tearDown?
- **Mock**: ¿Cuándo mockear y cuándo no? ¿Qué riesgo tiene mockear demasiado?
- **Coverage**: ¿70% es suficiente? ¿Qué partes deberían tener 100%?

---

## 4. Setup del entorno (una vez)

Hacé esto UNA VEZ. Verificá que cada paso funciona antes del siguiente.

### 4.1 WSL2 + Ubuntu

```powershell
# PowerShell como Admin
wsl --install -d Ubuntu-24.04
# Reiniciá
```

```bash
# Dentro de Ubuntu
sudo apt update && sudo apt upgrade -y
sudo apt install -y build-essential git curl wget zsh unzip
```

### 4.2 Zsh + herramientas

```bash
chsh -s $(which zsh)
# Cerrá y abrí de nuevo la terminal

# Oh My Zsh
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

# Plugins
git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions
git clone https://github.com/zsh-users/zsh-syntax-highlighting ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
git clone https://github.com/zsh-users/zsh-completions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-completions

# En ~/.zshrc: plugins=(git zsh-autosuggestions zsh-syntax-highlighting zsh-completions docker kubectl)

# Starship
curl -sS https://starship.rs/install.sh | sh
echo 'eval "$(starship init zsh)"' >> ~/.zshrc
```

### 4.3 CLI tools

```bash
sudo apt install -y ripgrep fd-find fzf bat zoxide httpie tmux
ln -sf $(which fdfind) ~/.local/bin/fd

# Rust toolchain
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env

# Herramientas Rust
cargo install eza git-delta just lazygit
```

### 4.4 UV + Python

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv python install 3.12
uv --version
```

### 4.5 Git

```bash
git config --global user.name "Víctor Moreno"
git config --global user.email "tu@email.com"
git config --global init.defaultBranch main
git config --global pull.rebase true
git config --global push.autoSetupRemote true

ssh-keygen -t ed25519 -C "tu@email.com"
cat ~/.ssh/id_ed25519.pub
# Añadilo a GitHub: Settings → SSH and GPG keys
```

### 4.6 VS Code

```bash
# Extensiones
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
code --install-extension charliermarsh.ruff
code --install-extension ms-python.mypy-type-checker
code --install-extension ms-azuretools.vscode-docker
code --install-extension redhat.vscode-yaml
code --install-extension eamodio.gitlens
code --install-extension mhutchie.git-graph
```

---

## 5. Estructura del repositorio

```text
zenith-ops/
├── .github/
│   ├── workflows/               ← CI/CD pipelines
│   ├── ISSUE_TEMPLATE/          ← feature.md, bug.md
│   └── pull_request_template.md
├── src/
│   ├── api/v1/                  ← Endpoints FastAPI
│   ├── core/                    ← Lógica de negocio pura
│   ├── db/                      ← Modelos SQLAlchemy, queries, migrations/
│   ├── monitoring/              ← Métricas Prometheus, drift
│   └── training/                ← Scripts de entrenamiento
├── tests/
│   ├── unit/                    ← Tests sin I/O externo
│   └── integration/             ← Tests contra servicios reales
├── docs/
│   ├── adr/                     ← Architecture Decision Records
│   ├── runbooks/                ← Cómo operar el sistema
│   └── specs/                   ← Feature specifications
├── infra/
│   ├── docker/                  ← Dockerfile, docker-compose
│   ├── helm/                    ← Helm charts (Fase 3)
│   └── terraform/               ← IaC (Fase 3)
├── .env.example
├── .gitignore
├── .pre-commit-config.yaml
├── Justfile
├── pyproject.toml
└── README.md
```

---

## 6. Fase 0 — Fundamentos Python (Sem 1–3)

### Objetivo

Poder construir un endpoint FastAPI tipado con validación Pydantic y tests en < 1h sin buscar referencias.

### Qué aprendés

- asyncio (event loop, tasks, await)
- Pydantic v2 (BaseModel, validators, model_config)
- FastAPI (routers, Depends, HTTPException, response_model)
- pytest (fixtures, parametrize, conftest)
- UV (init, add, sync, lockfile)

### Preguntas de investigación para esta fase

- ¿Cómo funciona el event loop de Python vs Node.js? ¿Son iguales?
- ¿Qué es `async def` vs `def` en FastAPI? ¿Cuándo usar cada uno?
- ¿Qué diferencia hay entre `Field()` y `validator` en Pydantic?
- ¿Qué es una fixture en pytest? ¿Qué scope tiene por defecto?
- ¿Qué es `conftest.py` y cómo se resuelve su ámbito?

### Prueba binaria

Sin buscar referencias, construí en < 120 min:

```python
# POST /v1/test-feature
# Request: { "request_id": "uuid", "data": { "name": str, "value": int } }
# Validar: value entre 1-100
# Error 422 si value > 100, con campo específico
# Éxito 200: { "id": str, "result": int }

# Tests:
# - Happy path → 200
# - value inválido → 422
```

```bash
uv run pytest    # Verde
just lint        # Sin errores
```

**Si tardás más de 120 min**: repetí la semana. Sin excepción.

---

## 7. Fase 1 — MVP: API + Registry (Sem 4–10)

### Objetivo

API en producción real (Fly.io, HTTPS) que sirve predicciones de un modelo hardcodeado,
con CI/CD, tests reales y documentación.

### Qué aprendés

- FastAPI en producción (middleware, logging, error handling)
- SQLAlchemy async + Alembic
- CRUD REST con PostgreSQL
- Docker multi-stage
- GitHub Actions CI/CD
- Deploy en Fly.io
- Health checks diferenciados
- Idempotency keys

### BD: las 3 tablas de Fase 1

Solo estas tres. Nada más.

**Tabla 1: `model_registry`** — ¿Por acá? Sin registry no sé qué modelo usar para predecir.

| Columna | Tipo | Por qué |
|---|---|---|
| id | UUID PK | Portable entre entornos |
| name | VARCHAR(255) | Nombre del modelo |
| version | VARCHAR(50) | Semver |
| framework | VARCHAR(50) | sklearn, pytorch... |
| artifact_path | TEXT | Ruta del archivo |
| status | VARCHAR(20) | staging/production/archived |
| metrics | JSONB | Flexibilidad de schema |
| created_at, deployed_at | TIMESTAMPTZ | Auditoría |

**Tabla 2: `prediction_metadata`** — ¿Por acá? Cada request deja traza.

| Columna | Tipo | Por qué |
|---|---|---|
| id | UUID PK | |
| request_id | UUID UNIQUE | Idempotencia |
| model_id | UUID FK → model_registry | |
| status | VARCHAR(20) | success/error |
| error_message | TEXT | Solo si falla |
| latency_ms | INT | Rendimiento |
| created_at | TIMESTAMPTZ | |

**Tabla 3: `health_checks`** — ¿Por acá? /health/ready necesita historial de checks.

| Columna | Tipo |
|---|---|
| id | UUID PK |
| check_type | VARCHAR(50) — db_connection, model_load |
| status | VARCHAR(20) — ok, error |
| error_message | TEXT |
| checked_at | TIMESTAMPTZ |

### Lo que NO está en Fase 1 (y por qué)

| Tabla | Entra en | Razón |
|---|---|---|
| experiments | Fase 2 | MLflow los gestiona |
| model_versions | Fase 2 | Solo con reentrenamiento |
| prediction_logs (features) | Fase 2 | Solo para drift detection |
| drift_detections | Fase 2 | Solo con Evidently |

### Objetivo 1.1 — Endpoint /v1/predict (Sem 4-5)

**Qué investigar primero:**
- ¿Qué es un correlation ID y cómo se propaga?
- ¿Qué es idempotency key y qué problema resuelve?
- ¿Diferencia entre liveness y readiness probe?

**Spec:**
```markdown
# SPEC-001: Prediction Endpoint

POST /v1/predict
Request: { model_id, features, idempotency_key? }
Response 200: { prediction_id, model_id, result, confidence?, latency_ms, model_version }

Errores:
  | Caso | Código |
  | Modelo no existe | 404 |
  | Features inválidas | 422 |
  | Timeout | 503 |
  | Error interno | 500 |

Reglas:
1. Cada predicción genera UUID único
2. Latencia medida con time.monotonic()
3. Modelo cacheado en memoria al arrancar
4. Idempotency key: mismo key → mismo resultado

Criterios de aceptación:
- [ ] POST /v1/predict devuelve 200 con estructura correcta
- [ ] model_id inválido → 404
- [ ] features inválidas → 422 con campo específico
- [ ] latency < 500ms
- [ ] Tests pasan (4+ casos)
- [ ] Coverage > 70%
```

**Implementación:**
- Manual el primer endpoint (entendé el patrón)
- SDD para endpoints repetitivos

**Validación:**
```bash
http POST localhost:8000/v1/predict model_id="test" features='{"f1": 1.0}'
→ 200 con prediction_id, result, latency_ms
```

### Objetivo 1.2 — Model Registry CRUD (Sem 6-7)

**Qué investigar primero:**
- ¿UUID vs serial integer como PK?
- ¿ENUM de PostgreSQL vs CHECK constraint?
- ¿JSONB vs columnas separadas para métricas?

**Spec:**
```markdown
# SPEC-002: Model Registry CRUD

POST   /v1/models/register         → 201 (crear)
GET    /v1/models                   → 200 (listar todos)
GET    /v1/models/{id}              → 200 (detalle)
PATCH  /v1/models/{id}/status       → 200 (cambiar estado)

Reglas:
1. (name, version) es único → 409 si duplicado
2. Status solo puede ser: staging, production, archived
3. Solo production está activo para predicciones

Criterios de aceptación:
- [ ] POST crea modelo y devuelve 201 con ID
- [ ] Duplicado → 409
- [ ] GET lista todos
- [ ] PATCH status funciona
- [ ] Tests de integración contra PostgreSQL real
```

### Objetivo 1.3 — Health checks (Sem 8)

```python
# /health/live — NUNCA falla. Siempre 200.
@router.get("/health/live")
async def health_live():
    return {"status": "alive"}

# /health/ready — 200 solo si BBDD + modelo están ok. Sino 503.
@router.get("/health/ready")
async def health_ready():
    # intenta SELECT 1 en BBDD
    # verifica modelo cargado en memoria
    # 200 o 503
```

**Validación:**
```bash
curl localhost:8000/health/live    → 200 SIEMPRE
curl localhost:8000/health/ready   → 200 (todo ok)

docker compose stop postgres
curl localhost:8000/health/live    → 200 (sigue vivo)
curl localhost:8000/health/ready   → 503
```

### Objetivo 1.4 — CI/CD (Sem 9)

**Qué investigar primero:**
- ¿Qué es un pipeline de CI? ¿Qué es CD?
- ¿Qué diferencia hay entre GitHub Actions y un deploy manual?

**Pipeline:**
```yaml
jobs:
  test:     lint + type-check + tests + coverage > 70%
  build:    docker build multi-stage + push a GHCR (depende de test)
  deploy:   flyctl deploy (solo en push a main, depende de build)
```

### Objetivo 1.5 — Deploy (Sem 10)

```bash
flyctl launch
# Region: mad (Madrid)
# PostgreSQL: No (usá Neon o la propia)
```

### Prueba de transición Fase 1 → 2

Binaria. Todo verde o no avanzás.

- [ ] POST /v1/predict funciona (local + producción)
- [ ] Registry CRUD funciona (register, list, get, patch)
- [ ] /health/live → 200 siempre
- [ ] /health/ready → 200/503 según estado
- [ ] CI/CD bloquea PRs si tests fallan (verificado rompiendo un test)
- [ ] Deploy automático en Fly.io funciona
- [ ] just test → verde, coverage > 70%
- [ ] just lint → sin cambios
- [ ] README con diagrama, quick start, endpoints
- [ ] Mínimo 2 ADRs escritos
- [ ] Runbook de deploy en /docs/runbooks/

---

## 8. Fase 2 — MLOps real (Sem 11–20)

### Objetivo

MLflow self-hosted, Prometheus + Grafana, drift detection. Portfolio de nivel mid/senior.

### Qué aprendés

- MLflow (experiment tracking, model registry)
- Prometheus client (métricas de negocio, no de infra)
- Grafana dashboards
- Evidently AI (drift detection estadístico)
- Alerting basado en métricas
- Reentrenamiento automático con GitHub Actions

### BD: se añaden 3 tablas

**Tabla 4: `experiments`** — ¿Por qué ahora? MLflow genera experimentos, los registrás en BBDD.

| Columna | Tipo |
|---|---|
| id | UUID PK |
| name | VARCHAR(255) |
| status | pending/running/completed/failed |
| model_id | UUID FK → model_registry |
| metrics | JSONB |
| parameters | JSONB |
| created_at, completed_at | TIMESTAMPTZ |

**Tabla 5: `model_versions`** — ¿Por qué ahora? Cada entrenamiento crea una versión.

| Columna | Tipo |
|---|---|
| id | UUID PK |
| model_id | UUID FK → model_registry |
| experiment_id | UUID FK → experiments |
| mlflow_run_id | VARCHAR(255) |
| metrics | JSONB |
| artifacts_uri | TEXT |
| created_at | TIMESTAMPTZ |

**Tabla 6: `prediction_logs`** — ¿Por qué ahora? Drift detection necesita features históricas.

| Columna | Tipo |
|---|---|
| id | UUID PK |
| model_id | UUID FK |
| features | JSONB NOT NULL |
| prediction | FLOAT |
| confidence | FLOAT |
| created_at | TIMESTAMPTZ |

### Objetivo 2.1 — MLflow (Sem 11-13)

**Qué investigar primero:**
- ¿MLflow vs Weights & Biases? Tradeoffs reales.
- ¿MLflow tracking vs MLflow registry? ¿Son lo mismo?
- ¿Compartir PostgreSQL con la API o instancia separada?

**Qué construís:**
- docker-compose con MLflow + PostgreSQL backend
- Script de entrenamiento que registra experimentos
- Endpoint de predicción que carga modelos desde MLflow

### Objetivo 2.2 — Prometheus + Grafana (Sem 14-16)

**Qué investigar primero:**
- ¿Qué es un Counter? ¿Qué es un Histogram? ¿Qué es un Gauge?
- ¿Por qué Prometheus usa pull y no push?
- ¿Qué es un dashboard narrativo?

**Métricas de negocio (NO de infra):**
```
mlops_prediction_requests_total   → Counter (por modelo, versión, estado)
mlops_prediction_latency_seconds  → Histogram (P50/P90/P99)
mlops_prediction_confidence       → Histogram
mlops_active_models               → Gauge
```

**Dashboard Grafana (orden narrativo):**
1. Request Rate (req/min) — ¿se usa?
2. Latency P50/P90/P99 — ¿responde bien?
3. Error Rate — ¿hay problemas?
4. Confidence Distribution — ¿el modelo está seguro?
5. Active Models — ¿cuántos hay?
6. Inference Throughput — ¿cuánto soporta?

Exportar dashboard como JSON a `/infra/grafana/dashboards/`.

### Objetivo 2.3 — Drift detection (Sem 17-20)

**Qué investigar primero:**
- ¿Qué es data drift vs prediction drift vs concept drift?
- ¿Cómo funciona el test de Kolmogorov-Smirnov?
- ¿Qué es la divergencia de Jensen-Shannon?

**Qué construís:**
- Almacenar features de cada predicción en `prediction_logs`
- Job periódico que compara distribución actual vs referencia
- Endpoint `/v1/monitoring/drift/{model_id}`
- Alerta si drift supera threshold configurable

### Prueba de transición Fase 2 → 3

- [ ] MLflow tiene 3+ experimentos registrados
- [ ] Dashboard Grafana con 6 panels con datos reales
- [ ] Drift detection devuelve resultados coherentes
- [ ] Simulación de drift: cambiar features → drift_detected = true
- [ ] just test → verde, coverage > 70%
- [ ] Deploy automático sigue funcionando
- [ ] 3 ADRs nuevos (MLflow, observabilidad, drift)

---

## 9. Fase 3 — Infra completa (Sem 21–32)

### Objetivo

Stack completo en Kubernetes (k3s) con Helm chart propio, toda la infraestructura como código en Terraform.

### Qué aprendés

- Helm charts desde cero (values.yaml, templates, helpers)
- k3s en VPS real
- Terraform (provisioning, state remoto, modules)
- Despliegue reproducible desde cero

### BD: sin cambios. Las 6 tablas de Fase 2 son definitivas.

### Objetivo 3.1 — Kubernetes + Helm (Sem 21-26)

**Qué investigar primero:**
- ¿k3s vs k8s completo? ¿Qué sacrificás?
- ¿Helm values vs hardcode? ¿Qué va en cada uno?
- ¿Cómo calcular CPU/mem requests y limits? (no adivinar)

**Qué construís:**
- Cluster k3s en Hetzner VPS
- Helm chart propio con templates de: Deployment, Service, Ingress, HPA, ConfigMap, Secrets
- Liveness y readiness probes configuradas
- Rolling update sin downtime
- HPA basado en CPU/mem

### Objetivo 3.2 — Terraform (Sem 27-28)

**Qué investigar primero:**
- ¿Qué es state remoto y por qué no puede vivir en local?
- ¿Terraform vs OpenTofu vs Pulumi? ¿Por qué uno u otro?

**Qué construís:**
- Módulo de VPS (Hetzner)
- Módulo de firewall
- Módulo de DNS
- State remoto en Cloudflare R2 o Backblaze B2
- cloud-init para instalar k3s

**Prueba definitiva:**
```bash
terraform destroy    # Todo abajo
terraform apply      # En < 15 min, todo funcionando de nuevo
```

### Objetivo 3.3 — Portfolio final (Sem 29-32)

- Documentación completa: revisar TODOS los ADRs
- MkDocs site desplegado en GitHub Pages
- Video demo de 5 min: problema → arquitectura → predict → Grafana → drift → reentrenamiento
- Post en LinkedIn explicando decisiones de ingeniería (no tutorial, sí análisis)
- README final pulido con badges, diagrama, links

---

## 10. Templates

### Template de Spec (copiar y rellenar para cada feature)

```markdown
# SPEC-NNN: [Nombre de la feature]

**Estado:** Borrador | Aprobada | Implementada
**Dependencias:** SPEC-NNN

## Contexto
[Qué existe ahora. Qué problema resuelve. 2-4 frases.]

## Contrato de API

**Método:** GET | POST | PATCH | DELETE
**Endpoint:** /v1/[ruta]

**Request:**
```json
{ "campo": "tipo y descripción" }
```

**Response (200):**
```json
{ "campo": "tipo" }
```

**Errores:**
| Caso | Código |
|---|---|
| [caso] | [código] |

## Schema BD (si aplica)

[Tablas nuevas o modificadas. Columnas, tipos, constraints.]

## Reglas de negocio
1. [Regla verificable]
2. [Regla verificable]

## Criterios de aceptación
- [ ] [Criterio con valores concretos]
- [ ] Tests pasan
- [ ] Coverage > 70%

## Fuera de scope
- No incluye [X]
```


### Template de ADR (para decisiones técnicas)

```markdown
# ADR-NNN: [Título]

**Fecha:** YYYY-MM-DD
**Estado:** Propuesto | Aceptado | Superado por ADR-NNN

## Contexto
¿Qué situación genera esta decisión?

## Opciones consideradas

### Opción A: [nombre]
Pros: ...
Contras: ...

### Opción B: [nombre]
Pros: ...
Contras: ...

## Decisión
Elegimos [Opción] porque [razón concreta].

## Consecuencias
Positivas: ...
Trade-offs: ...

## Referencias
[Links a documentación relevante]
```

---

## 11. Mapa de carrera y certificaciones

Esto es el carril B. El proyecto es siempre la prioridad.

| Fase | Certificación | Cuándo |
|---|---|---|
| Paralelo al proyecto | AWS Solutions Architect Associate (SAA-C03) | Meses 1-4 (~2h/sem) |
| Después de Fase 1 | CKAD (Certified Kubernetes Application Developer) | Meses 4-8 |
| Durante Fase 3 | Terraform Associate | Meses 6-10 |
| Después del proyecto | Deep Learning Specialization (Andrew Ng) | Meses 12-18 |

**Las que NO hacen**: Google Data Engineer, Azure AZ-900, MongoDB University, DataCamp, Scrum/PMP.

### Plan de crecimiento salarial

| Hito | Sueldo objetivo |
|---|---|
| Situación actual (Indra) | ~27.700€ |
| Después de Fase 3 + AWS SAA + CKAD | 35-42K€ |
| Con pipeline MLOps real en portfolio | 42-52K€ |
| Senior híbrido (MLOps + Backend) | 55-75K€+ |

---

## 12. Matriz de decisión: tablas BD

| Tabla | Fase | ¿Por qué en esta fase y no antes? | Semana |
|---|---|---|---|
| model_registry | 1 | Sin registry no sé qué modelo usar | 6 |
| prediction_metadata | 1 | Cada request deja traza para debugging | 4 |
| health_checks | 1 | /health/ready necesita historial de checks | 8 |
| experiments | 2 | MLflow genera experimentos, los registro | 11 |
| model_versions | 2 | Cada entrenamiento crea una versión | 13 |
| prediction_logs | 2 | Drift detection necesita features históricas | 17 |
| drift_detections | 2 | Registro de cuándo se detecta drift | 19 |
| retraining_jobs | 3 | Reentrenamiento automático (si entra en roadmap) | Post-MVP |

---

## Hoja de ruta semanal compacta

| Semana | Fase | Qué hacés |
|---|---|---|
| 1-3 | 0 | Python + FastAPI + pytest. Prueba: endpoint en < 120 min |
| 4-5 | 1.1 | /v1/predict con modelo hardcodeado |
| 6-7 | 1.2 | Model Registry CRUD + PostgreSQL + Alembic |
| 8 | 1.3 | Health checks diferenciados |
| 9 | 1.4 | CI/CD con GitHub Actions |
| 10 | 1.5 | Deploy en Fly.io + validación completa |
| 11-13 | 2.1 | MLflow self-hosted + integración |
| 14-16 | 2.2 | Prometheus + Grafana + métricas de negocio |
| 17-19 | 2.3 | Drift detection con Evidently |
| 20 | — | Reentrenamiento automático + validación Fase 2 |
| 21-26 | 3.1 | k3s + Helm chart propio |
| 27-28 | 3.2 | Terraform IaC |
| 29-32 | 3.3 | Documentación, video demo, LinkedIn |

---

*Este documento reemplaza y unifica: roadmap_granular_mlops.md, roadmap_granular_mlops_1.md,
roadmap_proyecto_aprendizaje.md, zenith-ops-ejecucion-granular.md, roadmap_elite_engineer.md,
y roadmap-estructura-prompt.md.*

*Creado el 18/06/2026. Revisar al completar cada fase.*
