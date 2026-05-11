# PDF_IA_Rework - AI Document Analysis Platform

Full-stack application for intelligent document analysis with AI-powered chat. Built with Django 5.0, React 19, and Groq API.

![Status](https://img.shields.io/badge/status-MVP%20Fase%205-brightgreen)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![Node](https://img.shields.io/badge/node-18+-blue)
![React](https://img.shields.io/badge/react-19-61dafb)
![Django](https://img.shields.io/badge/django-5.0-092e20)

---

## ✨ Features

- 📓 **Notebook System** - Create and organize multiple dynamic notebooks
- 💬 **AI Chat** - Ask questions powered by Groq API (llama-3.1-8b-instant)
- 📄 **Document Upload** - Upload and manage documents in notebooks
- 🔐 **JWT Authentication** - Secure token-based auth with refresh
- 💾 **Auto-Save** - Automatic markdown saving with debouncing
- 📱 **Responsive Design** - Modern UI with CatIA color palette

---

## 📋 Quick Links

- [GIT_STRATEGY.md](GIT_STRATEGY.md) - What to upload/ignore & why
- [PRE_PUSH_CHECKLIST.md](PRE_PUSH_CHECKLIST.md) - Verify before pushing to GitHub
- [SCRIPTS_GUIDE.md](SCRIPTS_GUIDE.md) - Setup & start scripts documentation
- [docs/IMPROVEMENT_PLAN.md](docs/IMPROVEMENT_PLAN.md) - Technical improvements roadmap
- [docs/](docs/) - Detailed documentation
- **[📊 Architecture Diagrams](docs/ARCHITECTURE_DIAGRAMS.md)** - Class, Flow & System Diagrams

---

## 🚀 Quick Start

### Prerequisites

- **Python** 3.11+
- **Node.js** 18+
- **PostgreSQL** 15+ (running on port 5434, or use SQLite for quick testing)
- **Groq API Key** - Get free key at https://console.groq.com/keys
- **Docker & Docker Compose** (optional, for containerized setup)

### ⚡ Automated Setup (Recommended)

Use the setup scripts to automate everything:

```bash
# Initial setup (run once)
./setup.sh
# → Choose: Docker Compose or Local Development
# → Answer questions about API keys
# → Done! ✨

# Start development (run every time)
./start.sh
# → Frontend: http://localhost:5173
# → Backend: http://localhost:8001/api/v1
```

**See [SCRIPTS_GUIDE.md](SCRIPTS_GUIDE.md) for detailed script documentation.**

---

### Manual Setup

If you prefer to set up manually:

#### Docker Compose Manual

```bash
# 1. Clone and setup
git clone <repo-url>
cd PDF_IA_Rework

# 2. Create environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

# 3. Edit with your Groq API key
nano backend/.env  # Add: GROQ_API_KEY=gsk_...

# 4. Start services
docker-compose up -d

# 5. Access
# Frontend: http://localhost:5173
# Backend: http://localhost:8001/api/v1
```

#### Local Development Manual

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Edit with Groq key
python manage.py migrate
python manage.py runserver 0.0.0.0:8001

# Frontend (in another terminal)
cd frontend
npm install --legacy-peer-deps
cp .env.example .env.local
npm run dev
# Open http://localhost:5173
```

---

## 🏗️ Architecture

### Backend (Django 5.0)
- **Database**: PostgreSQL 15 with pgvector support
- **API**: REST with CORS enabled for frontend
- **Authentication**: JWT tokens (SimpleJWT) with Bearer headers
- **AI Integration**: Groq API connector for chat completions
- **Models**: User, Notebook, Document, ChatMessage, Interaction
- **Tests**: 57 passing tests covering core functionality

### Frontend (React 19 + Vite)
- **UI Framework**: TailwindCSS with CatIA custom palette
  - Primary: #7C3AED (purple)
  - Accent: #EC4899 (pink)
  - Gold: #F59E0B
  - Dark: #0F172A
- **State Management**: Zustand with triple persistence layer:
  1. `authStore` - User token, profile, JWT refresh logic
  2. `chatStore` - Messages **isolated per notebook** (prevents cross-contamination)
  3. `notebookStore` - Markdown content with auto-save debouncing
- **API Client**: Axios with JWT Bearer interceptor + 401 auto-logout
- **Features**:
  - Auto-save markdown (2-second debounce)
  - Per-notebook chat isolation
  - Hybrid markdown formatting (Bold, Italic, Code)
  - Protected routes with auto-redirect

---

## 🔐 Important: Environment Variables

**NEVER commit actual `.env` files** - they contain secrets!

**Backend** requires:
- `GROQ_API_KEY` - Mandatory for AI features
- `SECRET_KEY` - Django secret
- `DATABASE_URL` - PostgreSQL connection
- `CORS_ALLOWED_ORIGINS` - Must match frontend URL

**Frontend** configuration:
- `VITE_API_BASE_URL` - Backend API endpoint

See `.env.example` files for all options.

---

## 📦 Technology Stack

| Layer | Technology | Status |
|-------|-----------|--------|
| **Backend** | Django 5.0, DRF 3.14, PostgreSQL 15 | ✅ Production |
| **Frontend** | React 19, Vite 5, TypeScript, TailwindCSS | ✅ Production |
| **AI Engine** | Groq API (llama-3.1-8b-instant) | ✅ Integrated |
| **Auth** | SimpleJWT, Bearer tokens | ✅ Implemented |
| **State** | Zustand + localStorage persistence | ✅ Per-notebook isolation |
| **API Client** | Axios + auto-refresh interceptor | ✅ JWT handling |
| **Deploy** | Docker, Docker Compose | ✅ Ready |

---

## � API Structure

### Authentication
```
POST   /api/v1/auth/login/           - Authenticate & get JWT tokens
POST   /api/v1/auth/register/        - Create new user account
```

### Notebooks
```
GET    /api/v1/notebooks/            - List user's notebooks
POST   /api/v1/notebooks/            - Create new notebook
GET    /api/v1/notebooks/:id/        - Retrieve notebook details
```

### Chat
```
POST   /api/v1/chat/ask_ai/          - Send message, get AI response
GET    /api/v1/chat/history/         - Get conversation history
```

### Documents
```
POST   /api/v1/documents/            - Upload document file
GET    /api/v1/documents/            - List documents in notebook
DELETE /api/v1/documents/:id/        - Delete document
```

---

## 🪝 Frontend Hooks

Custom React hooks for state management:
- `useAuth()` - Login, register, logout, token refresh
- `useNotebooks()` - CRUD operations on notebooks
- `useChat()` - Send/retrieve messages per notebook (auto-isolated)
- `useDocuments()` - Upload/delete documents with file preview

---

## 🎯 Before First Push to GitHub

1. **Read**: [GIT_STRATEGY.md](GIT_STRATEGY.md) - Explains what's ignored
2. **Run**: [PRE_PUSH_CHECKLIST.md](PRE_PUSH_CHECKLIST.md) - Verify no secrets
3. **Command**:
   ```bash
   git add .
   git commit -m "Initial commit: MVP backend + frontend"
   git push origin main
   ```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Backend won't start | Run `python manage.py migrate` |
| API 404 errors | Check `CORS_ALLOWED_ORIGINS` in backend `.env` |
| Node modules too large | Use `.npmrc`: `legacy-peer-deps=true` |
| Groq API not working | Verify API key validity at console.groq.com |

---

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature/name`
2. Commit: `git commit -m 'Description'`
3. Push: `git push origin feature/name`
4. Open PR

See [GIT_STRATEGY.md](GIT_STRATEGY.md) for detailed guidelines.

---

## 📝 Project Structure

```
PDF_IA_Rework/
├── backend/              # Django API
│   ├── apps/            # Business logic
│   ├── config/          # Settings
│   └── requirements.txt
├── frontend/            # React app
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
├── docker-compose.yml
├── .gitignore           # See GIT_STRATEGY.md
├── README.md            # This file
└── docs/                # Detailed docs
```

## 🎯 Current Status & Roadmap

### ✅ Completed (Fase 5)
- Full backend API with 57 passing tests
- React 19 frontend with 32+ components
- JWT authentication with token refresh
- Notebook CRUD with dynamic creation
- Document upload & management
- Per-notebook chat with AI responses
- Auto-save markdown with debouncing
- Zustand state with localStorage persistence
- **Critical fix**: Chat isolation per notebook (no cross-contamination)

### � Technical Improvements (Pre-Phase 6)

**Identified Issues** from code review - See [IMPROVEMENT_PLAN.md](docs/IMPROVEMENT_PLAN.md) for details:

1. ⚠️ **Variable Global Mutable** - `_groq_service` needs thread-safety fix (`@lru_cache`)
2. ⚠️ **Hardcoded Constants** - `GROQ_MODEL` and `MAX_TOKENS` should be in settings
3. ⚠️ **Document Truncation** - 500 char limit is arbitrary, needs configuration
4. ⚠️ **Duplicate Imports** - Clean up `core/models.py`

**Impact**: 🔴 Crítica para producción  
**Timeline**: Before Fase 6 starts  
**Effort**: ~13-18 hours

### �����🔜 Upcoming (Fase 6)
- [ ] Storage quotas (FREE vs PREMIUM plans)
- [ ] Document preview / search inside documents
- [ ] Settings page (API keys, preferences)
- [ ] User profile customization
- [ ] Email notifications

### 🚀 Future (Fase 7)
- [ ] Payment integration (Stripe)
- [ ] Advanced RAG with vector embeddings
- [ ] Real-time collaboration
- [ ] Production deployment
- [ ] Monitoring & analytics

---

## 🚀 Deployment Ready

```bash
# Run pre-push verification
cat PRE_PUSH_CHECKLIST.md

# Start with Docker Compose (production-like)
docker-compose up -d

# Or run locally
cd backend && python manage.py runserver
cd frontend && npm run dev
```

**Ports:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8001/api/v1
- PostgreSQL: localhost:5434

---

## 📄 License

MIT

---

## 📞 Support

Check [GIT_STRATEGY.md](GIT_STRATEGY.md) and [PRE_PUSH_CHECKLIST.md](PRE_PUSH_CHECKLIST.md) before asking questions.
  ├── metadata (JSON flexible)
  ├── context_snapshot (estado del notebook)
  └── related_interactions (relaciones entre interacciones)

Document
  ├── file_path, file_size, pages
  ├── content (texto extraído)
  ├── summary
  └── notebook (FK)

ChatMessage
  ├── role (user/assistant)
  ├── content
  ├── tokens_used
  └── notebook, document (FKs)
```

---

### 3. **Prioridades de Implementación** ([docs/ROADMAP.md](docs/ROADMAP.md))

| Fase | Días | Descripción | Estado |
|------|------|-------------|--------|
| **1** | 1-3 | Configuración inicial + Docker | ⏳ Pendiente |
| **2** | 4-7 | Gestión de usuarios (auth, roles) | ⏳ Pendiente |
| **3** | 8-10 | Sistema de notebooks | ⏳ Pendiente |
| **4** | 11-13 | Tracking de interacciones | ⏳ Pendiente |
| **5** | 14-17 | Gestión de documentos | ⏳ Pendiente |
| **6** | 18-21 | Chat con IA (Groq) | ⏳ Pendiente |
| **7** | 22-28 | Frontend (basado en mockup) | ⏳ Esperando mockup |
| **8** | 29-31 | OCR (opcional) | ⏳ Futuro |
| **9** | 32-35 | Pagos (Stripe) | ⏳ Futuro |
| **10** | 36-40 | Deploy & Production | ⏳ Futuro |

**Total estimado:** 6-8 semanas de desarrollo

---

## 🎯 Objetivos Generales (del documento adjunto)

### Según tus requerimientos:

1. ✅ **Carga y procesamiento de archivos**
   - PDF, imágenes, Word, etc.
   - OCR para documentos escaneados
   - Extracción de texto
   - Formato Markdown

2. ✅ **Generación de chat con IA**
   - Chat contextual por notebook
   - Historial persistente
   - Respuestas usando solo info del documento
   - Streaming de respuestas (opcional)

3. ✅ **Registro y autenticación de usuarios**
   - Registro por email
   - Login con JWT
   - Roles: Free, Premium, Admin
   - Cada usuario accede solo a sus archivos y conversaciones

4. ✅ **Historial y almacenamiento**
   - Guardar historial de conversaciones
   - Asociar cada conversación con archivo correspondiente
   - **CLAVE:** Sistema de Interacciones para tracking completo

5. ✅ **Pasarela de pagos**
   - Stripe integration
   - Planes: Free (€0), Premium (€9.99), Enterprise (€29.99)
   - Limitar acceso según plan
   - Control de estado de suscripción

---

## 🆚 Django + DRF vs FastAPI (Decisión Final)

### ✅ **GANADOR: Django + DRF**

| Criterio | Django + DRF | FastAPI |
|----------|-------------|---------|
| Admin Panel | ✅ Built-in | ❌ No existe |
| Auth Robusta | ✅ Excelente | ⚠️ Manual |
| ORM | ✅ Django ORM | ✅ SQLAlchemy |
| Ecosistema | ✅ Maduro | ⏣ Creciendo |
| Performance | ⚠️ Bueno | ✅ Excelente |
| Seguridad | ✅ Battle-tested | ⚠️ Manual |
| Mantenibilidad | ✅ Alta | ⚠️ Media |
| Curva aprendizaje | ⚠️ Pronunciada | ✅ Fácil |

**Veredicto:** 
Para un proyecto con:
- ✅ Gestión compleja de usuarios
- ✅ Pasarela de pagos
- ✅ Admin panel necesario
- ✅ Largo plazo

**Django es la mejor opción.**

---

## 🔑 Características Únicas del Sistema de Interacciones

### Por qué es revolucionario:

```python
# Ejemplo de uso del sistema de interacciones:

# 1. Usuario sube un PDF de Cálculo II
log_interaction(
    user=user,
    interaction_type='UPLOAD',
    notebook=calculo_notebook,
    document=document,
    metadata={'filename': 'derivadas.pdf', 'pages': 25}
)

# 2. Usuario genera resumen
log_interaction(
    user=user,
    interaction_type='SUMMARY',
    notebook=calculo_notebook,
    document=document,
    ai_response=summary,
    tokens_used=250,
    metadata={'model': 'llama-3.1', 'length': 'medium'}
)

# 3. Usuario pregunta en chat
log_interaction(
    user=user,
    interaction_type='CHAT',
    notebook=calculo_notebook,
    document=document,
    content="¿Cómo se calcula la derivada de x^2?",
    ai_response="La derivada de x^2 es 2x...",
    tokens_used=150,
    context_snapshot={
        'topic': 'derivatives',
        'previous_questions': ['what is a derivative?', 'chain rule example']
    }
)

# 4. Una semana después, usuario vuelve
# El chatbot puede decir:
# "Bienvenido de vuelta. La semana pasada estuviste estudiando 
#  derivadas en Cálculo II. ¿Quieres continuar o empezar algo nuevo?"
```

### Ventajas:
1. **Memoria a largo plazo:** El bot "recuerda" todo
2. **Contexto acumulativo:** Aprende cómo estudias
3. **Referencias futuras:** "Como vimos la semana pasada..."
4. **Analytics:** Patrones de estudio, horarios, temas favoritos
5. **Recomendaciones:** Basadas en tu historial

---

## 📦 Estructura del Proyecto

```
PDF_IA_Rework/
│
├── README.md
├── STACK_TECNOLOGICO.md    # Tecnologías y decisiones
├── ROADMAP.md              # Plan de implementación detallado
├── PDF_IA_REWORK_PLAN.md   # Plan original (referencia)
├── docker-compose.yml
├── .gitignore
│
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── .env.example
│   │
│   ├── config/                # Settings Django
│   │   ├── __init__.py
│   │   ├── settings/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── development.py
│   │   │   └── production.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   │
│   └── apps/
│       ├── users/          # Autenticación, roles, permisos
│       ├── notebooks/      # Notebooks dinámicos
│       ├── interactions/   # Tracking completo (CLAVE)
│       ├── documents/      # PDFs, upload, processing
│       ├── chat/           # Chat con IA, historial
│       └── core/           # Utilidades compartidas
│
└── frontend/
    ├── package.json
    ├── vite.config.js
    ├── Dockerfile
    │
    └── src/
        ├── components/
        │   ├── auth/       # Login, Register
        │   ├── dashboard/  # Layout principal
        │   ├── documents/  # Upload, lista, viewer
        │   ├── chat/       # Chat window
        │   └── notebooks/  # Gestión de notebooks
        ├── pages/
        ├── services/       # API calls
        ├── context/        # React Context
        └── hooks/          # Custom hooks
```

---

## 🚀 Siguiente Paso Inmediato

### Opción A: **Comenzar Implementación** 🛠️

Si dices **"adelante"**, empiezo con:

1. **Crear estructura de backend:**
   ```bash
   mkdir -p PDF_IA_Rework/backend
   cd PDF_IA_Rework/backend
   python3 -m venv venv
   source venv/bin/activate
   django-admin startproject config .
   ```

2. **Crear docker-compose.yml:**
   - PostgreSQL 15 (puerto 5434)
   - Redis (puerto 6380)
   - Backend (puerto 8001)
   - Frontend (puerto 5174)

3. **Configurar settings.py:**
   - Separar en base.py, development.py, production.py
   - Configurar DRF
   - Configurar JWT
   - Configurar CORS

4. **Crear apps iniciales:**
   ```bash
   python manage.py startapp users apps/users
   python manage.py startapp notebooks apps/notebooks
   python manage.py startapp interactions apps/interactions
   # etc.
   ```

**¿Empiezo con esto?** → Di "adelante FASE 1"

---

### Opción B: **Esperar Mockup del Frontend** 🎨

Si prefieres primero diseñar la UI:
- Creas el mockup en Figma/Excalidraw/etc.
- Me lo compartes
- Adapto el plan de FASE 7 (Frontend) según tu diseño
- Luego empezamos con backend

**¿Haces mockup primero?** → Di "primero mockup"

---

### Opción C: **Aclarar Dudas** ❓

Si tienes preguntas sobre:
- Stack tecnológico
- Arquitectura de datos
- Roadmap
- Cualquier otra cosa

**¿Tienes dudas?** → Pregúntame

---

## 📊 Comparación Rápida: PDF_IA vs PDF_IA_Rework

| Feature | PDF_IA (FastAPI) | PDF_IA_Rework (Django) |
|---------|------------------|------------------------|
| Backend | FastAPI | Django + DRF |
| Auth | JWT manual | djangorestframework-simplejwt |
| Admin Panel | ❌ | ✅ Django Admin |
| Users | Básico | Roles (Free/Premium/Admin) |
| Notebooks | 4 estáticos | Dinámicos (ilimitados) |
| Interactions | ❌ | ✅ Tracking completo |
| Payments | ❌ | ✅ Stripe |
| OCR | ❌ | ✅ Tesseract + Google |
| Limits | ❌ | ✅ Por plan |
| Multi-file | Solo PDF | PDF + Word + Imágenes |

---

## 💡 Recomendaciones

### Ahora:
1. **Empezar con backend** (FASE 1-4) para tener base sólida
2. **Hacer mockup en paralelo** (puedes diseñar mientras codifico)
3. **No tener prisa** (vas paso a paso, bien hecho)

### Más adelante:
1. **Tests desde el principio** (no dejar para el final)
2. **Commits frecuentes** (git cada feature)
3. **Documentar decisiones** (README actualizado)

---

## 📝 Status Actual

- ✅ Stack tecnológico definido
- ✅ Arquitectura diseñada
- ✅ Roadmap completo
- ✅ Bases de datos separadas (no conflicto con PDF_IA)
- ✅ Puertos separados (correr en paralelo)
- ⏳ Esperando decisión de inicio
- ⏳ Esperando mockup del frontend

---

## ❓ ¿Qué falta definir?

Nada crítico. Todo está listo para empezar.

**Opcional:**
- Nombre de dominio (si vas a deployar)
- Logo/branding
- Textos de bienvenida
- Email de soporte

Pero eso puede hacerse después.

---

## 🎯 Tu Decisión

**¿Qué hacemos?**

1. **"adelante FASE 1"** → Empiezo con configuración inicial
2. **"primero mockup"** → Espero tu diseño de UI
3. **"tengo dudas sobre X"** → Respondo tus preguntas
4. **"cambiemos Y por Z"** → Ajustamos el plan

---

**Estoy listo cuando tú lo estés** 🚀

No hay prisa. Vamos paso a paso, pero firmes.
