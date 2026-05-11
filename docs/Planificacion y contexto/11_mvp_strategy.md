# 11. MVP Strategy - Visión Integral del Proyecto

**Propósito:** Conectar objetivo, arquitectura, backend, frontend y fases de implementación en un plan cohesivo.

**Fecha:** 24 de marzo 2026
**Estado:** Estrategia propuesta para aprobación

---

## 1. VISIÓN DEL MVP (1 mes)

**Objetivo Original:**
> Aplicación de chat con documentos usando IA. Usuario: sube archivo → IA procesa → chatea sobre contenido.

**MVP Realista (Fase 4-6):**
```
Semana 1 (Fase 4A): Backend - Modelos + API CRUD
├─ Notebook CRUD (crear, editar, listar)
├─ Document CRUD (crear, listar, deletar - sin PDF aún)
├─ Chat CRUD (crear mensaje, historial)
└─ Permisos + tests

Semana 2 (Fase 4B): Backend - Procesamiento de archivos
├─ PDF upload a storage local (no S3 aún)
├─ Text extraction (pytesseract + pdfplumber)
├─ Markdown conversion
└─ Celery async tasks

Semana 3 (Fase 4C): Backend - Integración IA
├─ Groq LLM integration
├─ Chat con contexto de documento
├─ Response + token tracking
└─ Tests de IA

Semana 4 (Fase 5-6): Frontend + Pagos
├─ UI básica (React/Vue)
├─ Upload + Preview
├─ Chat interface
├─ Auth (JWT)
├─ Stripe pagos
└─ Deploy

TOTAL: MVP funcional en 4 semanas.
```

---

## 2. ESTADO ACTUAL (Hoy 24-03-2026)

### ✅ COMPLETADO

| Fase | Componentes | Estado |
|------|-----------|--------|
| **1** | Django scaffold, Docker, settings split | ✅ |
| **2** | User + UserProfile models, migrations, admin | ✅ |
| **3** | Auth endpoints (register, login), JWT tokens | ✅ |

### 🚀 ESTADO BACKEND

```
Backend estructura:
├── apps/
│   ├── users/          ✅ Completo (register, login, me)
│   ├── notebooks/      ⏳ Pendiente (CRUD models)
│   ├── documents/      ⏳ Pendiente (CRUD models)
│   ├── chat/           ⏳ Pendiente (CRUD models)
│   ├── interactions/   ⏳ Pendiente (tracking models)
│   └── core/           ⏳ Preparación para tasks celery
├── api/
│   └── v1/
│       ├── auth/       ✅ (register, login)
│       ├── notebooks/  ⏳ (list, create, update, delete)
│       ├── documents/  ⏳ (upload, list, delete)
│       └── chat/       ⏳ (send_message, history)
└── services/
    ├── llm_service.py  ⏳ (Groq integration)
    ├── pdf_service.py  ⏳ (PDF extraction + OCR)
    └── storage_service.py ⏳ (File handling)

DB Schema:
├── users_user ✅
├── users_userprofile ✅
├── notebooks_notebook ⏳
├── notebooks_document ⏳
├── chat_chatmessage ⏳
├── interactions_interaction ⏳
└── subscriptions_usersubscription ⏳
```

### ❌ NO EXISTE AÚN

| Componente | Razón | Impacto |
|-----------|-------|--------|
| Frontend | No planificado aún | Bloquea UI testing |
| PDF upload | Necesita S3/local storage | Bloquea file handling |
| Groq integration | Necesita models primero | Bloquea chat IA |
| Stripe/Pagos | Fase 5 | Bloquea suscripciones |
| Celery | Async tasks (OCR, IA) | Bloquea background jobs |

---

## 3. ARQUITECTURA DE DATOS PARA MVP

### 3.1 Documentos sin PDF (MVP Fase 4A-4B)

