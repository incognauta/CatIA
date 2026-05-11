# 09. Pasos, Decisiones y Ejecución por Fase

**Propósito:** Documento unificado que registra el paso a paso de cada fase, decisiones arquitectónicas tomadas, herramientas utilizadas, y explicación del "por qué" de cada decisión. Serve como guía de referencia para entender la evolución del proyecto.

---

## Índice de Fases

- [Fase 1: Scaffold y Setup](#fase-1-scaffold-y-setup)
- [Fase 2: Modelos y Base de Datos](#fase-2-modelos-y-base-de-datos)
- [Fase 3: Autenticación y Autorización](#fase-3-autenticación-y-autorización) *(pendiente)*
- [Fase 4: Endpoints API](#fase-4-endpoints-api) *(pendiente)*
- [Fase 5: Integración IA y Servicios](#fase-5-integración-ia-y-servicios) *(pendiente)*

---

## Fase 1: Scaffold y Setup

**Estado:** ✅ Completada (17 de marzo 2026)

### ¿QUÉ se hizo?

Establecer una base sólida de proyecto Django con infraestructura lista para desarrollo y producción.

1. **Crear estructura Django:**
   - Proyecto `config` con aplicaciones modular en `apps/`
   - 6 aplicaciones iniciales: `users`, `notebooks`, `documents`, `chat`, `interactions`, `core`
   - Ver: [docs/06_estructura_backend.md](06_estructura_backend.md) para detalle de carpetas

2. **Configurar base de datos PostgreSQL:**
   - Versión: 15 con extensión pgvector
   - Conexión via Docker: `db:5432`
   - Local dev: `localhost:5434`
   - Driver: `psycopg[binary]` v3.2.3 (moderno, Python 3.13 compatible)

3. **Dockerizar la aplicación:**
   - Backend en `python:3.12-slim`
   - Compose con servicios: `db` (PostgreSQL) + `backend` (Django)
   - Gunicorn listo para producción

### ¿CÓMO se hizo?

| Paso | Comando / Acción | Resultado |
|------|------------------|-----------|
| 1 | `django-admin startproject config` | Proyecto creado con asgi/wsgi |
| 2 | `python manage.py startapp` × 6 | Apps creadas en `apps/` |
| 3 | Split settings en `base.py`, `development.py`, `production.py` | Configuración modular, sans hardcode |
| 4 | `pip install -r requirements.txt` | 20 dependencias instaladas (Django, DRF, JWT, CORS, psycopg, etc) |
| 5 | Crear `.env` y `docker-compose.yml` | Infraestructura Docker lista |
| 6 | `docker compose up` + `python manage.py migrate` | BD inicializada, migraciones aplicadas |
| 7 | `curl http://localhost:8000/health/` | Health check positivo: `{"status": "ok"}` |

### ¿QUÉ se usó?

**Stack tecnológico Fase 1:**
- **Framework:** Django 5.0.6 + Django REST Framework 3.15.2
- **BD:** PostgreSQL 15 + psycopg v3
- **Auth:** djangorestframework-simplejwt (JWT + refresh tokens)
- **CORS:** django-cors-headers 4.4.0
- **Entorno:** Docker Compose v2, python-decouple, dj-database-url

**Por qué estas herramientas:**
- **Django + DRF** vs FastAPI: DRF tiene mejor soporte para user management, admin, migraciones automáticas
- **psycopg v3** vs psycopg2: Moderno, tipo-seguro, mejor Python 3.13 support
- **JWT + refresh:** Standard en APIs REST, permite auth stateless + seguridad mejorada
- **Compose:** Reproducibilidad local ≈ producción, evita "works on my machine"

### Por qué así

- ✅ Migraciones automáticas de Django = versionado de BD sin SQL manual
- ✅ Split settings = dev/prod sin colisiones
- ✅ CORS + JWT = Frontend (Vue/React) puede consumir API desde otro origen
- ✅ Docker = ambiente idéntico en laptop, CI/CD, servidor

---

## Fase 2: Modelos y Base de Datos

**Estado:** ✅ Completada (17 de marzo 2026)

### ¿QUÉ se hace?

Crear la estructura de datos que soportará toda la lógica del sistema. Endpoint para datos sin API aún.

1. **User personalizado:**
   - Reemplazar User por defecto de Django con `AUTH_USER_MODEL = 'apps.users.User'`
   - Extender `AbstractUser` para mantener funcionalidad existente (password hashing, permissions, etc)
   - Campo nuevo: `subscription_tier` (FREE|PREMIUM|ADMIN), `email_verified` (booleano)
   - Ver: [docs/08_modelo_datos.md](08_modelo_datos.md#user) para campos exactos

2. **UserProfile (1-a-1 con User):**
   - Datos adicionales: `bio`, `avatar_url`, `preferred_language`, `created_at`, `subscription_expires_at`
   - Signal automático: crear Profile al crear User
   - Nunca acceder a profile manualmente—siempre disponible via `user.userprofile`

3. **Migraciones iniciales:**
   - Generar con `python manage.py makemigrations`
   - Aplicar con `python manage.py migrate`
   - Crear usuario admin para acceso a `/admin/`

4. **Admin setup:**
   - Registrar `User` y `UserProfile` en `admin.py`
   - Permitir CRUD desde interfaz web (sin API aún)

5. **Tests básicos:**
   - User: email único, username requerido, password hashing
   - Profile: creación automática, cascada al eliminar User

### ¿CÓMO se hace?

#### Paso 2.1: Configurar AUTH_USER_MODEL

**Archivo:** [config/settings/base.py](../backend/config/settings/base.py)

```python
# Apuntar a nuestro User personalizado
# Ver: 08_modelo_datos.md#custom-user-strategy para explicación
AUTH_USER_MODEL = 'apps.users.User'
```

**Por qué:** Sin esto, Django sigue usando su User por defecto. Cambiar después es 100x más difícil (migraciones complejas).

---

#### Paso 2.2: Crear User y UserProfile en models.py

**Archivo:** [apps/users/models.py](../backend/apps/users/models.py)

Estructura esperada:
- Clase `User(AbstractUser)`: hereda todo (password, permissions, etc), agrega custom fields
- Clase `UserProfile(models.Model)`: relación 1-a-1, datos adicionales
- Función `create_profile_signal`: signal que auto-crea Profile al guardar User

**Referencia:** [08_modelo_datos.md#User](08_modelo_datos.md#user) (campos exactos, validaciones, constraints)

---

#### Paso 2.3: Registrar en admin.py

**Archivo:** [apps/users/admin.py](../backend/apps/users/admin.py)

Estructura esperada:
- Clase `UserAdmin(admin.ModelAdmin)`: personalizar vista en admin (mostrar subscription_tier, email_verified)
- Clase `UserProfileInline`: mostrar perfil dentro de User admin
- Registrar ambas en `admin.site.register()`

**Referencia:** [06_estructura_backend.md#Admin Pattern](06_estructura_backend.md#admin-pattern)

---

#### Paso 2.4: Generar y aplicar migraciones

```bash
# Desde /backend/
python manage.py makemigrations users
python manage.py migrate
```

**Esperado:**
- Archivo `apps/users/migrations/0001_initial.py` generado
- Tablas `users_user` y `users_userprofile` creadas en PostgreSQL
- `python manage.py check` sin errores

---

#### Paso 2.5: Tests básicos

**Archivo:** [apps/users/tests.py](../backend/apps/users/tests.py)

Estructura esperada:
- Test: User con email única (IntegrityError si se repite)
- Test: UserProfile creada automáticamente
- Test: Password hashed (nunca en plaintext)
- Test: Query eficiente via `user.userprofile.bio`

**Referencia:** [06_estructura_backend.md#Testing Pattern](06_estructura_backend.md#testing-pattern)

---

#### Paso 2.6: Validar Fase 2

```bash
python manage.py check                    # √ Sin errores
python manage.py test apps.users.tests    # √ Todos los tests pasan
python manage.py runserver
# Acceder a http://localhost:8000/admin/ y crear usuario de prueba
```

**Criterio de éxito:**
- ✅ User y Profile modelos activos en BD
- ✅ Admin funcional (create/edit users)
- ✅ Tests pasan
- ✅ `python manage.py check` sin warnings

### ¿QUÉ se usa?

| Concepto | Herramienta | Razón |
|----------|------------|-------|
| User base | `AbstractUser` | No reinventar contraseña/permisos/admin |
| Relación 1-a-1 | `OneToOneField` | Integridad referencial: User ↔ Profile |
| Auto-create | `signals.post_save` | Transparencia: Profile existe siempre |
| Migraciones | Django ORM | Versionadas, reversibles, SQL auto-generado |
| Admin | `ModelAdmin` | CRUD sin código API aún |
| Tests | `TestCase` | Validar constraints (unique, required, etc) |

**Por qué así:**

- ✅ `AbstractUser` vs custom desde cero: Hereda permisos, groups, password hashing—probado en producción
- ✅ Signal `post_save`: Garantiza Profile siempre existe sin código duplicado
- ✅ Migraciones: Revertibles, versionables, reutilizables en CI/staging/prod
- ✅ Admin primero: Validar modelos antes de construir API (feedback rápido)

### Decisión Arquitectónica: AUTH_USER_MODEL desde Day 1

**Alternativa rechazada:** Usar User por defecto + personalizar después
- ❌ Cambiar AUTH_USER_MODEL en prod: requiere reescribir todo referenciado a User (migraciones de datos)
- ❌ FK a User.id codificadas en otras tablas: imposible reapuntar sin migración compleja

**Alternativa elegida:** Custom User NOW
- ✅ Costo inicial: una migración
- ✅ Costo futuro: cero (ya está customizado)
- ✅ Flexibilidad: agregar campos sin "tech debt"

---

## Fase 3: Autenticación y Autorización

**Estado:** ✅ Completada (18 de marzo 2026)

### ¿QUÉ se hace?

Crear endpoints REST autenticados para que clientes (frontend, apps, etc) consuman la API de usuarios.

1. **Serializers:**
   - `UserSerializer`: serializar User (username, email, subscription_tier)
   - `UserProfileSerializer`: perfil (bio, avatar_url, preferred_language)
   - `RegisterSerializer`: validar registro (email único, password confirmation)
   - `LoginSerializer`: validar login (email + password)
   - Ver: [docs/07_contratos_api.md#auth-endpoints](07_contratos_api.md#auth-endpoints) para esquemas exactos

2. **Views:**
   - `RegisterView`: POST /api/v1/auth/register/ (anónimo)
   - `LoginView`: POST /api/v1/auth/login/ (retorna JWT tokens)
   - `UserMeView`: GET /api/v1/users/me/ (perfil autenticado)
   - `UserListView`: GET /api/v1/users/ (admin)
   - Ver: [docs/06_estructura_backend.md#views-pattern](06_estructura_backend.md#views-pattern)

3. **URLs:**
   - Crear `apps/users/urls.py`
   - Registrar en `config/urls.py` bajo `/api/v1/`
   - Ver: [docs/07_contratos_api.md](07_contratos_api.md) para rutas

4. **Permisos:**
   - `IsAuthenticated` para /me/ y /api/v1/users/
   - `AllowAny` para /register/ y /login/
   - Ver: [docs/05_arquitectura_general.md#security](05_arquitectura_general.md#security)

5. **Tests:**
   - Registro: email único, password match, User + Profile creados
   - Login: credenciales, tokens retornados
   - /me/: retorna perfil del usuario autenticado
   - Protegido sin token: 401 Unauthorized

### ¿CÓMO se hace?

#### Paso 3.1: Crear Serializers (`apps/users/serializers.py`)

Estructura esperada:
- `UserSerializer(serializers.ModelSerializer)`: serializar User
- `UserProfileSerializer`: serializar UserProfile
- `RegisterSerializer`: validar email único, passwords match, create user
- `LoginSerializer`: validar credenciales existentes

**Referencia:** [docs/07_contratos_api.md#register](07_contratos_api.md#register) (campos exactos)

---

#### Paso 3.2: Crear Views (`apps/users/views.py`)

Estructura esperada:
- `RegisterView(generics.CreateAPIView)`: POST /auth/register/, permite anónimos
- `LoginView(generics.GenericAPIView)`: POST /auth/login/, retorna tokens
- `UserMeView(generics.RetrieveUpdateAPIView)`: GET/PUT /users/me/, requiere auth
- `UserListView(generics.ListAPIView)`: GET /users/, solo admin

**Referencia:** [docs/06_estructura_backend.md#views-pattern](06_estructura_backend.md#views-pattern)

---

#### Paso 3.3: Crear URLs (`apps/users/urls.py`)

Estructura esperada:
```python
# apps/users/urls.py
from django.urls import path
from .views import RegisterView, LoginView, UserMeView, UserListView

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('users/me/', UserMeView.as_view(), name='user-me'),
    path('users/', UserListView.as_view(), name='user-list'),
]
```

Luego en `config/urls.py`:
```python
path('api/v1/', include('apps.users.urls')),
```

**Referencia:** [docs/07_contratos_api.md](07_contratos_api.md)

---

#### Paso 3.4: Agregar Tests en `apps/users/tests.py`

Agregar test cases:
- `TestRegisterView`: POST /auth/register/ válido → User + Profile creados, 201
- `TestRegisterValidation`: email duplicado → 400; passwords no match → 400
- `TestLoginView`: POST /auth/login/ válido → access_token + refresh_token
- `TestLoginInvalid`: credenciales incorrectas → 401
- `TestUserMeView`: GET /users/me/ autenticado → retorna perfil; sin token → 401
- `TestPermissions`: endpoint protegido sin auth → 401

**Referencia:** [docs/06_estructura_backend.md#testing-pattern](06_estructura_backend.md#testing-pattern)

---

#### Paso 3.5: Validar Fase 3

```bash
python manage.py check                    # √ Sin errores
python manage.py test apps.users.tests    # √ Todos tests pasan
python manage.py runserver
# Probar: curl POST http://localhost:8000/api/v1/auth/register/ ...
```

**Criterio de éxito:**
- ✅ POST /api/v1/auth/register/ funciona (emails únicos)
- ✅ POST /api/v1/auth/login/ retorna {"access": "...", "refresh": "..."}
- ✅ GET /api/v1/users/me/ con token retorna {"id": ..., "username": ...}
- ✅ GET /api/v1/users/me/ sin token retorna 401
- ✅ Tests pasan (registro, login, permisos)
- ✅ `python manage.py check` sin issues

### ¿QUÉ se usa?

| Concepto | Herramienta | Razón |
|----------|------------|-------|
| Serialización | `ModelSerializer` | Convertir modelo ↔ JSON automáticamente |
| Validación | DRF validators | Email, password constraints, boilerplate reducido |
| Views | `generics.CreateAPIView`, `RetrieveUpdateAPIView` | Pre-construidas, HTTP 201/200/401 automático |
| Autenticación | `JWTAuthentication` (SimpleJWT) | Tokens stateless, refresh automático |
| Permisos | `IsAuthenticated`, `AllowAny` | Decorator-based, granular |
| Tests | `APITestCase` de DRF | Simula HTTP real (headers, tokens, status) |

**Por qué así:**

- ✅ `ModelSerializer`: Boilerplate -80% vs custom serializers
- ✅ JWT + SimpleJWT: Standard en APIs REST, refresh tokens built-in
- ✅ Generics: Views en 5 líneas vs 50 en FastAPI
- ✅ APITestCase: Tests que simulan clientes reales (con headers, tokens)

### Decisión Arquitectónica: JWT Stateless

**Alternativa rechazada:** Sesiones backend (Django default)
- ❌ Requiere DB lookup por request (overhead)
- ❌ No funciona bien entre múltiples dispositivos
- ❌ Logout requiere lista negra (stateful)

**Alternativa elegida:** JWT con SimpleJWT
- ✅ Token self-contained (verificable por firma)
- ✅ Frontend almacena localmente (localStorage/sessionStorage)
- ✅ Refresh token permite rotate sin re-login
- ✅ Stateless: DB no verifica token cada request

---

## Fase 4: Endpoints API

**Estado:** 📋 Planificada

### ¿QUÉ se hará?

*Será documentado al ejecutar*

### ¿CÓMO se hará?

*Será documentado al ejecutar*

### ¿QUÉ se usará?

*Será documentado al ejecutar*

---

## Fase 5: Integración IA y Servicios

**Estado:** 📋 Planificada

### ¿QUÉ se hará?

*Será documentado al ejecutar*

### ¿CÓMO se hará?

*Será documentado al ejecutar*

### ¿QUÉ se usará?

*Será documentado al ejecutar*

---

## Referencias Cruzadas

- **Tech Decisions:** [docs/04_decisiones_tecnicas.md](04_decisiones_tecnicas.md)
- **Data Model:** [docs/08_modelo_datos.md](08_modelo_datos.md)
- **Backend Structure:** [docs/06_estructura_backend.md](06_estructura_backend.md)
- **API Contracts:** [docs/07_contratos_api.md](07_contratos_api.md)
- **Architecture:** [docs/05_arquitectura_general.md](05_arquitectura_general.md)

---

**Última actualización:** 17 de marzo 2026
