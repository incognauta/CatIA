# 🛠️ Stack Tecnológico - ARCHIVO ARCHIVED

> **Estado:** [ARCHIVED] - Consolidado en `04_decisiones_tecnicas.md` + `05_arquitectura_general.md`.  
> **Razón:** Las razones técnicas y decisiones ya están documentadas en archivos de Progreso.  
> **Consultar:** 
> - `docs/Progreso/04_decisiones_tecnicas.md` para ADRs
> - `docs/Progreso/05_arquitectura_general.md` para componentes

## 📋 Decisiones de Arquitectura

Basado en los objetivos del proyecto y los requerimientos establecidos:

---

## 1️⃣ Backend: Django + Django REST Framework (DRF)

### ✅ Decisión Final: **USAR Django 5.0 + DRF 3.14**

### 🎯 Pros de Django + DRF

#### **Ventajas para el Proyecto:**

1. **🔐 Sistema de Autenticación Robusto Built-in**
   - Sistema de usuarios maduro y battle-tested
   - Permisos granulares (user, group, custom permissions)
   - Password hashing seguro (PBKDF2 por defecto)
   - Sesiones y cookies manejadas automáticamente
   - **Crítico para:** Gestión de usuarios con roles (Free, Premium, Admin)

2. **⚙️ Django Admin Panel**
   - Panel de administración listo para usar
   - Personalizable sin esfuerzo
   - CRUD automático para todos los modelos
   - **Crítico para:** Moderación de contenido, gestión de usuarios, estadísticas

3. **🗄️ ORM Maduro y Potente**
   - Consultas optimizadas automáticamente
   - Migraciones manejadas elegantemente
   - Relaciones complejas fáciles de manejar
   - **Crítico para:** Historial de conversaciones, relaciones usuario-documento-chat

4. **📦 Ecosistema Rico**
   - Miles de paquetes django-* disponibles
   - Comunidad grande y activa
   - Documentación excelente
   - **Útil para:** OCR, pagos (Stripe), caching (Redis), etc.

5. **🛡️ Seguridad por Defecto**
   - CSRF protection
   - SQL injection protection
   - XSS protection
   - Clickjacking protection
   - **Crítico para:** Pasarela de pagos, datos sensibles de usuarios

6. **🔄 Django REST Framework (DRF)**
   - Serialización automática
   - ViewSets y Routers (menos código repetitivo)
   - Browsable API (testing manual fácil)
   - Throttling y permissions built-in
   - **Crítico para:** API REST completa con límites de uso

#### **Casos de Uso Perfectos para Django:**
- ✅ Aplicaciones con **usuarios y autenticación compleja**
- ✅ Proyectos que necesitan **admin panel**
- ✅ Sistemas con **relaciones de datos complejas**
- ✅ Aplicaciones a **largo plazo** (mantenibilidad)
- ✅ Equipos que valoran **convención sobre configuración**

---

### ⚠️ Contras de Django + DRF

1. **🐌 Performance (ligeramente inferior a FastAPI)**
   - Sincrónico por defecto (aunque soporta async en Django 4.1+)
   - ~10-20% más lento que FastAPI en benchmarks puros
   - **Mitigación:** Para este proyecto, la diferencia es insignificante (Groq AI es el cuello de botella, no Django)

2. **📝 Más Boilerplate**
   - Más archivos y estructura (models.py, serializers.py, views.py, urls.py, admin.py)
   - FastAPI tiene menos código para misma funcionalidad
   - **Mitigación:** La estructura organizada ayuda en proyectos grandes

3. **🔧 Menos "Moderno"**
   - No usa type hints nativamente (aunque DRF los soporta)
   - Sintaxis más tradicional vs FastAPI (decoradores async/await everywhere)
   - **Mitigación:** No es un problema para el equipo

4. **📦 Tamaño Mayor**
   - Django es más pesado que FastAPI/Starlette
   - Más dependencias
   - **Mitigación:** En Docker, el tamaño es manejable

---

### 🆚 Comparación Directa: Django vs FastAPI

