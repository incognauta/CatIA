# 📚 CatIA - Guía de Onboarding

> **Aplicación de Chat con Documentos usando IA**
>
> Fase 7 Completada - MVP Listo para Producción

---

## 🎯 ¿Qué es CatIA?

CatIA es una plataforma de análisis inteligente de documentos que permite a los usuarios:

1. **Cargar documentos** en múltiples formatos (PDF, DOCX, TXT, imágenes)
2. **Conversar con IA** sobre el contenido de esos documentos
3. **Obtener respuestas contextuales** usando RAG (Retrieval-Augmented Generation)
4. **Gestionar múltiples notebooks** para organizar conversaciones por tema
5. **Cambiar idioma** entre Español e Inglés (Fase 7)
6. **Configurar el comportamiento del LLM** (modelo, temperatura, tokens)

---

## 🛠️ Stack Tecnológico

### Backend
- **Framework:** Django 5.0 + Django REST Framework
- **Base de Datos:** PostgreSQL 15 con pgvector
- **LLM:** Groq API (Llama 3.1, Mixtral, Gemma)
- **Procesamiento:** OCR (Tesseract), Markdown conversion
- **Autenticación:** JWT con refresh tokens
- **Arquitectura:** DIP (Dependency Inversion Principle)

### Frontend
- **Framework:** React 19 + TypeScript
- **Build Tool:** Vite 5
- **Styling:** TailwindCSS + Lucide Icons
- **Estado:** Zustand
- **API Client:** Axios con interceptors
- **i18n:** i18next (Español/Inglés)
- **Internacionalización:** 150+ keys de traducción

### DevOps
- **Containerización:** Docker + Docker Compose
- **Deployment:** Render, Railway, AWS, DigitalOcean
- **CI/CD:** GitHub Actions (opcional)

---

## 📁 Estructura del Proyecto

### Backend

```
backend/
├── config/
│   ├── settings/
│   │   ├── base.py          # Configuración base
│   │   ├── development.py   # Dev (debug=true)
│   │   └── production.py    # Prod (debug=false, SSL, etc)
│   ├── urls.py              # Rutas principales
│   └── wsgi.py              # WSGI para gunicorn
├── apps/
│   ├── users/               # Autenticación y perfiles
│   ├── chat/                # Endpoints de chat
│   ├── documents/           # Upload y procesamiento
│   ├── notebooks/           # Gestión de notebooks
│   ├── core/                # Servicios DIP (RAG, LLM)
│   └── interactions/        # Tracking (stub para Fase 8)
├── requirements.txt         # Dependencias
├── manage.py                # CLI de Django
└── Dockerfile              # Imagen Docker
```

**Arquitectura de Servicios (Core):**

```
backend/apps/core/services/
├── base.py                          # Interfaces abstractas (DIP)
│   ├── LLMServiceBase               # Contrato para proveedores LLM
│   ├── ChatServiceBase              # Contrato para orquestación chat
│   └── RAGServiceBase               # Contrato para búsqueda RAG
├── llm_service.py                   # Implementación Groq
├── chat_service.py                  # Orquestación: RAG + LLM + persistencia
├── rag_semantic_service.py          # Búsqueda semántica de documentos
├── embedding_service.py             # Embeddings para búsqueda
└── document_service.py              # Procesamiento de archivos
```

### Frontend

