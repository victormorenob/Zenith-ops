# SPEC-000: Convenciones de implementación del proyecto

**Estado:** Aprobada
**Issue:** N/A (meta-spec)
**Dependencias:** Ninguna

---

## Propósito

Define patrones que aplican a **todas** las features. La IA debe leerla junto a la Spec concreta.

---

## Estructura de módulos

Por feature (nombres ilustrativos):

| Capa | Ruta típica |
|------|-------------|
| Negocio | `src/core/<feature>.py` |
| API | `src/api/v1/<router>.py` |
| Persistencia | `src/db/<repositorio>.py` |
| Tests unitarios | `tests/unit/test_<feature>.py` |
| Tests integración | `tests/integration/test_<flujo>.py` |

La organización del paquete Python (`zenith_ops`, etc.) debe seguir la Spec sin romper imports públicos acordados.

---

## Manejo de errores

Todas las excepciones de dominio heredan de `ZenithOpsException`:

- `ModelNotFoundError` → HTTP 404
- `ModelNotReadyError` → HTTP 503
- `InvalidInputError` → HTTP 422
- `InferenceError` → HTTP 500

Los endpoints (o un exception handler registrado) mapean `ZenithOpsException` al status correspondiente.
No usar `except Exception`. No devolver stacktraces al cliente.

Cuerpo de error:

```json
{"error": "codigo_snake_case", "message": "descripción legible", "detail": {}}
```

---

## Dependency injection (FastAPI)

- Servicios y sesiones se obtienen con `Depends(get_*)`.
- No instanciar servicios pesados dentro del cuerpo del endpoint.

---

## Logging

- `structlog` únicamente; prohibido `print()` para trazas operativas.
- Incluir `event` y `correlation_id` en cada log de request.

---

## Criterios de aceptación de esta meta-Spec

- [ ] Tipos explícitos; `mypy --strict` sin errores en código nuevo tocado por la feature.
- [ ] Funciones públicas con docstring Google donde aplique.
- [ ] Errores alineados con la jerarquía anterior.
- [ ] Tests en patrón AAA y nombres descriptivos.
- [ ] `just lint` y `just test` en verde (o comandos equivalentes documentados en el repo).
