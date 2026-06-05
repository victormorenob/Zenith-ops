# Zenith-Ops: MLOps Portfolio Engine

> *"La diferencia entre un proyecto que existe y uno que no existe es un repositorio con un README."*

**Zenith-Ops** es un proyecto integral de ingeniería y portfolio diseñado para documentar y ejecutar el camino desde el desarrollo Backend hasta el MLOps y la Ingeniería de Infraestructura de alto nivel (Top 1%).

Más que un simple repositorio, es un **motor de aprendizaje y ejecución granular** para 2026-2027, enfocado en construir sistemas de grado industrial utilizando un stack tecnológico moderno, robusto y altamente demandado.

---

## Visión del Proyecto

> *"Los seniors no saben más. Tienen más superficie de contacto con la complejidad y saben gestionarla sin pánico."*

El objetivo principal de Zenith-Ops es construir una plataforma MLOps completa end-to-end, pasando de forma metódica por todas las fases del ciclo de vida del software: desde la configuración de un entorno Unix profesional y la creación de una API robusta, hasta el despliegue de modelos de Machine Learning en Kubernetes con infraestructura inmutable y observabilidad total.

---

## Arquitectura y Stack Tecnológico (Grado Industrial)

La selección tecnológica no sigue modas, sino **densidad de empleo, longevidad y transferibilidad**. Las herramientas han sido elegidas para simular un entorno de producción real.

*   **Lenguaje Core:** Python 3.12+ (Gestión de entornos y dependencias ultra-rápida con `uv`)
*   **Backend & API:** FastAPI (Async-first), Pydantic v2
*   **Base de Datos:** PostgreSQL + SQLAlchemy 2.0 (Async) + Alembic
*   **Testing & Calidad:** Pytest, Ruff (Linter/Formatter), Mypy (Strict mode)
*   **ML & Data:** Pandas/Polars, PyTorch/Scikit-learn, MLflow (Experiment Tracking), Evidently AI (Drift)
*   **Infraestructura & DevOps:** Docker multi-stage, Kubernetes (k3s local / EKS-GKE cloud), Terraform / OpenTofu, GitHub Actions (CI/CD)
*   **Observabilidad:** Prometheus, Grafana, Loki (LGTM Stack), structlog para logging estructurado

---

## Fases de Ejecución

El roadmap está estructurado en fases incrementales de complejidad, asegurando que cada capa está sólida antes de pasar a la siguiente:

1.  **Fase 0 — Entorno y Fundamentos:** Setup de entorno profesional en WSL2 con Zsh, herramientas CLI modernas (eza, bat, fd, rg, just) y dominio de Python puro sin "magia" de frameworks.
2.  **Fase 1 — Primera Versión Desplegada:** Construcción del backend base con FastAPI, separación de responsabilidades (Routers, Core, DB), testing riguroso (>70% cobertura) y dockerización.
3.  **Fase 2 — MLOps Real:** Integración del ciclo de vida de ML. Pipelines de entrenamiento, empaquetado de modelos, tracking con MLflow y telemetría de negocio/sistema con Prometheus y Grafana.
4.  **Fase 3 — Infraestructura Completa:** Orquestación y escalabilidad. Migración a Kubernetes, Infraestructura como Código (IaC) con Terraform y despliegues automatizados (CI/CD).

---

## Estructura del Repositorio

El proyecto implementa una arquitectura limpia y modular, separando estrictamente la lógica de negocio del framework web:

```text
Zenith-Ops/
├── src/                # Código fuente de la aplicación
│   ├── api/v1/         # Routers FastAPI y contratos (Pydantic request/response)
│   ├── core/           # Lógica de negocio pura (independiente de FastAPI)
│   ├── db/             # Modelos SQLAlchemy, queries y migraciones Alembic
│   ├── monitoring/     # Métricas Prometheus y detección de drift
│   └── training/       # Scripts de entrenamiento y registro en MLflow
├── tests/              # Tests automatizados
│   ├── unit/           # Tests unitarios sin I/O externo (mocks)
│   └── integration/    # Tests contra servicios reales (PostgreSQL, etc.)
├── infra/              # Infraestructura (Terraform, manifiestos K8s, Docker)
├── scripts/            # Automatización local y utilidades varias
├── docs/               # Documentación viva (ADRs, Runbooks, Specs)
├── Docs_Claude/        # Roadmaps estratégicos y guías del proyecto
└── .cursorrules        # Reglas estrictas de calidad y arquitectura para la IA
```

---

## Filosofía de Desarrollo (SDD + IA)

Este proyecto adopta **Specification-Driven Development (SDD)** en conjunto con herramientas de IA avanzadas (Cursor IDE).

El contrato de trabajo es estricto: **La IA no toma decisiones de diseño arquitectónico.**

1.  **El humano piensa y diseña:** Define la arquitectura, toma decisiones de dependencias (ADRs), escribe las especificaciones concretas y establece el *qué* y el *por qué*.
2.  **La IA ejecuta y asiste:** Lee el contexto holístico del proyecto, implementa el *cómo* respetando las rígidas reglas del `.cursorrules` (tipado estricto, manejo de errores de dominio, inyección de dependencias) y genera los tests asociados.

*Este sistema evita el "copypaste" ciego y garantiza que el desarrollador mantiene el control absoluto y el entendimiento profundo de cada línea de código en producción.*
