# Diagramas de Arquitectura - PDF_IA_Rework

Este documento contiene los diagramas principales del proyecto: clases, flujo y arquitectura.

---

## 📊 Diagrama de Clases

```mermaid
classDiagram
    class User {
        -UUID id
        -String username
        -String email*
        -String subscription_tier
        -Boolean email_verified
        -DateTime created_at
        -DateTime updated_at
        +login()
        +register()
        +logout()
    }
    
    class UserProfile {
        -UUID id
        -String bio
        -String avatar_url
        -String preferred_language
        -DateTime subscription_expires_at
        +update_profile()
    }
    
    class Notebook {
        -UUID id
        -String name*
        -String slug*
        -String description
        -String color
        -String icon
        -Boolean is_default
        -DateTime created_at
        -DateTime updated_at
        +create()
        +update()
        +delete()
    }
    
    class Document {
        -UUID id
        -String title
        -String original_filename
        -Text content
        -Text content_markdown
        -String file_type
        -String file_path
        -BigInt file_size
        -Int pages
        -DateTime created_at
        +upload()
        +delete()
        +extract_content()
    }
    
    class ChatMessage {
        -UUID id
        -String role
        -Text content
        -Int tokens_used
        -DateTime created_at
        +send_message()
        +get_response_from_groq()
    }
    
    class Interaction {
        -UUID id
        -String interaction_type
        -Text content
        -Text ai_response
        -JSON metadata
        -DateTime created_at
        +track_interaction()
    }
    
    User "1" --> "*" Notebook : owns
    User "1" --> "1" UserProfile : has
    User "1" --> "*" Document : uploads
    User "1" --> "*" ChatMessage : sends
    User "1" --> "*" Interaction : performs
    
    Notebook "1" --> "*" Document : contains
    Notebook "1" --> "*" ChatMessage : has_context
    Notebook "1" --> "*" Interaction : tracks
    
    Document "1" --> "*" ChatMessage : referenced_in
    
    ChatMessage "0..1" --> "0..1" Document : about
```

### 📝 Explicación Diagrama de Clases

| Clase | Descripción | Cardinalidad |
|-------|-------------|--------------|
| **User** | Usuario del sistema (extiende AbstractUser) | Entidad Principal |
| **UserProfile** | Perfil extendido (1-a-1 con User) | Datos Adicionales |
| **Notebook** | Contenedor lógico para documentos | 1 user → * notebooks |
| **Document** | Documento cargado por usuario | 1 notebook → * documents |
| **ChatMessage** | Mensaje en conversación con IA | 1 user → * messages |
| **Interaction** | Tracking de interacciones del usuario | 1 user → * interactions |

**Relaciones Clave:**
- `User` es la entidad central que se relaciona con todas las demás
- `Notebook` agrupa `Document` y `ChatMessage`
- `ChatMessage` puede referenciar un `Document` (opcional)

---

## 🔄 Diagrama de Flujo - Interacción Usuario

```mermaid
flowchart TD
    A["👤 Nuevo Usuario"] --> B{¿Tiene Cuenta?}
    B -->|No| C["📝 Registro"]
    B -->|Sí| D["🔑 Login"]
    
    C --> E["✅ Email Verificado"]
    D --> E
    
    E --> F["📓 Dashboard"]
    F --> G{Acción?}
    
    G -->|Crear| H["📚 Nuevo Notebook"]
    G -->|Seleccionar| I["🎯 Abrir Notebook"]
    
    H --> I
    I --> J{¿Siguiente?}
    
    J -->|Subir Doc| K["📄 Upload Document"]
    K --> L["✅ Documento Guardado"]
    L --> M["💬 Chat Disponible"]
    
    J -->|Chat| M
    M --> N["🤖 Enviar Pregunta"]
    N --> O["🔄 API → Groq"]
    O --> P["💭 Respuesta IA"]
    P --> Q["💾 Guardar en BD"]
    Q --> M
    
    J -->|Editar| R["✏️ Markdown Editor"]
    R --> S["💾 Auto-save"]
    S --> I
    
    Q --> T["📊 Volver Dashboard"]
    T --> F
```

### 🎯 Flujo Principal

1. **Autenticación** (5 min)
   - Registro con email
   - Login con credenciales
   - Email verificado

2. **Dashboard** (2 min)
   - Listar notebooks
   - Crear nuevo notebook
   - Seleccionar notebook existente

3. **Editor Notebook** (10 min)
   - Upload de documentos
   - Chat con IA
   - Edición markdown

4. **Chat Loop** (∞)
   - Enviar pregunta
   - API procesa → Groq AI
   - Guardar respuesta en BD
   - Volver al chat

---

## 🏗️ Diagrama de Arquitectura

