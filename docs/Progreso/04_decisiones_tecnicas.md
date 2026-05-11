# Decisiones Tecnicas (ADR Ligero)

## Decision 001 - Framework backend

- Fecha: 2026-03-17
- Decision: usar Django + DRF (en lugar de continuar con FastAPI para rework)
- Motivo:
  - Auth y permisos mas completos out of the box
  - Admin nativo para gestion
  - ORM y migraciones integradas
- Tradeoff:
  - Mas boilerplate que FastAPI

## Decision 002 - Driver PostgreSQL

- Fecha: 2026-03-17
- Decision: usar `psycopg[binary]` v3
- Motivo:
  - Compatibilidad moderna en entorno actual
  - Instalacion estable en esta base
- Tradeoff:
  - Requiere validar version pinneada en CI/produccion

## Decision 003 - Base de datos separada

- Fecha: 2026-03-17
- Decision: nueva BD para rework (`pdf_ia_rework_db`)
- Motivo:
  - Evitar colisiones con el proyecto original
  - Permitir cambios de esquema sin riesgo
- Tradeoff:
  - Doble mantenimiento temporal

## Decision 004 - Entornos local vs docker

- Fecha: 2026-03-17
- Decision:
  - `.env` local usa `localhost:5434`
  - `docker-compose` override usa `db:5432`
- Motivo:
  - Evitar errores de resolucion de host
- Tradeoff:
  - Mantener claro cual URL aplica en cada contexto
