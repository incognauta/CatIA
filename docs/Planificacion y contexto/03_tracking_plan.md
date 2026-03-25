# Tracking de Plan de Trabajo

Fecha de inicio: 2026-03-17
Última actualización: 2026-03-24

## Estado por fase

- [x] Fase 1 - Configuración inicial
- [x] Fase 2 - Modelos y base de datos
- [x] Fase 3 - API REST con DRF
- [x] Fase 4 - MVP Híbrido (Notebooks, Documentos, Chat)
  - [x] 4A - ViewSets + Endpoints (1 semana) ✅ COMPLETADA
  - [x] 4B - Procesamiento de archivos + OCR (1 semana) ✅ COMPLETADA
  - [x] 4C - Chat + IA (Groq + RAG) (1 semana) ✅ COMPLETADA
- [ ] Fase 5 - Frontend MVP (React/Vue/Next.js)
  - [ ] 5A - Setup frontend + autenticación
  - [ ] 5B - Interfaz notebooks + documentos
  - [ ] 5C - Chat UI + visualización RAG
- [ ] Fase 6 - Pagos + Escalado (Stripe/MercadoPago + S3)
- [ ] Fase 7 - Features avanzadas
- [ ] Fase 8 - Testing completo
- [ ] Fase 9 - Docker/deploy completo
- [ ] Fase 10 - Optimización/producción

Leyenda:

- `[ ]` no iniciado
- `[~]` en progreso
- `[x]` completado

## Resumen Fase 4 - COMPLETADA ✅

### 4A - ViewSets + Endpoints
- ✅ Models: User, UserProfile, Notebook, Document, ChatMessage
- ✅ Serializers con nested relationships
- ✅ ViewSets con permissions (IsAuthenticated, IsNotebookOwner)
- ✅ Endpoints CRUD para notebooks, documentos, chat
- ✅ 45 tests pasando
- ✅ JWT authentication en lugar de Session

### 4B - Procesamiento de archivos + OCR
- ✅ FileProcessor: validación y extracción de contenido
- ✅ Soporta: PDF, DOCX, TXT, imágenes (PNG, JPG)
- ✅ OCR con pytesseract + pdf2image
- ✅ Endpoint: POST /api/v1/documents/upload/
- ✅ 6 tests new (51 total)
- ✅ Límite de archivo: 10MB
- ✅ Markdown conversion del contenido

### 4C - Chat + IA (Groq + RAG)
- ✅ GroqService: integración Groq API
- ✅ RAG: búsqueda de documentos + context building
- ✅ Modelo: llama-3.1-8b-instant
- ✅ Endpoint: POST /api/v1/chat/ask_ai/
- ✅ Conversation history (últimos 5 mensajes)
- ✅ Token tracking + context documentation
- ✅ 6 tests new (57 total)
- ✅ Error handling para API downtime (503 responses)

## Próxima Fase: Frontend MVP (Fase 5)

Comenzar con diseño de interfaz y selección de stack frontend.

---

## Checklist operativo Fase 1

- [x] Crear estructura Django
- [x] Separar settings por entorno
- [x] Crear apps base
- [x] Definir dependencias iniciales
- [x] Crear `.env` y `.env.example`
- [x] Crear `Dockerfile` backend
- [x] Crear `docker-compose.yml`
- [x] Health endpoint inicial
- [x] `python manage.py check` sin errores
- [x] Levantar DB y backend por Docker
- [x] Ejecutar `migrate` contra PostgreSQL Docker
- [x] Verificar `GET /health/` con respuesta `200 OK`

## Bitácora de progreso

### 2026-03-17

- Cambio:
  - Scaffold de backend Django + apps iniciales.
  - Configuración modular de settings.
  - Instalación de stack base con `psycopg[binary]`.
  - Ajuste de `DATABASE_URL` para local vs Docker.
- Impacto:
  - Base técnica estable para iniciar Fase 2 sin rehacer setup.
- Siguiente paso:
  - Cierre operativo de Fase 1 con Docker local y migraciones reales.

### 2026-03-18

- Cambio:
  - Verificación operativa completada con `docker compose`.
  - Contenedores `db` y `backend` en estado `Up`.
  - Migraciones de Django aplicadas correctamente.
  - Health check confirmado en `http://localhost:8001/health/`.
