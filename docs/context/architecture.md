# Arquitectura: MLOps Portfolio Engine (Zenith-ops)

## Propósito

Plataforma de serving y monitorización de modelos ML: registro de modelos, inferencia vía API,
seguimiento de rendimiento y detección de drift cuando las fases correspondientes estén activas.

## Componentes previstos

| Componente | Tecnología | Responsabilidad |
|------------|------------|-----------------|
| Model API | FastAPI + Python 3.12 | Predicciones, health, contratos Pydantic |
| Model Registry | PostgreSQL + SQLAlchemy async | Metadatos de modelos |
| Experiment tracking | MLflow self-hosted (Fase 2+) | Experimentos y artefactos |
| Observabilidad | Prometheus + Grafana + Loki (Fase 2+) | Métricas, dashboards, logs |
| Drift | Evidently AI (Fase 2+) | Señales de degradación |
| CI/CD | GitHub Actions | Test, build, despliegue |
| Infra objetivo | k3s/K8s + Helm + Terraform (Fase 3+) | Orquestación e IaC |

## Flujo de datos (objetivo)

Cliente → `POST /v1/predict` (u otro endpoint aprobado en Spec) → validación Pydantic →
carga de modelo (registry / MLflow según fase) → inferencia → logs estructurados → métricas
(opcional) → respuesta tipada.

## Decisiones clave

- Detalle en `docs/adr/` cuando existan ADRs.
- Fase 1: sin Redis; cache en memoria solo si una Spec lo define.
- Desarrollo: una instancia PostgreSQL puede compartirse entre componentes hasta que producción exija separación.

## Variables de entorno

Lista base en `.env.example` del repositorio.