```python
# Fase 4A: Solo texto
class Document(models.Model):
    id = UUIDField(primary_key=True)
    user = ForeignKey(User)
    notebook = ForeignKey(Notebook)
    
    # Content
    title = CharField(max_length=255)
    content = TextField()  # Texto extraído de archivo
    original_filename = CharField(max_length=255)
    
    # Metadata para upload
    file_type = CharField(choices=['txt', 'pdf', 'image'], default='txt')
    file_path = CharField(max_length=1000, blank=True)  # Local: /uploads/...
    file_size = IntegerField(default=0)
    
    # OCR tracking
    ocr_status = CharField(
        choices=['pending', 'processing', 'completed', 'failed'],
        default='completed'
    )  # En MVP: siempre 'completed' (sync)
    
    created_at = DateTimeField(auto_now_add=True)

# Fase 4B: Upgraded con versioning
# (No necesitas cambiar Document, solo agregar DocumentVersion)
```

### 3.2 Chat + Context

```python
class ChatMessage(models.Model):
    id = UUIDField(primary_key=True)
    user = ForeignKey(User)
    notebook = ForeignKey(Notebook)
    document_context = ForeignKey(Document, null=True, blank=True)
    
    role = CharField(choices=['user', 'assistant'])
    content = TextField()
    
    # IA metadata
    tokens_used = IntegerField(default=0)
    model = CharField(default='groq-mixtral')
    
    created_at = DateTimeField(auto_now_add=True)

class Interaction(models.Model):
    """Registrar eventos para análisis + memory"""
    id = UUIDField(primary_key=True)
    user = ForeignKey(User)
    
    action_type = CharField(choices=['upload', 'chat', 'search', 'export'])
    content = TextField()
    metadata = JSONField()
    
    created_at = DateTimeField(auto_now_add=True)
```

### 3.3 Suscripción (para Fase 5 pagos)

```python
class UserSubscription(models.Model):
    user = OneToOneField(User)
    
    tier = CharField(
        choices=['FREE', 'PREMIUM', 'PRO'],
        default='FREE'
    )
    
    limits = JSONField(default={
        'documents': 5,
        'chats_per_month': 50,
        'storage_gb': 1
    })
    
    # Lifecycle
    started_at = DateTimeField(auto_now_add=True)
    expires_at = DateTimeField(null=True)
    is_active = BooleanField(default=True)
```

---

## 4. ENDPOINTS MVP (Backend)

### 4.1 Notebooks

```
GET    /api/v1/notebooks/              # Listar mis notebooks
POST   /api/v1/notebooks/              # Crear notebook
PATCH  /api/v1/notebooks/{id}/         # Editar nombre, color
DELETE /api/v1/notebooks/{id}/         # Borrar notebook + docs

Response example:
{
    "id": "notebook-uuid",
    "name": "Enero 2026",
    "document_count": 3,
    "color": "blue",
    "is_default": false,
    "created_at": "2026-03-24"
}
```

### 4.2 Documents

```
POST   /api/v1/documents/upload/       # Subir archivo
GET    /api/v1/documents/              # Listar mis docs (filtrar por notebook)
GET    /api/v1/documents/{id}/         # Ver detalle + content
DELETE /api/v1/documents/{id}/         # Borrar documento

Request upload:
{
    "notebook": "notebook-uuid",
    "file": <multipart file>,           # File upload
    "title": "Optional title"
}

Response:
{
    "id": "doc-uuid",
    "notebook": "...",
    "title": "Resume.pdf",
    "content": "Lorem ipsum...",
    "file_type": "pdf",
    "ocr_status": "completed",
    "file_size": 234567,
    "created_at": "2026-03-24T10:30"
}
```

### 4.3 Chat

```
POST   /api/v1/chat/send_message/      # Enviar mensaje a IA
GET    /api/v1/chat/history/           # Obtener historial de notebook
DELETE /api/v1/chat/clear_history/     # Limpiar historial

Request send:
{
    "notebook": "notebook-uuid",
    "document_context": "doc-uuid",     # Opcional pero recomendado
    "content": "¿Cuál es el resumen?"
}

Response:
{
    "id": "msg-uuid",
    "role": "assistant",
    "content": "Basado en el documento...",
    "document_context": "doc-uuid",
    "tokens_used": 245,
    "created_at": "2026-03-24T10:31"
}
```