- Impacto:
  - Fase 1 cerrada y baseline ejecutable validada de punta a punta.
- Siguiente paso:
  - Iniciar Fase 2 con modelo `User` personalizado y `UserProfile`.

### 2026-03-18 (Documentación de estructura)

- Cambio:
  - Se agregó documentación técnica de estructura estable:
    - `05_arquitectura_general.md`
    - `06_estructura_backend.md`
    - `07_contratos_api.md`
    - `08_modelo_datos.md`
- Impacto:
  - Se reduce pérdida de contexto y errores de implementación en Fase 2.
  - Queda definida una base para revisar decisiones con criterio técnico común.
- Siguiente paso:
  - Iniciar Fase 2 siguiendo `08_modelo_datos.md` y `06_estructura_backend.md`.

### 2026-03-17 (Fase 2: Modelos y BD - COMPLETADA)

- Cambio:
  - Configurar `AUTH_USER_MODEL = "users.User"` en settings/base.py.
  - Crear modelo `User` (AbstractUser): subscription_tier, email_verified.
  - Crear modelo `UserProfile` (1-a-1): bio, avatar_url, preferred_language.
  - Signals: auto-crear UserProfile al crear User.
  - Admin customizado para User y UserProfile avec display fields.
  - Tests: user creation, email unique, password hashing, profile signals (8 tests pasan).
  - Migraciones: makemigrations users, resetear BD, migrate.
  - Usuario admin creado (admin / admin123).
- Impacto:
  - Modelos BD mapeados completamente; migraciones ejecutadas.
  - `python manage.py check` sin errores.
  - Admin /admin/ funcional y accesible.
  - Base lista para Fase 3: serializers, views, endpoints API.
- Siguiente paso:
  - Fase 3: Crear serializers, views, y endpoints de autenticación/usuarios.

### 2026-03-24 (Fase 4 - COMPLETADA)

- Cambio:
  - ✅ Fase 4A: Implement all ViewSets (45 tests passing)
    - Nested serializers for models
    - Permission classes (IsAuthenticated, IsNotebookOwner)
    - All CRUD endpoints working
  
  - ✅ Fase 4B: File processing + OCR
    - FileProcessor class with validation
    - Support for PDF, DOCX, TXT, images
    - pytesseract + pdf2image for OCR
    - Markdown conversion
    - upload endpoint with multipart support
    - 6 new tests (51 total)
  
  - ✅ Fase 4C: Groq AI + RAG
    - GroqService with build_rag_context
    - ask_ai endpoint with full RAG pipeline
    - Conversation history support
    - Token tracking
    - 6 new tests (57 total)
    - Model: llama-3.1-8b-instant (rápido y disponible)

- Impacto:
  - Backend MVP completamente funcional
  - Toda la lógica de negocio implementada
  - 57 tests validando funcionalidad end-to-end
  - Docker con todas las dependencias (tesseract, poppler, groq)
  - JWT authentication en todos los endpoints

- Siguiente paso:
  - Fase 5: Implementar Frontend MVP para llevar MVP más cerca de users

---

## Planes Fase 5 - Frontend MVP

### Opciones de stack frontend:

1. **React + Vite** (recomendado para MVP rápido)
   - Bundle build pequeño y rápido
   - HMR (Hot Module Replacement) excelente
   - TypeScript ready
   - Excelente para prototipos

2. **Next.js 14** (si queremos con SSR/SSG)
   - Full-stack (frontend + backend node)
   - Vercel deployment automático
   - Más heavy que Vite pero más features

3. **Vue 3 + Vite** (alternativa más lite)
   - Sintaxis más simple que React
   - Vite build rápido
   - Buen balance entre facilidad y poder

### Herramientas a considerar:

**Componentes UI:**
- Shadcn/ui (headless, muy customizable)
- TailwindCSS (styling rápido)
- Radix UI (accesibilidad)

**Estados/API:**
- TanStack Query (data fetching + caching)
- Zustand (state management, más simple que Redux)
- axios o fetch wrapper (HTTP client)

**Auth:**
- JWT stored in httpOnly cookie
- Endpoint: /api/v1/auth/token/
- Refresh logic built-in

**Markdown/Chat:**
- react-markdown para mostrar respuestas RAG
- Markdown component para preview docs
- Scroll automático en chat

---