| Aspecto | Django + DRF | FastAPI (actual) | Ganador para PDF_IA_Rework |
|---------|-------------|------------------|---------------------------|
| **Performance pura** | 7/10 | 10/10 | FastAPI ⚡ |
| **Admin Panel** | 10/10 | 0/10 (no existe) | **Django 🏆** |
| **Auth & Permissions** | 10/10 | 3/10 (manual) | **Django 🏆** |
| **ORM** | 10/10 (Django ORM) | 8/10 (SQLAlchemy) | Django (por convención) |
| **Curva de aprendizaje** | 6/10 (estructura rígida) | 9/10 (muy simple) | FastAPI |
| **Ecosistema** | 10/10 | 7/10 | **Django 🏆** |
| **Desarrollo rápido** | 8/10 | 9/10 | FastAPI |
| **Mantenibilidad** | 9/10 | 8/10 | Django |
| **Type safety** | 5/10 | 10/10 | FastAPI |
| **Docs automáticas** | 8/10 (drf-yasg) | 10/10 (Swagger) | FastAPI |
| **Testing** | 9/10 | 9/10 | Empate |
| **WebSockets** | 7/10 (Channels) | 10/10 (nativo) | FastAPI |
| **Async support** | 7/10 (desde v4.1) | 10/10 | FastAPI |

**TOTAL: Django 9 victorias, FastAPI 7 victorias**

#### 🎯 **Veredicto para PDF_IA_Rework:**
**Django + DRF gana** porque:
- ✅ Admin panel es **crítico** (gestión de usuarios, pagos)
- ✅ Autenticación compleja (Free/Premium/Admin)
- ✅ Relaciones de datos complejas (usuarios → documentos → chats → historial)
- ✅ Pasarela de pagos (necesita seguridad robusta)
- ✅ Largo plazo (el proyecto crecerá)

---

### 🔄 Alternativas Consideradas

#### **Opción B: FastAPI + SQLAdmin + FastAPI-Users**
- **Pros:** Performance superior, type hints, moderno
- **Contras:** Requiere integrar manualmente admin panel, auth compleja, más trabajo inicial
- **Veredicto:** Viable pero más tiempo de desarrollo (30% más)

#### **Opción C: NestJS (TypeScript)**
- **Pros:** TypeScript end-to-end, arquitectura similar a Spring Boot
- **Contras:** Equipo debe aprender nuevo lenguaje, menos librerías para AI/ML
- **Veredicto:** Descartado (cambio de stack muy grande)

#### **Opción D: Flask + Flask-Admin**
- **Pros:** Intermedio entre Django y FastAPI
- **Contras:** Menos features built-in que Django, más manual que FastAPI
- **Veredicto:** Descartado (lo peor de ambos mundos)

---

## 2️⃣ Base de Datos: PostgreSQL 15 (Nueva)

### ✅ Decisión: **PostgreSQL 15 (brand new database)**

#### **Configuración:**
```yaml
Database Name: pdf_ia_rework_db
Host: localhost (Docker)
Port: 5434 (distinto de PDF_IA original: 5433)
User: postgres
Image: pgvector/pgvector:pg15
```

#### **Por qué PostgreSQL:**
1. **pgvector extension** (vectores para embeddings futuros)
2. **JSONB support** (para metadata flexible)
3. **Full-text search** (búsqueda de documentos)
4. **Confiabilidad** (ACID compliant)
5. **Django ORM lo soporta perfectamente**

#### **Esquema Inicial:**
```
Users (Django auth_user extendido)
  ├── UserProfile (avatar, bio, preferences)
  ├── Documents (PDFs, metadata)
  │     └── ChatMessages (historial por documento)
  ├── Notebooks (custom notebooks por usuario)
  ├── Interactions (toda interacción guardada para referencias futuras)
  ├── Subscriptions (Free, Premium, Enterprise)
  └── ActivityLogs (tracking de uso)
```

---

## 3️⃣ Frontend: React 18 + Material-UI (Nuevo Diseño)

### ✅ Decisión: **React 18 + MUI + Diseño Nuevo (basado en mockup)**

#### **Stack Frontend:**
- **Framework:** React 18.2
- **Build Tool:** Vite 5.0 (más rápido que Webpack)
- **UI Library:** Material-UI 5.15 (mantener consistencia)
- **Styling:** Emotion (CSS-in-JS, viene con MUI)
- **State Management:** React Context API + useState (sin Redux por ahora)
- **Routing:** React Router v6
- **Forms:** React Hook Form + Yup (validación)
- **API Client:** Axios 1.6
- **Animations:** Framer Motion (opcional, para transiciones suaves)