---

## 5. FUNCIONES FUNDAMENTALES PARA MVP

### 5.1 Backend (Python/Django)

**File Processing Service** (`apps/core/services/file_service.py`)
```python
class FileProcessor:
    def process_file(file_obj, file_type='txt') -> str:
        """
        1. Detectar tipo (PDF, imagen, texto, Word)
        2. Extraer texto (pytesseract para OCR, pdfplumber para PDF)
        3. Convertir a Markdown
        4. Guardar en storage local
        return: (extracted_text, markdown_content)
        """
        pass

class PDFExtractor:
    def extract_from_pdf(pdf_path) -> str:
        """Usar pdfplumber para extraer texto"""
        pass

class OCRProcessor:
    def process_image(image_path) -> str:
        """Usar pytesseract (wrapper de Tesseract OCR)"""
        pass
```

**LLM Service** (`apps/core/services/llm_service.py`)
```python
class GroqClient:
    def chat_with_context(question: str, context: str) -> str:
        """
        1. Pasar documento como system prompt
        2. Enviar pregunta de usuario
        3. Obtener respuesta de Groq
        4. Registrar tokens usados
        return: (response_text, tokens_used)
        """
        pass

    def check_subscription_limits(user, tokens_used) -> bool:
        """Validar que usuario no excedió su límite"""
        pass
```

**ViewSets** (`apps/notebooks/views.py`, etc)
```python
class NotebookViewSet(ModelViewSet):
    # CRUD automático para Notebook
    # Filtros: user, is_default
    # Permisos: IsOwner

class DocumentViewSet(ModelViewSet):
    # CRUD para Document
    # Upload: multipart/form-data
    # Auto-process del archivo (call FileProcessor)
    # Permisos: IsOwner

class ChatViewSet(ModelViewSet):
    # send_message: POST (crea mensaje, llama a Groq, retorna response)
    # history: GET (lista mensajes de notebook ordenados)
    # clear_history: DELETE
    # Permisos: IsOwner
```

### 5.2 Frontend (React/Vue)

**Páginas principales**
```javascript
// App estructura
<App>
  ├─ Login/Register        # Auth page
  ├─ NotebooksList         # /notebooks - sidebar + grid
  ├─ NotebookDetail        # /notebooks/{id} - editors + chat
  │  ├─ DocumentUpload     # Drop zone para archivos
  │  ├─ DocumentView       # Preview del documento
  │  └─ ChatInterface      # Messages + input
  └─ SettingsPage          # Perfil + suscripción
```

**Componentes clave**
```javascript
<FileUpload>           // Drop + upload, progress bar
<DocumentPreview>      // PDF/texto preview + highlight
<ChatBubbles>          // Message list (user/assistant)
<ChatInput>            // Text input + send button
<NotebookSidebar>      // Listar notebooks, crear
<SubscriptionBanner>   // "Upgrade para más documentos"
```

**API Client** (`frontend/api/client.ts`)
```typescript
// Auto-generated from DRF API (drf-yasg o drf-spectacular)
const api = {
  notebooks: {
    list: () => GET /api/v1/notebooks/
    create: (data) => POST /api/v1/notebooks/
    update: (id, data) => PATCH /api/v1/notebooks/{id}/
  }
  documents: {
    upload: (file, notebook) => POST /api/v1/documents/upload/
    list: (notebook?) => GET /api/v1/documents/
  }
  chat: {
    send: (message) => POST /api/v1/chat/send_message/
    history: (notebook) => GET /api/v1/chat/history/
  }
}
```

---

## 6. STACK TECNOLÓGICO FINAL (MVP)

### Backend
```
Django 5.0.6 + DRF 3.15.2       ✅ Auth + API
PostgreSQL 15 + pgvector         ✅ BD + embeddings (futuro)
Python 3.13 + psycopg3          ✅ Moderno
SimpleJWT                       ✅ Auth tokens
Groq SDK                        ⏳ (instalar cuando fase 4C)
pdfplumber                      ⏳ PDF extraction
pytesseract                     ⏳ OCR (necesita Tesseract binario)
Celery + Redis                  ⏳ Async tasks (Fase 4B)
Django-storages + boto3         ⏳ S3 (Fase 5)
Stripe SDK                      ⏳ Pagos (Fase 5)
```

