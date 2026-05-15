# PDF_IA_Rework — AI Document Analysis Platform

Full-stack application for intelligent document analysis with AI-powered chat. Built with **Django 5.0 + DRF**, **React 19 + TypeScript**, and **Groq API**.

![Status](https://img.shields.io/badge/status-Fase%207-blueviolet)
![Python](https://img.shields.io/badge/python-3.12+-blue)
![Node](https://img.shields.io/badge/node-18+-blue)
![React](https://img.shields.io/badge/react-19-61dafb)
![Django](https://img.shields.io/badge/django-5.0-092e20)
![Tests](https://img.shields.io/badge/tests-57%20passing-brightgreen)

---

## Features

- **Notebook System** — Dynamic notebooks with per-notebook chat isolation
- **AI Chat with RAG** — Context-aware answers using document content (Groq API)
- **Multi-format Upload** — PDF, DOCX, TXT, images with OCR (Tesseract)
- **JWT Authentication** — Secure token-based auth with refresh + roles (Free/Premium/Admin)
- **LLM Settings** — Configurable model, temperature, max tokens per user
- **DIP Architecture** — Service layer with Dependency Inversion Principle
- **Docker Ready** — Full containerized setup with Docker Compose
- **Auto-Save** — Automatic markdown saving with debouncing

---

## Architecture Diagram

```mermaid
graph TB
    subgraph Frontend["Frontend — React 19 + Vite + TypeScript"]
        P[Pages<br/>8 pages]
        C[Components<br/>8 components]
        H[Hooks<br/>useAuth, useChat, useNotebooks, etc.]
        S[Zustand Stores<br/>auth, chat, notebook, ui]
        API[API Client<br/>Axios + JWT Interceptor]
    end

    subgraph Backend["Backend — Django 5.0 + DRF"]
        direction TB
        subgraph Apps["Django Apps"]
            U[users<br/>Auth, Roles, Plans<br/>Subscriptions]
            N[notebooks<br/>CRUD, Slug, Default]
            D[documents<br/>Upload, Processing<br/>Content Extraction]
            CH[chat<br/>Messages, RAG,<br/>History Isolation]
            CORE[core<br/>LLM Service,<br/>File Processor, DIP]
            I[interactions<br/>Tracking — WIP]
        end
        subgraph Services["Service Layer — DIP"]
            LLM[GroqLLMService]
            FP[FileProcessor<br/>PDF · DOCX · TXT · OCR]
            DS[DjangoChatService<br/>RAG + History]
        end
        SETTINGS[Config<br/>base · development · production]
    end

    subgraph External["External Services"]
        GROQ[Groq API<br/>llama · mixtral · gemma]
        DB[(PostgreSQL 15<br/>pgvector)]
        TESS[Tesseract OCR]
    end

    Frontend -->|HTTP REST| Backend
    Backend --> GROQ
    Backend --> DB
    Backend --> TESS
    API -->|JWT Auth| U
    API --> N
    API --> D
    API --> CH
    API --> CORE
```

---

## Data Flow Diagram

```mermaid
sequenceDiagram
    actor User
    participant Frontend
    participant Backend
    participant DB as PostgreSQL
    participant Groq as Groq API

    Note over User,Groq: Document Upload Flow
    User->>Frontend: Upload file (PDF / DOCX / TXT / IMG)
    Frontend->>Backend: POST /api/v1/documents/upload/
    Backend->>Backend: FileProcessor (extract text + OCR if image)
    Backend->>DB: Store document metadata + content
    Backend-->>Frontend: Document created
    Frontend-->>User: Confirm upload

    Note over User,Groq: AI Chat Flow (RAG)
    User->>Frontend: Type question
    Frontend->>Backend: POST /api/v1/chat/ask_ai/
    Backend->>DB: Fetch notebook documents (RAG context)
    Backend->>Groq: Send prompt + document context
    Groq-->>Backend: AI response
    Backend->>DB: Save ChatMessage (user + assistant)
    Backend-->>Frontend: AI response
    Frontend-->>User: Display answer

    Note over User,Groq: LLM Settings Flow
    User->>Frontend: Change model / temperature
    Frontend->>Backend: PUT /api/v1/llm-settings/{id}/
    Backend->>DB: Update UserLLMSettings
    Backend-->>Frontend: Settings updated
    Frontend-->>User: Confirm
```

---

## Entity-Relationship Diagram

```mermaid
erDiagram
    User ||--o{ Notebook : owns
    User ||--o{ Document : owns
    User ||--o{ ChatMessage : sends
    User ||--|| UserProfile : has
    User ||--|| UserSubscription : subscribes
    User ||--|| UserLLMSettings : configures
    UserSubscription }|--|| Plan : based_on
    Notebook ||--o{ Document : contains
    Notebook ||--o{ ChatMessage : has

    User {
        uuid id PK
        string username
        string email UK
        string subscription_tier
        boolean email_verified
        datetime created_at
    }

    Notebook {
        uuid id PK
        string name
        string slug UK "per user"
        string description
        string color
        boolean is_default
        datetime created_at
    }

    Document {
        uuid id PK
        string title
        string original_filename
        text content
        text content_markdown
        string file_type
        int file_size
        int pages
        datetime created_at
    }

    ChatMessage {
        uuid id PK
        string role "user | assistant"
        text content
        int tokens_used
        datetime created_at
    }

    Plan {
        uuid id PK
        string name "free | pro | enterprise"
        decimal price
        int documents_limit
        int messages_per_month
        json features
    }

    UserLLMSettings {
        uuid id PK
        string model "llama | mixtral | gemma"
        float temperature
        int max_tokens
    }
```

---

## Quick Start

### Prerequisites

- **Python** 3.12+
- **Node.js** 18+
- **PostgreSQL** 15+ (port 5434, or use Docker)
- **Groq API Key** — Get a free key at https://console.groq.com/keys
- **Docker & Docker Compose** (optional, recommended)

### Automated Setup (Recommended)

```bash
# Initial setup (run once — creates .env, installs deps)
./setup.sh

# Start development (daily use)
./start.sh
# → Frontend: http://localhost:5173
# → Backend:  http://localhost:8001/api/v1
```

See [SCRIPTS_GUIDE.md](SCRIPTS_GUIDE.md) for full documentation.

### Docker Compose

```bash
cp backend/.env.example  backend/.env
cp frontend/.env.example frontend/.env.local
# Edit backend/.env  →  add GROQ_API_KEY=gsk_...

docker-compose up -d
```

### Local Development

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # edit GROQ_API_KEY
python manage.py migrate
python manage.py runserver 0.0.0.0:8001

# Frontend (another terminal)
cd frontend
npm install --legacy-peer-deps
cp .env.example .env.local
npm run dev
```

---

## Architecture

### Backend (Django 5.0 + DRF)

| Layer | Description |
|-------|-------------|
| **6 Apps** | `users`, `notebooks`, `documents`, `chat`, `core`, `interactions` |
| **Database** | PostgreSQL 15 with pgvector |
| **Auth** | JWT (SimpleJWT) — access 1h / refresh 7d with rotation |
| **Service Layer** | DIP pattern — abstract bases + concrete implementations |
| **File Processing** | PDF (PyMuPDF), DOCX (python-docx), TXT, images (Tesseract OCR) |
| **AI** | Groq API with RAG context (llama-3.1, mixtral, gemma) |
| **Tests** | 57+ passing tests (1,256 lines) across all apps |

### Frontend (React 19 + Vite + TypeScript)

| Layer | Description |
|-------|-------------|
| **UI** | TailwindCSS with CatIA palette (purple `#7C3AED`, pink `#EC4899`, gold `#F59E0B`) |
| **State** | Zustand with localStorage persistence — 4 stores (auth, chat, notebook, ui) |
| **Server State** | @tanstack/react-query for API data fetching & caching |
| **API Client** | Axios singleton with JWT Bearer interceptor + 401 auto-logout |
| **Pages** | 8 pages — Login, Register, Dashboard, Notebook, Docs, Settings, Help, ComingSoon |
| **Components** | 8 components — Sidebar, Header, ChatSidebar, ChatMessage, ChatSettings, NotebookCanvas, DocumentsModal, RootLayout |
| **Hooks** | 6 custom hooks — useAuth, useNotebooks, useNotebook, useChat, useDocuments, useLLMSettings |

---

## Technology Stack

| Layer | Technology | Status |
|-------|-----------|--------|
| **Backend** | Django 5.0, DRF 3.14, PostgreSQL 15 | ✅ Production |
| **Frontend** | React 19, Vite 5, TypeScript, TailwindCSS 3.4 | ✅ Production |
| **AI Engine** | Groq API (llama-3.1, mixtral, gemma) | ✅ Integrated |
| **Auth** | SimpleJWT, Bearer tokens, roles (Free / Premium / Admin) | ✅ Implemented |
| **State** | Zustand + @tanstack/react-query | ✅ Implemented |
| **API Client** | Axios + auto-refresh interceptor | ✅ Implemented |
| **File Processing** | PyMuPDF, python-docx, Tesseract OCR, Pillow | ✅ Implemented |
| **Deploy** | Docker, Docker Compose | ✅ Ready |
| **Architecture** | DIP Service Layer, Repository Pattern | ✅ Fase 7 |

---

## API Reference

### Health
```
GET  /health/
```

### Authentication — `/api/v1/auth/`
```
POST  /auth/register/        Register + JWT
POST  /auth/login/            Login + JWT
```

### Users — `/api/v1/users/`
```
GET   /users/me/              Profile
PUT   /users/me/              Update profile
GET   /users/                 List (admin only)
```

### Notebooks — `/api/v1/notebooks/`
```
GET    /notebooks/                           List
POST   /notebooks/                           Create
GET    /notebooks/{id}/                      Detail
PUT    /notebooks/{id}/                      Update
DELETE /notebooks/{id}/                      Delete
GET    /notebooks/{id}/documents/            Documents in notebook
GET    /notebooks/{id}/chat_history/         Chat history
```

### Documents — `/api/v1/documents/`
```
GET    /documents/                           List
POST   /documents/                           Create
GET    /documents/{id}/                      Detail
PUT    /documents/{id}/                      Update
DELETE /documents/{id}/                      Delete
POST   /documents/upload/                    Upload file (multipart)
GET    /documents/{id}/content/              Full extracted text
```

### Chat — `/api/v1/chat/`
```
GET    /chat/                                List messages
POST   /chat/                                Create message
GET    /chat/{id}/                           Message detail
PUT    /chat/{id}/                           Update message
DELETE /chat/{id}/                           Delete message
POST   /chat/ask_ai/                         Ask AI (with RAG context)
GET    /chat/history/?notebook={id}          Conversation history
DELETE /chat/clear_history/?notebook={id}    Clear history
```

### LLM Settings — `/api/v1/llm-settings/`
```
GET    /llm-settings/                        Get user settings
PUT    /llm-settings/{id}/                   Update settings
PATCH  /llm-settings/{id}/                   Partial update
GET    /llm-settings/defaults/               System defaults
POST   /llm-settings/reset/                  Reset to defaults
```

---

## Environment Variables

| File | Variable | Required | Default |
|------|----------|----------|---------|
| `backend/.env` | `GROQ_API_KEY` | Yes | — |
| | `SECRET_KEY` | Yes | Auto-generated |
| | `DATABASE_URL` | No | PostgreSQL on localhost:5434 |
| | `CORS_ALLOWED_ORIGINS` | No | `http://localhost:5173` |
| `frontend/.env.local` | `VITE_API_BASE_URL` | No | `http://localhost:8001/api/v1` |

---

## Project Structure

```
PDF_IA_Rework/
├── backend/
│   ├── config/
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── development.py
│   │   │   └── production.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── apps/
│   │   ├── users/             # Auth, roles, plans, subscriptions
│   │   ├── notebooks/         # Notebook CRUD
│   │   ├── documents/         # Upload, processing, management
│   │   ├── chat/              # Messages, RAG, AI
│   │   ├── core/              # LLM service, file processor, DIP
│   │   └── interactions/      # Tracking (WIP)
│   ├── manage.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── pages/             # 8 pages
│   │   ├── components/        # 8 components
│   │   ├── hooks/             # 6 custom hooks
│   │   ├── stores/            # 4 Zustand stores
│   │   ├── api/               # Axios client + services
│   │   └── types/             # TypeScript definitions
│   ├── package.json
│   ├── vite.config.ts
│   ├── Dockerfile
│   └── .env.example
├── docker-compose.yml
├── setup.sh
├── start.sh
├── SCRIPTS_GUIDE.md
├── .gitignore
├── README.md
└── docs/
    ├── ARCHITECTURE_DIAGRAMS.md
    ├── ESTADO_PROYECTO.md
    ├── IMPROVEMENT_PLAN.md
    ├── PHASE_7_SIMPLIFIED.md
    ├── PHASE_7_PRODUCTION_ROADMAP.md
    └── ...
```

---

## Current Status

### ✅ Completed (Fase 5 → 7)

- Full backend API with 57+ passing tests (1,256 lines)
- React 19 frontend with 8 pages, 8 components, 6 hooks, 4 stores
- JWT authentication with token refresh and role-based access
- Notebook CRUD with dynamic creation and per-notebook isolation
- Multi-format document upload (PDF, DOCX, TXT, images + OCR)
- AI Chat with RAG context via Groq API (3 model options)
- User LLM settings (model, temperature, max tokens)
- DIP architecture with service layer and abstract base classes
- Docker Compose with PostgreSQL 15

### 🔜 Upcoming

- Interactions app — full tracking system for analytics
- Async Groq API calls — non-blocking AI responses
- Rate limiting — per-user request throttling
- Production deployment — gunicorn + nginx + SSL
- Real-time collaboration
- Payment integration (Stripe)

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Backend won't start | Run `python manage.py migrate` |
| API 404 errors | Check `CORS_ALLOWED_ORIGINS` in backend `.env` |
| Node modules too large | Use `--legacy-peer-deps` flag |
| Groq API not working | Verify key at https://console.groq.com/keys |
| File upload fails | Check file size (max 10MB) and format (PDF/DOCX/TXT/IMG) |

---

## License

MIT
