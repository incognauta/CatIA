# Arquitectura General

Fecha: 2026-03-18
Estado: Activo

## 1. Objetivo

Definir la arquitectura de referencia para PDF_IA_Rework y evitar decisiones inconsistentes durante las fases 2-10.

## 2. Componentes

- Frontend: React (cliente web).
- Backend API: Django + DRF.
- Base de datos: PostgreSQL.
- IA: servicio Groq (via backend).
- Almacenamiento de archivos: filesystem local (fase actual), opcion a S3 en futuro.

## 3. Flujo funcional principal

1. Usuario se autentica en frontend.
2. Frontend envia JWT en cada request al backend.
3. Backend valida JWT y permisos.
4. Backend consulta/actualiza PostgreSQL.
5. Para funciones IA, backend llama a Groq.
6. Backend responde JSON al frontend.

## 4. Principios de arquitectura

- Separation of concerns:
  - `apps/users`: autenticacion, perfil, limites.
  - `apps/notebooks`: organizacion de materias.
  - `apps/documents`: carga/procesamiento de archivos.
  - `apps/chat`: conversacion y contexto.
  - `apps/interactions`: tracking historico.
- Source of truth:
  - Estado de proyecto: `docs/03_tracking_plan.md`.
  - Estado tecnico fase 1: `docs/01_fase1_estado.md`.
- API-first:
  - El frontend depende de contratos API versionados.

## 5. Vista de alto nivel

```text
[React Frontend]
      |
      | HTTPS + JWT
      v
[Django/DRF API] -----> [Groq API]
      |
      | ORM
      v
[PostgreSQL]
      |
      v
[Media Files (local)]
```

## 6. Seguridad base

- JWT para autenticacion.
- Permisos por rol (Free, Premium, Admin) en fases siguientes.
- CORS controlado por settings.
- Validacion de entrada con DRF serializers.

## 7. Convenciones de desarrollo

- Cada nueva capacidad debe:
  1. agregar/update documentacion en `docs/`;
  2. incluir tests minimos;
  3. actualizar tracker de fase.

## 8. Criterio para evolucionar arquitectura

Se ajusta arquitectura cuando cambie alguno de estos limites:

- volumen alto de documentos;
- necesidad de procesamiento asincrono pesado;
- requerimiento multi-tenant estricto;
- despliegue cloud con almacenamiento externo.