#### **Estructura de Componentes (Nueva):**
```
frontend/src/
├── components/
│   ├── auth/
│   │   ├── LoginForm.jsx
│   │   ├── RegisterForm.jsx
│   │   └── ProtectedRoute.jsx
│   ├── dashboard/
│   │   ├── DashboardLayout.jsx
│   │   ├── Sidebar.jsx
│   │   ├── Topbar.jsx
│   │   └── UserMenu.jsx
│   ├── documents/
│   │   ├── DocumentList.jsx
│   │   ├── DocumentCard.jsx
│   │   ├── DocumentUpload.jsx
│   │   └── DocumentViewer.jsx
│   ├── chat/
│   │   ├── ChatWindow.jsx
│   │   ├── MessageBubble.jsx
│   │   ├── ChatInput.jsx
│   │   └── ChatHistory.jsx
│   ├── notebooks/
│   │   ├── NotebookList.jsx
│   │   ├── NotebookCard.jsx
│   │   └── CreateNotebookDialog.jsx
│   ├── interactions/
│   │   ├── InteractionTimeline.jsx  # NUEVO: Historial de todo
│   │   └── InteractionDetail.jsx
│   └── common/
│       ├── LoadingSpinner.jsx
│       ├── ErrorBoundary.jsx
│       └── ConfirmDialog.jsx
├── pages/
│   ├── Login.jsx
│   ├── Register.jsx
│   ├── Dashboard.jsx
│   ├── DocumentsPage.jsx
│   ├── ChatPage.jsx
│   ├── NotebooksPage.jsx
│   ├── ProfilePage.jsx
│   └── SubscriptionPage.jsx
├── services/
│   ├── api.js          # Axios instance
│   ├── auth.js         # Login, register, logout
│   ├── documents.js    # CRUD documentos
│   ├── chat.js         # Chat endpoints
│   └── notebooks.js    # Notebooks endpoints
├── context/
│   ├── AuthContext.jsx
│   └── ThemeContext.jsx
├── hooks/
│   ├── useAuth.js
│   ├── useDocuments.js
│   └── useChat.js
├── utils/
│   ├── constants.js
│   ├── validators.js
│   └── formatters.js
├── App.jsx
└── main.jsx
```

#### **Diseño basado en mockup del usuario:**
- Esperando mockup para definir:
  - Color palette
  - Typography
  - Component styles
  - Layout specifics

---

## 4️⃣ Autenticación & Autorización

### ✅ Stack de Auth:

#### **Backend:**
```python
# Instalaciones
pip install djangorestframework-simplejwt
pip install django-cors-headers
```

**Componentes:**
1. **djangorestframework-simplejwt:** JWT tokens con refresh
2. **Django permissions:** Custom permissions por role
3. **Django Groups:** Free, Premium, Admin

#### **Flujo de Autenticación:**
```
1. Usuario → Register (email, password, username)
2. Backend → Crea User + UserProfile
3. Backend → Asigna role="FREE" por defecto
4. Backend → Retorna access_token + refresh_token
5. Frontend → Guarda tokens en localStorage
6. Frontend → Incluye "Authorization: Bearer {token}" en todas las requests
7. Backend → Valida token en cada endpoint
8. Token expira → Frontend usa refresh_token para obtener nuevo access_token
```

#### **Roles y Permisos:**

| Role | Max PDFs | AI Calls/día | Features |
|------|----------|--------------|----------|
| **FREE** | 5 | 20 | Chat básico, 1 notebook |
| **PREMIUM** | Ilimitado | 200 | Chat avanzado, notebooks ilimitados, export |
| **ADMIN** | Ilimitado | Ilimitado | Todo + panel admin |

---

## 5️⃣ Notebooks & Gestión de Interacciones

### 🎯 **Prioridad #1: Sistema de Notebooks + Tracking de Interacciones**

#### **Modelo de Notebooks:**
```python
class Notebook(models.Model):
    # Básico
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)  # Ej: "Cálculo II"
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    
    # Visual
    color = models.CharField(max_length=7, default='#1976d2')  # Hex
    icon = models.CharField(max_length=50, default='📚')  # Emoji
    
    # Metadata
    is_default = models.BooleanField(default=False)  # Los 4 originales
    is_public = models.BooleanField(default=False)  # Compartir con otros
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Stats
    total_documents = models.IntegerField(default=0)
    total_interactions = models.IntegerField(default=0)
```