### Frontend
```
React 18+ o Vue 3               ⏳ Framework
Vite                            ⏳ Build tool
Tailwind CSS                    ⏳ UI styling
React Query / TanStack Query    ⏳ API state
React Markdown / marked         ⏳ Markdown render
```

### Infrastructure
```
Docker + Docker Compose         ✅
PostgreSQL                      ✅
Local file storage (MVP)       ⏳
S3 (Fase 5)                    ⏳
Stripe (Fase 5)                ⏳
Groq API (Fase 4C)             ⏳
```

---

## 7. PLAN EJECUCIÓN FASE 4 PROPUESTO

### Fase 4A: Modelos Backend (3-4 días)

**Hito 1**: Crear modelos + migraciones
```bash
# 1. Crear modelos
# apps/notebooks/models.py → Notebook
# apps/documents/models.py → Document
# apps/chat/models.py → ChatMessage, Interaction
# apps/subscriptions/models.py → UserSubscription

# 2. Crear migraciones
python manage.py makemigrations
python manage.py migrate

# 3. Register en admin
# apps/*/admin.py

# 4. Tests básicos
python manage.py test apps.notebooks.tests
```

**Hito 2**: Crear ViewSets + URLs
```bash
# 1. Serializers (apps/*/serializers.py)
# 2. Views (apps/*/views.py)
# 3. URLs (apps/*/urls.py)
# 4. Register en config/urls.py

# 5. Tests
python manage.py test apps.notebooks.views
```

**Hito 3**: Permisos + Tests
```bash
# 1. Crear permissions.py (IsOwner, IsSubscriptionActive)
# 2. Aplicar en ViewSets
# 3. Tests de permisos
```

**Result:** 12 endpoints funcionales, 100+ tests, docs vía drf-spectacular.

---

### Fase 4B: Procesamiento archivos (3-4 días)

**Hito 1**: Instalar dependencias + File Storage
```bash
pip install pdfplumber pytesseract pillow celery redis

# Crear storage local
# backend/storage/uploads/
```

**Hito 2**: File Service
```python
# apps/core/services/file_service.py
- Detectar MIME type
- Extraer texto (PDF → pdfplumber, IMG → pytesseract)
- Convertir a Markdown
- Guardar en BD

# apps/documents/views.py
- ParseMultiPartForm → File
- Call FileService → content
- Create Document con content
```

**Hito 3**: Async Processing (Celery)
```python
# tasks.py
- process_file_async.delay(doc_id)
- Update Document.ocr_status mientras procesa
```

**Result:** Upload endpoint funcional, archivos procesados, OCR working.

---

### Fase 4C: Chat + IA (2-3 días)

**Hito 1**: Groq Integration
```python
# apps/core/services/llm_service.py
from groq import Groq
client = Groq(api_key=settings.GROQ_API_KEY)

def send_message(question, context_doc):
    response = client.chat.completions.create(
        model="mixtral-8x7b-32768",
        system_prompt=f"Document content: {context_doc.content}",
        messages=[{"role": "user", "content": question}]
    )
    return response.content
```

**Hito 2**: Chat ViewSet
```python
# apps/chat/views.py
class ChatViewSet(ViewSet):
    def send_message(request):
        1. Get document_context (if provided)
        2. Call llm_service.send_message(question, document)
        3. Create ChatMessage (user + assistant)
        4. Return response
```

**Hito 3**: Token Tracking + Limits
```python
# Check subscription limits
if user.subscription.used_tokens + tokens_used > limits:
    raise PermissionDenied("Token limit exceeded")
```

**Result:** Chat fully functional, IA responses, token tracking.

---

### Fase 5: Frontend (+Pagos) (4-5 días)

**Hito 1**: Frontend scaffold
```
npm create vite@latest frontend -- --template react
npm install tailwindcss react-query axios react-markdown
```