```
frontend/
├── src/
│   ├── pages/                       # Componentes de páginas
│   │   ├── LoginPage.tsx
│   │   ├── RegisterPage.tsx
│   │   ├── DashboardPage.tsx        # Mi escritorio
│   │   ├── DocsPage.tsx             # Documentos por notebook
│   │   ├── NotebookPage.tsx         # Chat + editor
│   │   ├── SettingsPage.tsx         # Configuración + idioma
│   │   ├── HelpPage.tsx             # Preguntas frecuentes
│   │   └── ComingSoonPage.tsx       # Próximas features
│   ├── components/                  # Componentes reutilizables
│   │   ├── auth/                    # Login, Register
│   │   ├── chat/                    # Chat UI, Message
│   │   ├── documents/               # Upload, DocumentList
│   │   ├── layout/                  # Header, Sidebar, Footer
│   │   └── notebook/                # NotebookList, Editor
│   ├── hooks/                       # React hooks personalizados
│   │   ├── useAuth.ts               # Autenticación
│   │   ├── useChat.ts               # Chat state + mutations
│   │   ├── useDocuments.ts          # Documentos
│   │   └── useNotebooks.ts          # Notebooks
│   ├── stores/                      # Zustand state management
│   ├── api/                         # Clientes HTTP
│   │   ├── client.ts                # Axios instance configurado
│   │   ├── auth.ts                  # Endpoints auth
│   │   ├── chat.ts                  # Endpoints chat
│   │   ├── documents.ts             # Endpoints documents
│   │   └── notebooks.ts             # Endpoints notebooks
│   ├── i18n/                        # Internacionalización
│   │   ├── config.ts                # i18next setup
│   │   └── locales/
│   │       ├── es.json              # Traducción Español (150+ keys)
│   │       └── en.json              # Traducción Inglés
│   ├── types/                       # TypeScript types
│   ├── main.tsx                     # Entrada + i18n bootstrap
│   └── App.tsx                      # Router + providers
├── index.html                       # HTML base
├── package.json                     # Dependencias
├── vite.config.ts                   # Configuración Vite
├── tsconfig.json                    # TypeScript config
└── Dockerfile                       # Imagen Docker
```

---

## 🔄 Flujo de Datos

### 1. Autenticación
```
Frontend
  ↓ POST /auth/register/
Backend (RegisterView)
  ↓ Crear User + UserProfile
DB
  ↓ Retorna tokens (access + refresh)
Frontend
  ↓ Guardar en localStorage
  ↓ Configurar axios interceptor
```

### 2. Carga de Documentos
```
Frontend (DocsPage)
  ↓ FormData (file)
  ↓ POST /documents/upload/
Backend (DocumentUploadView)
  ↓ DocumentService.process_file()
    ├─ Validar (formato, tamaño)
    ├─ OCR si es imagen (Tesseract)
    ├─ Convertir a Markdown
    └─ Guardar en BD + embeddings
DB
  ↓ Document creado con content_markdown
Frontend
  ↓ Mostrar en DocumentList
```

### 3. Chat con IA (RAG)
```
Frontend (NotebookPage)
  ↓ Enviar mensaje
  ↓ POST /chat/ask_ai/
  ├─ body: { message, notebook_id, language: 'es' }
Backend (AskAIView)
  ↓ ChatService.process_query()
    ├─ RAGService.find_relevant_documents()
    │   ├─ Buscar documentos por keywords
    │   ├─ Calcular similitud semántica
    │   └─ Top 5 documentos
    ├─ Obtener últimos 10 mensajes (context)
    ├─ LLMService.generate_response()
    │   ├─ Groq API (llama-3.1-8b-instant)
    │   ├─ System prompt + language instruction
    │   ├─ Context RAG + conversation history
    │   └─ Recibir respuesta
    ├─ Guardar ChatMessage en BD
    └─ Retornar respuesta al frontend
Frontend
  ↓ Mostrar respuesta en chat
```

### 4. Cambio de Idioma (i18n)
```
Frontend (SettingsPage)
  ↓ Usuario selecciona "English"
  ├─ i18n.changeLanguage('en')
  ├─ localStorage.setItem('language', 'en')
  └─ Componentes re-renderean (useState + listener)
Frontend (NotebookPage)
  ↓ Nuevo mensaje
  ↓ useChat hook
  ├─ Obtiene i18n.language
  ├─ Envía con body: { language: 'en' }
Backend
  ├─ Recibe language: 'en'
  ├─ LLMService construye system prompt
  │   └─ "Always respond in English..."
  └─ Groq recibe instrucción en inglés
Frontend
  ↓ Respuesta en Inglés
```