#### **Modelo de Interacciones (CLAVE):**
```python
class Interaction(models.Model):
    """
    Registra TODA interacción del usuario con documentos/notebooks.
    Esto permitirá:
    - Historial completo de uso
    - Patrones de aprendizaje
    - Recomendaciones personalizadas
    - Analytics de uso
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notebook = models.ForeignKey(Notebook, on_delete=models.CASCADE)
    document = models.ForeignKey(Document, on_delete=models.SET_NULL, null=True)
    
    # Tipo de interacción
    interaction_type = models.CharField(max_length=50, choices=[
        ('UPLOAD', 'Subió documento'),
        ('VIEW', 'Vió documento'),
        ('SUMMARY', 'Generó resumen'),
        ('CHAT', 'Preguntó en chat'),
        ('EXPORT', 'Exportó contenido'),
        ('SHARE', 'Compartió documento'),
        ('HIGHLIGHT', 'Marcó texto importante'),
        ('NOTE', 'Añadió nota'),
    ])
    
    # Datos de la interacción
    content = models.TextField(blank=True)  # Ej: pregunta hecha, texto marcado
    ai_response = models.TextField(blank=True)  # Respuesta de la IA
    metadata = models.JSONField(default=dict)  # Datos extra flexibles
    
    # Context preservation (CLAVE para referencias futuras)
    context_snapshot = models.JSONField(default=dict)  # Estado del notebook en ese momento
    related_interactions = models.ManyToManyField('self', blank=True)  # Interacciones relacionadas
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Analytics
    tokens_used = models.IntegerField(default=0)
    processing_time = models.FloatField(default=0.0)  # Segundos
```

#### **Por qué este modelo de Interacciones es poderoso:**

1. **📚 Referencias Futuras:**
   - El chatbot puede consultar interacciones previas
   - Ejemplo: "Como vimos la semana pasada cuando estudiabas derivadas..."

2. **🧠 Contexto Acumulativo:**
   - El sistema "recuerda" cómo el usuario estudia
   - Adapta respuestas según patrones previos

3. **📊 Analytics Avanzados:**
   - ¿Qué temas estudia más?
   - ¿En qué horarios es más activo?
   - ¿Qué tipo de preguntas hace más?

4. **🎯 Recomendaciones:**
   - "Basado en tu estudio de Cálculo I, te recomendamos estos recursos de Cálculo II"

5. **🔍 Búsqueda Contextual:**
   - Buscar en todo el historial de interacciones
   - "Muéstrame todas las veces que pregunté sobre integrales"

---

## 6️⃣ OCR & Procesamiento Avanzado de Documentos

### ✅ Stack de OCR (para implementar más adelante):

#### **Herramientas Recomendadas:**

1. **Tesseract OCR (Open Source)**
   ```bash
   pip install pytesseract
   apt-get install tesseract-ocr
   apt-get install tesseract-ocr-spa  # Español
   ```
   - **Pros:** Gratis, multi-idioma, activamente mantenido
   - **Contras:** Precisión media (85-90%)
   - **Uso:** PDFs escaneados, imágenes de texto

2. **Google Cloud Vision API (Pago)**
   ```bash
   pip install google-cloud-vision
   ```
   - **Pros:** Alta precisión (95%+), reconoce texto en imágenes complejas
   - **Contras:** Costo (€1.50 por 1000 imágenes)
   - **Uso:** Documentos importantes, handwriting

3. **AWS Textract (Pago)**
   ```bash
   pip install boto3
   ```
   - **Pros:** Extrae tablas y formularios estructurados
   - **Contras:** Costo similar a Google
   - **Uso:** Facturas, formularios, tablas

#### **Estrategia Híbrida:**
```python
# apps/documents/services/ocr_service.py

class OCRService:
    def extract_text(self, file, source_type='pdf'):
        # 1. Intentar extracción nativa (PDF digital)
        if source_type == 'pdf':
            text = self._extract_pdf_native(file)
            if self._is_valid_text(text):
                return text
        
        # 2. Si falla, usar OCR (PDF escaneado)
        # Empezar con Tesseract (gratis)
        text = self._extract_tesseract(file)
        
        # 3. Si confianza < 80%, usar Google Vision (pago)
        if self._confidence_score(text) < 0.8:
            text = self._extract_google_vision(file)
        
        return text
```