**Hito 2**: UI Components
- NotebooksList
- DocumentUpload + Preview
- ChatInterface
- AuthPages

**Hito 3**: API Integration
```typescript
// frontend/src/api/client.ts
export const api = new OpenAPI({baseUrl: 'http://localhost:8000/api/v1'})
```

**Hito 4**: Stripe Integration
```typescript
// Pagos endpoint
POST /api/v1/subscriptions/create_checkout/
```

---

## 8. DECISIONES CRÍTICAS PARA MVP

| Decisión | Opción MVP | Razón |
|----------|-----------|-------|
| **Almacenamiento** | Local (`/uploads/`) | S3 después, MVP simplifica |
| **OCR Async** | Sync en MVP (dentro del request) | Celery después, MVP es sync |
| **Modelos IA** | Groq free tier (5000 llamadas/mes) | OpenAI después |
| **Versioning docs** | No (solo current) | Fase 5+ |
| **Embeddings** | No (búsqueda full-text) | Fase 6 RAG |
| **Testing** | APITestCase, fixtures | Pytest después |
| **Documentación** | drf-spectacular auto-gen | OpenAPI después |

---

## 9. ROADMAP VISUAL

```mermaid
Timeline
    title MVP Development Timeline (4 weeks)

    section Backend
    Fase 4A (Models) : f4a, 2026-03-24, 4d
    Fase 4B (Files) : f4b, after f4a, 4d
    Fase 4C (Chat+IA) : f4c, after f4b, 3d
    Integration & Testing : f4d, after f4c, 3d

    section Frontend
    Setup + Components : f5a, 2026-04-07, 2d
    API Integration : f5b, after f5a, 2d
    Auth + Chat UI : f5c, after f5b, 2d

    section Deployment
    Docker + Compose : f6a, 2026-04-14, 1d
    Stripe Integration : f6b, after f6a, 1d
    MVP Launch : f6c, after f6b, 1d

    section QA
    End-to-End Testing : qa1, 2026-04-17, 2d
    Load Testing : qa2, after qa1, 1d
    Security Review : qa3, after qa2, 1d
```

---

## 10. ENTREGABLES POR FASE

### Fase 4A (3-4 días)
- [x] 4 modelos creados (Notebook, Document, ChatMessage, Interaction)
- [x] 12 endpoints REST funcionales
- [x] Permisos + ownership validation
- [x] 100+ tests (models + API)
- [x] Admin panel actualizado
- [x] Documentación API (drf-spectacular)

### Fase 4B (3-4 días)
- [x] File upload endpoint
- [x] PDF extraction (pdfplumber)
- [x] OCR (pytesseract)
- [x] Markdown conversion
- [x] Storage local setup
- [x] Intgración tests

### Fase 4C (2-3 días)
- [x] Groq SDK integration
- [x] Chat endpoint con IA context
- [x] Token tracking
- [x] Subscription limits

### Fase 5 (4-5 días)
- [x] Frontend React scaffold
- [x] UI components (upload, chat, notebooks)
- [x] API client integration
- [x] Auth pages
- [x] Stripe checkout

### MVP Ready (24 de abril)
- [x] Backend 100% funcional
- [x] Frontend 100% funcional
- [x] Tests all green
- [x] Deployed en Docker
- [x] Listo para usuarios

---

## 11. PREGUNTAS FINALES ANTES DE EJECUTAR

1. **¿Confirmamos Fase 4A primero (modelos)**, luego phased los otros?
2. **¿Frontend con React o Vue?** (Recomiendo React por ecosistema)
3. **¿Tesseract instalado en máquina?** (Para OCR local)
4. **¿Groq API key** lista?
5. **¿Stripe key** (Fase 5)?
6. **¿Comenzamos Fase 4A hoy o revisamos algo más?**

---

## Referencias rápidas

- Arquitectura: `docs/05_arquitectura_general.md`
- Modelos: `docs/08_modelo_datos.md`
- API: `docs/07_contratos_api.md`
- Decisiones: `docs/10_fase4_arquitectura_detallada.md`
- Proceso: `docs/09_pasos_decisiones.md`