```mermaid
graph TB
    subgraph Frontend["🖥️ FRONTEND - React 19 + Vite"]
        A1["📱 UI Components"]
        A2["🎨 TailwindCSS"]
        A3["📍 React Router"]
        A4["🔀 Zustand Store"]
        A5["🌐 Axios Client"]
        
        A1 --> A2
        A1 --> A3
        A3 --> A4
        A4 --> A5
    end
    
    subgraph API["🔌 REST API - Django DRF"]
        B1["🔐 Auth Endpoints"]
        B2["📓 Notebook Endpoints"]
        B3["💬 Chat Endpoints"]
        B4["📄 Document Endpoints"]
        B5["🔄 Middleware JWT"]
        
        B1 --> B5
        B2 --> B5
        B3 --> B5
        B4 --> B5
    end
    
    subgraph Backend["⚙️ BACKEND - Django 5.0"]
        C1["📊 Models"]
        C2["🎬 Views/Serializers"]
        C3["🧪 Business Logic"]
        C4["🔌 External APIs"]
        
        C1 --> C2
        C2 --> C3
        C3 --> C4
    end
    
    subgraph Database["🗄️ DATABASE - PostgreSQL 15"]
        D1["👤 Users"]
        D2["📓 Notebooks"]
        D3["📄 Documents"]
        D4["💬 ChatMessages"]
        D5["📊 Interactions"]
        
        D1 -.relates_to.-> D2
        D2 -.contains.-> D3
        D1 -.sends.-> D4
        D1 -.performs.-> D5
    end
    
    subgraph External["🌐 EXTERNAL SERVICES"]
        E1["🤖 Groq API"]
        E2["📧 Email Service"]
        E3["💳 Stripe"]
        
        E1 -->|llama-3.1-8b| C4
    end
    
    Frontend -->|HTTP/REST| API
    API --> Backend
    Backend --> Database
    Backend --> External
    
    subgraph Infrastructure["🐳 INFRASTRUCTURE"]
        F1["🐳 Docker"]
        F2["🔗 Docker Compose"]
        F3["📦 nginx Reverse Proxy"]
        
        F1 --> F2
        F2 --> F3
    end
    
    Infrastructure -.deploys.-> Frontend
    Infrastructure -.deploys.-> Backend
    Infrastructure -.deploys.-> Database
```

### 🎯 Capas de Arquitectura

#### 1️⃣ **Frontend (React 19 + Vite)**
- **Components**: UI reutilizable (Login, Dashboard, Chat)
- **Styling**: TailwindCSS + CatIA palette
- **Routing**: React Router v6 con guard de autenticación
- **State Management**: Zustand con 3 stores (auth, chat, notebook)
- **HTTP Client**: Axios con interceptor JWT

#### 2️⃣ **REST API (Django DRF)**
- **Auth**: POST /api/v1/auth/login/, /register/
- **Notebooks**: CRUD endpoints
- **Chat**: POST /ask_ai/, GET /history/
- **Documents**: Upload/Delete
- **Security**: JWT middleware en todos los endpoints

#### 3️⃣ **Backend Business Logic (Django)**
- **Models**: User, Notebook, Document, ChatMessage, Interaction
- **Serializers**: Validación y transformación de datos
- **Views**: APIView y ViewSet para CRUD
- **Managers**: Lógica de negocio (filtrados, búsquedas)

#### 4️⃣ **Database (PostgreSQL 15)**
- **Users**: Autenticación y perfiles
- **Notebooks**: Contenedores de documentos
- **Documents**: Archivos y contenido
- **ChatMessages**: Conversaciones con IA
- **Interactions**: Tracking de eventos

#### 5️⃣ **External Services**
- **Groq AI**: llama-3.1-8b-instant para respuestas
- **Email**: Verificación de email
- **Stripe**: Pagos (Fase 6)

#### 6️⃣ **Infrastructure (Docker)**
- **Docker**: Contenedores para Frontend, Backend, PostgreSQL
- **Docker Compose**: Orquestación de servicios
- **nginx**: Reverse proxy y balanceo

---

## 🔌 Endpoints de API

### Auth
```
POST   /api/v1/auth/login/           - Login (usuario + password)
POST   /api/v1/auth/register/        - Registro (usuario + email + password)
POST   /api/v1/auth/refresh/         - Refresh JWT token
```

### Notebooks
```
GET    /api/v1/notebooks/            - Listar notebooks del usuario
POST   /api/v1/notebooks/            - Crear notebook
GET    /api/v1/notebooks/:id/        - Detalles del notebook
PUT    /api/v1/notebooks/:id/        - Actualizar notebook
DELETE /api/v1/notebooks/:id/        - Eliminar notebook
```

### Chat
```
POST   /api/v1/chat/ask_ai/          - Enviar pregunta (con AI)
GET    /api/v1/chat/history/         - Historial de mensajes
```

### Documents
```
POST   /api/v1/documents/            - Subir documento
GET    /api/v1/documents/            - Listar documentos
DELETE /api/v1/documents/:id/        - Eliminar documento
```

---

## 🔐 Flujo de Autenticación

```
1. Frontend: POST /auth/login/ { email, password }
   ↓
2. Backend: Valida credenciales, genera JWT tokens
   ↓
3. Response: { access, refresh, user }
   ↓
4. Frontend: Guarda tokens en localStorage (Zustand)
   ↓
5. Request siguientes: Header "Authorization: Bearer {access_token}"
   ↓
6. Si 401: Automáticamente refresh con refresh_token
   ↓
7. Si expira refresh: Redirect a login
```

---

## 📦 Dependencias Clave

### Backend
- `django==5.0`
- `djangorestframework==3.14`
- `djangorestframework-simplejwt`
- `psycopg2-binary` (PostgreSQL)
- `groq` (IA API)

### Frontend
- `react==19`
- `vite==5`
- `typescript`
- `tailwindcss`
- `zustand`
- `axios`
- `react-router-dom`

---

## 🚀 Estado del Proyecto (Fase 5)

| Feature | Status | % Completado |
|---------|--------|--------------|
| Authentication | ✅ Completo | 100% |
| Notebook CRUD | ✅ Completo | 100% |
| Document Upload | ✅ Completo | 100% |
| Chat con IA | ✅ Completo | 100% |
| Auto-save | ✅ Completo | 100% |
| Markdown Editor | ✅ Completo | 100% |
| Storage Quotas | 🔜 Próximo | 0% |
| Payments | 🔜 Fase 6 | 0% |
| Production Deploy | 🔜 Fase 7 | 0% |

---

## 📚 Referencias

- [GIT_STRATEGY.md](GIT_STRATEGY.md) - Estrategia de git
- [PRE_PUSH_CHECKLIST.md](PRE_PUSH_CHECKLIST.md) - Checklist pre-push
- [README.md](../README.md) - Documentación principal