#### **Tipos de Archivos Soportados (futuro):**
- ✅ PDF (nativo + escaneado)
- ✅ DOCX (python-docx)
- ✅ PPTX (python-pptx)
- ✅ Imágenes (JPG, PNG) → OCR
- ✅ Excel (pandas)
- ⏳ Audio (transcripción con Whisper API)

---

## 7️⃣ IA & Modelos de Lenguaje

### ✅ Stack de IA:

#### **LLM Principal: Groq AI**
```python
# Mantener configuración actual
Model: llama-3.1-8b-instant
API: Groq Cloud
Cost: Gratis (por ahora, tier gratuito)
```

**Funcionalidades:**
- Resúmenes de documentos
- Chat conversacional con contexto
- Generación de preguntas de estudio
- Explicaciones de conceptos

#### **Embeddings (para futuro):**
```python
# Para búsqueda semántica
Option A: sentence-transformers (local, gratis)
  - Model: all-MiniLM-L6-v2
  - Pros: Gratis, rápido
  - Contras: Precisión media

Option B: OpenAI Embeddings (pago)
  - Model: text-embedding-3-small
  - Pros: Alta precisión
  - Contras: $0.02 por 1M tokens
```

#### **Almacenamiento de Vectores:**
```python
# pgvector extension en PostgreSQL
# Ya incluido en imagen pgvector/pgvector:pg15

# Ejemplo de uso:
from pgvector.django import VectorField

class DocumentChunk(models.Model):
    document = models.ForeignKey(Document)
    content = models.TextField()
    embedding = VectorField(dimensions=384)  # Dimensiones del modelo
```

---

## 8️⃣ Pasarela de Pagos

### ✅ Opción Recomendada: **Stripe**

#### **Por qué Stripe:**
1. ✅ API excelente (bien documentada)
2. ✅ Dashboard completo
3. ✅ Soporta suscripciones recurrentes
4. ✅ Webhooks para eventos
5. ✅ Modo test completo
6. ✅ Integración con Django fácil (dj-stripe)

#### **Instalación:**
```bash
pip install stripe
pip install dj-stripe  # Opcional: wrapper Django
```

#### **Planes de Suscripción:**

| Plan | Precio/mes | Features |
|------|-----------|----------|
| **Free** | €0 | 5 PDFs, 20 AI calls/día, 1 notebook |
| **Premium** | €9.99 | PDFs ilimitados, 200 AI calls/día, notebooks ilimitados |
| **Enterprise** | €29.99 | Todo ilimitado + API access + soporte prioritario |

#### **Implementación:**
```python
# apps/subscriptions/models.py
class Subscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    stripe_subscription_id = models.CharField(max_length=255)
    plan = models.CharField(max_length=50, choices=[...])
    status = models.CharField(max_length=50)  # active, canceled, past_due
    current_period_end = models.DateTimeField()
```

---

## 9️⃣ Infraestructura & DevOps

### ✅ Stack de Infraestructura:

#### **Contenedorización:**
```yaml
Docker 24.0
docker-compose 2.20
```

#### **Servicios Docker:**
```
1. db (PostgreSQL 15)
2. backend (Django)
3. frontend (React)
4. redis (Cache & Celery broker) - NUEVO
5. celery (Tareas asíncronas) - NUEVO
```

#### **Redis + Celery (para tareas pesadas):**
```python
# Casos de uso:
- Procesamiento de PDFs grandes (asyncrónico)
- Generación de resúmenes (cola de jobs)
- Envío de emails (bienvenida, notificaciones)
- Cálculo de estadísticas (nightly jobs)

# Instalación:
pip install celery
pip install redis
```

#### **Estructura Docker Compose:**
```yaml
version: '3.8'

services:
  db:
    image: pgvector/pgvector:pg15
    ports: ["5434:5432"]
  
  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
  
  backend:
    build: ./backend
    ports: ["8001:8000"]
    depends_on: [db, redis]
  
  celery:
    build: ./backend
    command: celery -A config worker -l info
    depends_on: [redis, db]
  
  frontend:
    build: ./frontend
    ports: ["5174:5173"]
```

---

## 🔟 Testing & Quality Assurance

### ✅ Stack de Testing:

```python
# Backend
pytest==7.4.3
pytest-django==4.7.0
pytest-cov==4.1.0
factory-boy==3.3.0  # Para crear fixtures
faker==20.1.0  # Datos fake para tests

# Frontend
@testing-library/react
@testing-library/jest-dom
vitest  # Más rápido que Jest
```