---

## 🚀 Guía Rápida de Inicio

### 1. Clonar y Configurar

```bash
git clone https://github.com/incognauta/CatIA.git
cd CatIA

# Backend
cp backend/.env.example backend/.env
# Editar: GROQ_API_KEY=gsk_...

# Frontend
cp frontend/.env.example frontend/.env.local
```

### 2. Desarrollo Local

```bash
# Terminal 1 - Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8001

# Terminal 2 - Frontend
cd frontend
npm install --legacy-peer-deps
npm run dev
```

**URLs:**
- Frontend: http://localhost:5173
- Backend: http://localhost:8001/api/v1
- Admin: http://localhost:8001/admin

### 3. Docker Compose

```bash
docker compose build --no-cache
docker compose up -d

# URLs (mismas que arriba)
```

### 4. Testear la Aplicación

```bash
# 1. Registrar usuario
Email: test@example.com
Password: Test123!

# 2. Crear Notebook
Nombre: "Mi Primer Notebook"

# 3. Cargar documento
Elegir un PDF de prueba

# 4. Chat
Pregunta: "¿De qué trata este documento?"

# 5. Cambiar idioma
Settings → Language → English
Nueva pregunta (respuesta en inglés)
```

---

## 🏗️ Conceptos Arquitectónicos Clave

### Dependency Inversion Principle (DIP)

**Problema anterior:** Clases concretas hardcodeadas (GroqLLMService en todas partes)

**Solución actual:**

```python
# base.py - Interfaz abstracta
class LLMServiceBase(ABC):
    @abstractmethod
    def generate_response(...): pass

# llm_service.py - Implementación Groq
class GroqLLMService(LLMServiceBase):
    def generate_response(...): 
        # Implementación Groq específica

# Beneficios:
# ✅ Cambiar a OpenAI sin tocar otra lógica
# ✅ Testeable con mocks
# ✅ Escalable a múltiples proveedores
```

### Retrieval-Augmented Generation (RAG)

**Flujo:**

```
Usuario: "¿Cuál es la temperatura óptima?"
    ↓
RAG Service: Buscar documentos relevantes
    ├─ Keywords: temperature
    ├─ Similitud: cosine(query, doc)
    └─ Top 5 documentos
    ↓
LLM Service: Generar respuesta
    ├─ System Prompt: "Eres un asistente..."
    ├─ Context: <documentos relevantes>
    ├─ User Query: "¿Cuál es la temperatura óptima?"
    └─ Respuesta: "Según el documento X, la temperatura es..."
    ↓
ChatMessage: Guardar en BD
```

### Internacionalización (i18n)

**Backend:**
```python
language = request.data.get('language', 'es')
system_prompt += "\n\nSiempre responde en Español."  # si es 'es'
# O
system_prompt += "\n\nAlways respond in English."     # si es 'en'
```

**Frontend:**
```typescript
const { i18n, t } = useTranslation()
<select value={selectedLanguage} onChange={(e) => {
  i18n.changeLanguage(e.target.value)
  localStorage.setItem('language', e.target.value)
}}>
  <option value="es">{t('settings.spanish')}</option>
  <option value="en">{t('settings.english')}</option>
</select>
```

---

## 📊 API Endpoints Principales

### Autenticación

```
POST   /auth/register/        Registrar usuario
POST   /auth/login/           Login (retorna access + refresh)
POST   /auth/refresh/         Refrescar token
POST   /auth/logout/          Logout (opcional, frontend)
GET    /auth/me/              Obtener usuario actual
```

### Notebooks

```
GET    /notebooks/            Listar notebooks del usuario
POST   /notebooks/            Crear notebook
GET    /notebooks/{id}/       Obtener detalles
PATCH  /notebooks/{id}/       Actualizar
DELETE /notebooks/{id}/       Eliminar
```

### Documentos

