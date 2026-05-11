# SPEC-NNN: [Nombre de la feature]

**Estado:** Borrador | En revisión | Aprobada | Implementada  
**Issue:** #[número]  
**ADR relacionado:** ADR-NNN (si aplica)  
**Dependencias:** SPEC-NNN (specs que deben estar implementadas antes)

---

## Contexto

[Qué existe ahora. Qué problema resuelve. Qué partes del sistema toca. 2–4 frases.]

---

## Comportamiento esperado

### Input

[Tipos, restricciones, límites.]

### Output

[Tipos, formato, códigos HTTP de éxito.]

### Casos de error

| Caso | Respuesta | Código HTTP |
|------|-----------|-------------|
| … | … | … |

---

## Contrato de la API (si aplica)

**Método:** GET | POST | PUT | DELETE  
**Endpoint:** `/v1/[ruta]`

**Request body (ejemplo):**

```json
{
  "campo": "tipo y descripción"
}
```

**Response 200 (ejemplo):**

```json
{
  "campo": "tipo y descripción"
}
```

**Errores (formato estándar):**

```json
{"error": "codigo_snake_case", "message": "descripción legible", "detail": {}}
```

---

## Schema de base de datos (si aplica)

[Tablas, columnas, índices con justificación.]

---

## Reglas de negocio

1. [Regla verificable en test]
2. […]

---

## Criterios de aceptación

- [ ] [Criterio binario, con valores concretos]
- [ ] […]

---

## Fuera de scope

- No incluye …
- No modifica …
- … se cubre en SPEC-NNN

---

## Instrucciones para la IA (opcional)

[Patrones a reutilizar, archivos existentes, restricciones de implementación.]