#### **Cobertura Mínima:**
- Backend: 80%
- Frontend: 70%

#### **Tipos de Tests:**
1. **Unit tests:** Funciones individuales
2. **Integration tests:** API endpoints
3. **E2E tests (opcional):** Playwright/Cypress

---

## 📦 Dependencias Completas

### **Backend (requirements.txt):**
```txt
# Core
Django==5.0.1
djangorestframework==3.14.0
djangorestframework-simplejwt==5.3.1

# Database
psycopg2-binary==2.9.9
dj-database-url==2.1.0

# CORS & Security
django-cors-headers==4.3.1
python-decouple==3.8

# File handling
Pillow==10.2.0
PyPDF2==3.0.1

# AI & ML
groq==0.4.1
# sentence-transformers==2.2.2  # Futuro: embeddings

# OCR (futuro)
# pytesseract==0.3.10
# google-cloud-vision==3.5.0

# Payments
stripe==8.0.0
# dj-stripe==2.8.3  # Opcional

# Tasks & Caching
celery==5.3.4
redis==5.0.1
django-redis==5.4.0

# API Documentation
drf-yasg==1.21.7

# Utilities
python-slugify==8.0.1
django-filter==24.1

# Development
django-extensions==3.2.3
ipython==8.18.1

# Testing
pytest==7.4.3
pytest-django==4.7.0
pytest-cov==4.1.0
factory-boy==3.3.0
faker==20.1.0

# Production
gunicorn==21.2.0
whitenoise==6.6.0  # Static files
```

### **Frontend (package.json):**
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.21.0",
    "@mui/material": "^5.15.0",
    "@mui/icons-material": "^5.15.0",
    "@emotion/react": "^11.11.3",
    "@emotion/styled": "^11.11.0",
    "axios": "^1.6.5",
    "react-hook-form": "^7.49.3",
    "yup": "^1.3.3",
    "framer-motion": "^10.18.0",
    "react-dropzone": "^14.2.3"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.2.1",
    "vite": "^5.0.10",
    "@testing-library/react": "^14.1.2",
    "vitest": "^1.1.1"
  }
}
```

---

## 🎯 Resumen de Decisiones

| Tecnología | Decisión | Razón |
|------------|----------|-------|
| **Backend** | Django 5.0 + DRF | Admin panel, auth robusta, ORM maduro |
| **Base de Datos** | PostgreSQL 15 (nueva) | pgvector, JSONB, full-text search |
| **Frontend** | React 18 + MUI (nuevo) | Mockup del usuario, mantener familiaridad |
| **Auth** | djangorestframework-simplejwt | JWT con refresh, standard de DRF |
| **LLM** | Groq AI (llama-3.1) | Gratis, rápido, suficiente para MVP |
| **OCR** | Tesseract + Google Vision (futuro) | Híbrido: gratis + pago según precisión |
| **Pagos** | Stripe | API excelente, soporta suscripciones |
| **Caché** | Redis | Celery broker + cache de queries |
| **Tasks** | Celery | Procesamiento asíncrono |
| **Testing** | pytest + pytest-django | Standard en Django |
| **Docs API** | drf-yasg | Swagger automático |

---

## ⏭️ Próximos Pasos

1. ✅ **Stack definido** (este documento)
2. ⏳ **Esperando mockup del frontend** (del usuario)
3. ⏳ **Definir prioridades detalladas:**
   - Fase 1: Auth + Users + Notebooks básicos
   - Fase 2: Documents + Upload + Storage
   - Fase 3: Chat + Interactions tracking
   - Fase 4: UI completa basada en mockup
   - Fase 5: OCR + Features avanzadas
   - Fase 6: Pagos + Suscripciones

---

## 📝 Notas del Usuario

> "La idea es llevarles un soporte de tal manera que toda la interacción de los libros sea guardada para poder usar como referencia a futuros usos del notebook o del chatbot"

✅ **Implementado** mediante el modelo `Interaction` que registra:
- Cada pregunta hecha
- Cada documento visto
- Cada resumen generado
- Metadata de contexto
- Relaciones entre interacciones

Esto permitirá al chatbot:
- Referenciar conversaciones pasadas
- Entender patrones de estudio del usuario
- Dar recomendaciones personalizadas
- Mostrar timeline de aprendizaje

---

**¿Listo para empezar?** 🚀

Siguiente paso: Esperar mockup del frontend y definir orden de implementación de las fases.