```
GET    /documents/            Listar documentos (filtrar por notebook)
POST   /documents/upload/     Cargar archivo
GET    /documents/{id}/       Obtener detalles
DELETE /documents/{id}/       Eliminar
GET    /documents/{id}/content/ Obtener contenido procesado
```

### Chat

```
POST   /chat/ask_ai/          Enviar pregunta + recibir respuesta
GET    /chat/history/         Obtener historial (filtrar por notebook)
DELETE /chat/message/{id}/    Eliminar mensaje
```

### LLM Settings

```
GET    /llm-settings/         Obtener configuración del usuario
PATCH  /llm-settings/         Actualizar (modelo, temp, max_tokens)
POST   /llm-settings/reset/   Resetear a defaults
```

---

## 🔐 Seguridad

### Implementado

- ✅ JWT con refresh tokens
- ✅ CORS configurado
- ✅ Password hashing (bcrypt)
- ✅ Queryset filtering (usuario actual)
- ✅ Rate limiting (opcional en Fase 8)

### En Producción

- ✅ HTTPS/SSL obligatorio
- ✅ DEBUG=False
- ✅ SECRET_KEY fuerte
- ✅ ALLOWED_HOSTS configurado
- ✅ SECURE_SSL_REDIRECT=True
- ✅ HSTS habilitado

---

## 🧪 Testing

### Backend Tests

```bash
cd backend
python manage.py test apps.chat
python manage.py test apps.documents
python manage.py test apps.notebooks
```

**Status:** 57+ tests pasando ✅

### Frontend Tests (Próxima fase)

```bash
npm run test
npm run test:coverage
```

---

## 📈 Próximos Pasos (Fase 8+)

| Feature | Prioridad | Complejidad |
|---------|-----------|-------------|
| Streaming de respuestas | Media | Media |
| WebSocket para real-time | Alta | Alta |
| Stripe integration (pagos) | Alta | Alta |
| Rate limiting | Media | Baja |
| Async Groq calls | Media | Media |
| Cache con Redis | Media | Media |
| Colaboración en tiempo real | Baja | Muy Alta |
| Monitoreo y analytics | Media | Media |

---

## 🆘 Troubleshooting

### Backend

| Error | Solución |
|-------|----------|
| `ModuleNotFoundError: No module named 'groq'` | `pip install -r requirements.txt` |
| `GROQ_API_KEY not configured` | Revisar `backend/.env` |
| `psycopg2 error` | PostgreSQL no corriendo o credenciales incorrectas |
| `CORS error` | Revisar `CORS_ALLOWED_ORIGINS` en settings |

### Frontend

| Error | Solución |
|-------|----------|
| `i18next is not defined` | Verificar que `main.tsx` importa `./i18n/config.ts` |
| `Cannot find module 'lucide-react'` | `npm install --legacy-peer-deps` |
| `API 404` | Verificar URL en `.env.local` |
| `Language not switching` | Limpiar localStorage: DevTools → Application → Clear |

---

## 📚 Documentación Adicional

- 📊 [ARCHITECTURE_DIAGRAMS.md](ARCHITECTURE_DIAGRAMS.md) — Diagramas de arquitectura
- 🚀 [DEPLOYMENT.md](DEPLOYMENT.md) — Guía de deployment
- 📋 [ESTADO_PROYECTO.md](ESTADO_PROYECTO.md) — Estado actual del proyecto
- 🎬 [PRESENTATION_CHECKLIST.md](PRESENTATION_CHECKLIST.md) — Demo step-by-step

---

## 👥 Contribución

1. Fork el repositorio
2. Crear rama: `git checkout -b feature/nueva-feature`
3. Commit: `git commit -m "Add nueva-feature"`
4. Push: `git push origin feature/nueva-feature`
5. PR a `main`

---

## 📝 Licencia

MIT

---

**Desarrollado con ❤️ para análisis inteligente de documentos**

**Última actualización:** 21 de mayo de 2026  
**Fase:** 7 - Completada  
**Status:** MVP Listo para Producción ✅
