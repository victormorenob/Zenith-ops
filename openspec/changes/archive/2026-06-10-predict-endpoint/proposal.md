# Proposal: Prediction Endpoint

## Intent
Implementar el endpoint `POST /v1/predict` que recibe features numéricas, ejecuta inferencia contra un modelo ML cargado en memoria, y devuelve el resultado con métricas de latencia.

## Scope
- Endpoint POST /v1/predict con validación Pydantic
- Servicio de inferencia con caché lazy de modelos (.joblib)
- Modelo dummy Iris para pruebas
- Tests unitarios + integración
- ~310 líneas estimadas

## Problem
El sistema necesita servir predicciones de modelos ML para poder monitorizar su rendimiento (Fase 2) y eventualmente reentrenar automáticamente (Fase 3). Sin este endpoint no hay núcleo sobre el que construir el resto.

## Success Criteria
- POST /v1/predict responde 200 con prediction_id, result, latency_ms
- Modelo no encontrado → 404
- Latencia < 200ms en modelo simple con caché caliente
- Tests: pytest verde, mypy 0 errores, coverage > 70%
