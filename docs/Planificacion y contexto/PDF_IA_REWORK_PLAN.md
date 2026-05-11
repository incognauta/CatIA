# 🔄 Plan de Migración: PDF_IA → PDF_IA_Rework (Django + DRF)

> **Estado:** [ARCHIVED] - Documento histórico.  
> **Razón:** Contenido consolidado en `09_pasos_decisiones.md` y `11_mvp_strategy.md`.  
> **Seguimiento oficial:** `docs/03_tracking_plan.md`.  
> **NOTA:** Referencia histórica solamente. Para nuevas decisiones, ver archivos activos.

## 📋 Resumen Ejecutivo

**Objetivo:** Crear PDF_IA_Rework usando Django + Django REST Framework, manteniendo todas las funcionalidades de PDF_IA (FastAPI) y mejorando la gestión de usuarios y características avanzadas.

**Duración Estimada:** 2-3 semanas  
**Complejidad:** Media-Alta  
**Estado:** Planificación

---

## 🎯 Funcionalidades a Replicar (desde PDF_IA FastAPI)

### ✅ Funcionalidades Core que deben mantenerse:
1. **📄 Gestión de Documentos (PDFs)**
   - Subida de archivos PDF
   - Almacenamiento en PostgreSQL
   - Metadata (nombre, tipo notebook, páginas, tamaño)
   - CRUD completo (Create, Read, Update, Delete)
   - Filtrado por notebook
   - Búsqueda de documentos

2. **🤖 Integración con Groq AI**
   - Generación de resúmenes
   - Chat contextual con historial
   - Preguntas de estudio
   - Tracking de tokens usados

3. **💬 Sistema de Chat Persistente**
   - Mensajes guardados por notebook
   - Historial de conversaciones
   - Contexto conversacional (AI recuerda chat anterior)
   - Export a Markdown
   - Clear chat history

4. **📊 Notebooks por Materia**
   - Matemáticas
   - Leyes
   - Ciencias
   - General
   - (Base para expansión dinámica futura)

5. **💾 Persistencia PostgreSQL**
   - Base de datos relacional
   - Modelos: Document, ChatMessage
   - Migraciones

### 🚀 Mejoras Nuevas (Django + DRF):
1. **👥 Sistema de Autenticación Robusto**
   - Registro de usuarios (email + password)
   - Login/Logout
   - JWT tokens (con refresh tokens)
   - Permisos y roles (User, Premium, Admin)
   - Verificación de email (opcional)
   - Reset de password

2. **🔐 Gestión de Usuarios Avanzada**
   - Perfiles de usuario
   - Límites por tipo de usuario (Free: 5 PDFs, Premium: ilimitado)
   - Tracking de uso (PDFs subidos, tokens consumidos)
   - Dashboard de usuario

3. **⚙️ Panel de Administración Django**
   - Django Admin personalizado
   - Gestión de usuarios
   - Ver documentos de todos los usuarios
   - Estadísticas de uso
   - Moderación de contenido

4. **📈 Features Adicionales**
   - Compartir documentos entre usuarios
   - Notebooks personalizados (crear/editar/borrar)
   - Historial de resúmenes generados
   - API paginada
   - Rate limiting
   - Logs de actividad

---

## 🏗️ Estructura del Proyecto PDF_IA_Rework

```
PDF_IA_Rework/
│
├── backend/                          # Django Project
│   ├── manage.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── .env.example
│   │
│   ├── config/                       # Configuración principal (settings.py)
│   │   ├── __init__.py
│   │   ├── settings/
│   │   │   ├── __init__.py
│   │   │   ├── base.py              # Settings comunes
│   │   │   ├── development.py       # Dev settings
│   │   │   └── production.py        # Prod settings
│   │   ├── urls.py                  # URLs principales
│   │   ├── wsgi.py
│   │   └── asgi.py
│   │
│   ├── apps/                         # Apps de Django
│   │   │
│   │   ├── users/                   # 👤 App de usuarios
│   │   │   ├── __init__.py
│   │   │   ├── models.py            # User, UserProfile
│   │   │   ├── serializers.py       # UserSerializer, RegisterSerializer
│   │   │   ├── views.py             # RegisterView, LoginView, ProfileView
│   │   │   ├── urls.py
│   │   │   ├── permissions.py       # Custom permissions
│   │   │   ├── admin.py
│   │   │   └── tests.py
│   │   │
│   │   ├── documents/               # 📄 App de documentos (replica FastAPI)
│   │   │   ├── __init__.py
│   │   │   ├── models.py            # Document (migrado desde FastAPI)
│   │   │   ├── serializers.py       # DocumentSerializer
│   │   │   ├── views.py             # DocumentViewSet (DRF)
│   │   │   ├── urls.py
│   │   │   ├── services.py          # PDFProcessorService
│   │   │   ├── admin.py
│   │   │   └── tests.py
│   │   │
│   │   ├── chat/                    # 💬 App de chat (replica FastAPI)
│   │   │   ├── __init__.py
│   │   │   ├── models.py            # ChatMessage (migrado)
│   │   │   ├── serializers.py       # ChatMessageSerializer
│   │   │   ├── views.py             # ChatViewSet
│   │   │   ├── urls.py
│   │   │   ├── services.py          # LLMService (Groq)
│   │   │   ├── admin.py
│   │   │   └── tests.py
│   │   │
│   │   ├── notebooks/               # 📚 App de notebooks (nueva funcionalidad)
│   │   │   ├── __init__.py
│   │   │   ├── models.py            # Notebook (dinámico, creado por users)
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── admin.py
│   │   │   └── tests.py
│   │   │
│   │   └── core/                    # 🔧 Utilidades compartidas
│   │       ├── __init__.py
│   │       ├── utils.py
│   │       ├── exceptions.py
│   │       └── middleware.py
│   │
│   ├── static/                      # Archivos estáticos
│   ├── media/                       # Archivos subidos (PDFs)
│   └── templates/                   # Templates (si los usas)
│
├── frontend/                         # React (puede reutilizarse)
│   ├── src/
│   ├── package.json
│   └── ...
│
├── docker-compose.yml               # PostgreSQL + Backend + Frontend
├── .gitignore
└── README.md
```

---

## 📦 Stack Tecnológico

### Backend (Cambios de FastAPI → Django):
| Componente | FastAPI (Original) | Django Rework (Nuevo) |
|------------|-------------------|----------------------|
| **Framework** | FastAPI 0.119.0 | Django 5.0 + DRF 3.14 |
| **ORM** | SQLAlchemy 2.0 | Django ORM |
| **Validación** | Pydantic | DRF Serializers |
| **Auth** | JWT manual | djangorestframework-simplejwt |
| **Admin** | No tiene | Django Admin + django-admin-interface |
| **Migraciones** | Alembic | Django Migrations |
| **Testing** | pytest | pytest-django |
| **ASGI Server** | Uvicorn | Daphne / Gunicorn |
| **CORS** | fastapi-cors | django-cors-headers |

### Mantener igual:
- **Database:** PostgreSQL 15 (pgvector/pgvector:pg15)
- **AI/LLM:** Groq AI (llama-3.1-8b-instant)
- **Frontend:** React 18 + Vite + Material-UI
- **Containerization:** Docker + docker-compose

### Nuevas dependencias Django:
```txt
Django==5.0
djangorestframework==3.14.0
djangorestframework-simplejwt==5.3.1
django-cors-headers==4.3.1
django-filter==24.1
psycopg2-binary==2.9.9
python-decouple==3.8
Pillow==10.2.0
drf-yasg==1.21.7              # Swagger docs
django-extensions==3.2.3
pytest-django==4.8.0
groq==0.4.1                   # Mantener Groq AI
PyPDF2==3.0.1                 # Mantener PDF processing
```

---

## 🗺️ Plan de Implementación (Paso a Paso)

### **FASE 1: Configuración Inicial** (Día 1-2)

#### Paso 1.1: Crear estructura del proyecto
```bash
# Crear directorio principal
mkdir PDF_IA_Rework
cd PDF_IA_Rework

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Crear proyecto Django
pip install django djangorestframework
django-admin startproject config backend
cd backend
```

#### Paso 1.2: Configurar settings.py
- Crear `settings/base.py`, `settings/development.py`, `settings/production.py`
- Configurar PostgreSQL (mismo que PDF_IA original)
- Configurar Django REST Framework
- Configurar CORS
- Configurar STATIC_ROOT y MEDIA_ROOT
- Variables de entorno con python-decouple

#### Paso 1.3: Instalar dependencias
```bash
pip install -r requirements.txt
```

#### Paso 1.4: Crear apps iniciales
```bash
python manage.py startapp users apps/users
python manage.py startapp documents apps/documents
python manage.py startapp chat apps/chat
python manage.py startapp notebooks apps/notebooks
python manage.py startapp core apps/core
```

#### Paso 1.5: Configurar Docker
- Crear `Dockerfile` para backend
- Crear `docker-compose.yml` (PostgreSQL + backend + frontend)
- Probar que levante correctamente

**✅ Hito 1:** Proyecto Django configurado y corriendo

---

### **FASE 2: Modelos y Base de Datos** (Día 3-4)

#### Paso 2.1: Crear modelo User personalizado (apps/users/models.py)
```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=20,
        choices=[('FREE', 'Free'), ('PREMIUM', 'Premium'), ('ADMIN', 'Admin')],
        default='FREE'
    )
    max_documents = models.IntegerField(default=5)  # Free: 5, Premium: 999
    total_tokens_used = models.BigIntegerField(default=0)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

#### Paso 2.2: Migrar modelo Document (apps/documents/models.py)
```python
# Basado en PDF_IA/backend/app/models/document.py
from django.db import models
from django.conf import settings
import uuid

class NotebookType(models.TextChoices):
    MATEMATICAS = 'matematicas', 'Matemáticas'
    LEYES = 'leyes', 'Leyes'
    CIENCIAS = 'ciencias', 'Ciencias'
    GENERAL = 'general', 'General'

class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='documents')
    filename = models.CharField(max_length=255)
    original_filename = models.CharField(max_length=255)
    notebook = models.CharField(max_length=50, choices=NotebookType.choices)
    file_path = models.CharField(max_length=500)  # Ruta en filesystem
    file_size = models.BigIntegerField()  # Bytes
    pages = models.IntegerField(null=True)
    content = models.TextField()  # Texto extraído del PDF
    summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'notebook']),
            models.Index(fields=['created_at']),
        ]
```

#### Paso 2.3: Migrar modelo ChatMessage (apps/chat/models.py)
```python
# Basado en PDF_IA/backend/app/models/chat_message.py
from django.db import models
from django.conf import settings
import uuid

class ChatMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_messages')
    document = models.ForeignKey('documents.Document', on_delete=models.SET_NULL, null=True, blank=True)
    notebook = models.CharField(max_length=50)
    role = models.CharField(max_length=20, choices=[('user', 'User'), ('assistant', 'Assistant')])
    content = models.TextField()
    tokens_used = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['user', 'notebook']),
        ]
```

#### Paso 2.4: Crear modelo Notebook personalizado (apps/notebooks/models.py)
```python
# NUEVA FUNCIONALIDAD: Notebooks dinámicos creados por usuarios
from django.db import models
from django.conf import settings
import uuid

class Notebook(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notebooks')
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#1976d2')  # Hex color
    icon = models.CharField(max_length=50, default='📚')  # Emoji
    is_default = models.BooleanField(default=False)  # Los 4 originales son default
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = [['user', 'slug']]
        ordering = ['name']
```

#### Paso 2.5: Ejecutar migraciones
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

**✅ Hito 2:** Base de datos configurada con todos los modelos

---

### **FASE 3: API REST con Django REST Framework** (Día 5-8)

#### Paso 3.1: Configurar JWT Authentication
```python
# config/settings/base.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
}
```

#### Paso 3.2: Crear Serializers

##### apps/users/serializers.py
```python
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio', 'created_at', 'updated_at']

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'role', 'max_documents', 'total_tokens_used', 'profile']
        read_only_fields = ['id', 'role', 'max_documents', 'total_tokens_used']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'password2']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords don't match"})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        UserProfile.objects.create(user=user)
        return user
```

##### apps/documents/serializers.py
```python
from rest_framework import serializers
from .models import Document

class DocumentSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True, required=False)
    
    class Meta:
        model = Document
        fields = '__all__'
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'content', 'file_size', 'pages']

class DocumentUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    notebook = serializers.ChoiceField(choices=Document.NotebookType.choices)
```

##### apps/chat/serializers.py
```python
from rest_framework import serializers
from .models import ChatMessage

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = '__all__'
        read_only_fields = ['id', 'user', 'created_at', 'tokens_used']

class ChatRequestSerializer(serializers.Serializer):
    notebook = serializers.CharField()
    question = serializers.CharField()
    document_id = serializers.UUIDField(required=False)
```

#### Paso 3.3: Crear ViewSets (DRF)

##### apps/users/views.py
```python
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, UserSerializer
from .models import User

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
```

##### apps/documents/views.py
```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q
from .models import Document
from .serializers import DocumentSerializer, DocumentUploadSerializer
from .services import PDFProcessorService

class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        queryset = Document.objects.filter(user=self.request.user)
        notebook = self.request.query_params.get('notebook')
        search = self.request.query_params.get('search')
        
        if notebook:
            queryset = queryset.filter(notebook=notebook)
        if search:
            queryset = queryset.filter(
                Q(filename__icontains=search) | Q(original_filename__icontains=search)
            )
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def upload(self, request):
        serializer = DocumentUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Check user document limit
        user = request.user
        if user.documents.count() >= user.max_documents:
            return Response(
                {'error': f'Límite de {user.max_documents} documentos alcanzado. Actualiza a Premium.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Process PDF
        pdf_service = PDFProcessorService()
        result = pdf_service.process_upload(
            file=serializer.validated_data['file'],
            notebook=serializer.validated_data['notebook'],
            user=request.user
        )
        
        return Response(DocumentSerializer(result).data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def generate_summary(self, request, pk=None):
        document = self.get_object()
        # Lógica de resumen con Groq (similar a FastAPI)
        from apps.chat.services import LLMService
        llm_service = LLMService()
        summary = llm_service.generate_summary(document.content)
        
        document.summary = summary
        document.save()
        
        return Response({'summary': summary})
```

##### apps/chat/views.py
```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ChatMessage
from .serializers import ChatMessageSerializer, ChatRequestSerializer
from .services import LLMService
from apps.documents.models import Document

class ChatViewSet(viewsets.ModelViewSet):
    serializer_class = ChatMessageSerializer
    
    def get_queryset(self):
        return ChatMessage.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def send_message(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        notebook = serializer.validated_data['notebook']
        question = serializer.validated_data['question']
        document_id = serializer.validated_data.get('document_id')
        
        # Save user message
        user_msg = ChatMessage.objects.create(
            user=request.user,
            notebook=notebook,
            role='user',
            content=question,
            document_id=document_id
        )
        
        # Get chat history
        history = ChatMessage.objects.filter(
            user=request.user,
            notebook=notebook
        ).order_by('created_at')[:20]
        
        # Get document context if provided
        document = None
        if document_id:
            document = Document.objects.filter(id=document_id, user=request.user).first()
        
        # Generate AI response
        llm_service = LLMService()
        answer, tokens = llm_service.answer_question(
            text=document.content if document else "",
            question=question,
            chat_history=list(history.values('role', 'content'))
        )
        
        # Save assistant message
        assistant_msg = ChatMessage.objects.create(
            user=request.user,
            notebook=notebook,
            role='assistant',
            content=answer,
            tokens_used=tokens,
            document_id=document_id
        )
        
        # Update user token usage
        request.user.total_tokens_used += tokens
        request.user.save()
        
        return Response({
            'user_message': ChatMessageSerializer(user_msg).data,
            'assistant_message': ChatMessageSerializer(assistant_msg).data,
        })
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        notebook = request.query_params.get('notebook')
        if not notebook:
            return Response({'error': 'notebook parameter required'}, status=400)
        
        messages = ChatMessage.objects.filter(
            user=request.user,
            notebook=notebook
        ).order_by('created_at')
        
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['delete'])
    def clear_history(self, request):
        notebook = request.query_params.get('notebook')
        if not notebook:
            return Response({'error': 'notebook parameter required'}, status=400)
        
        deleted_count, _ = ChatMessage.objects.filter(
            user=request.user,
            notebook=notebook
        ).delete()
        
        return Response({'deleted': deleted_count})
```

#### Paso 3.4: Configurar URLs

##### config/urls.py
```python
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="PDF_IA Rework API",
        default_version='v1',
        description="API REST para gestión de PDFs con IA",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/', include('apps.users.urls')),
    path('api/v1/', include('apps.documents.urls')),
    path('api/v1/', include('apps.chat.urls')),
    path('api/v1/', include('apps.notebooks.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
```

##### apps/documents/urls.py
```python
from rest_framework.routers import DefaultRouter
from .views import DocumentViewSet

router = DefaultRouter()
router.register(r'documents', DocumentViewSet, basename='document')

urlpatterns = router.urls
```

##### apps/chat/urls.py
```python
from rest_framework.routers import DefaultRouter
from .views import ChatViewSet

router = DefaultRouter()
router.register(r'chat', ChatViewSet, basename='chat')

urlpatterns = router.urls
```

**✅ Hito 3:** API REST completa con endpoints funcionales

---

### **FASE 4: Servicios (Groq AI, PDF Processing)** (Día 9-10)

#### Paso 4.1: Migrar LLMService (apps/chat/services.py)
```python
# Basado en PDF_IA/backend/app/services/llm_service.py
import os
from groq import Groq
from decouple import config

class LLMService:
    def __init__(self):
        self.client = Groq(api_key=config('GROQ_API_KEY'))
        self.model = "llama-3.1-8b-instant"
    
    def generate_summary(self, text: str) -> str:
        # Migrar lógica de FastAPI
        pass
    
    def answer_question(self, text: str, question: str, chat_history: list) -> tuple[str, int]:
        # Migrar lógica con historial
        pass
    
    def generate_questions(self, text: str) -> list:
        # Migrar generación de preguntas
        pass
```

#### Paso 4.2: Migrar PDFProcessorService (apps/documents/services.py)
```python
# Basado en PDF_IA/backend/app/services/pdf_processor.py
import os
import uuid
from PyPDF2 import PdfReader
from django.conf import settings
from django.core.files.storage import default_storage
from .models import Document

class PDFProcessorService:
    def process_upload(self, file, notebook, user):
        # Extract text from PDF
        reader = PdfReader(file)
        pages = len(reader.pages)
        content = ""
        for page in reader.pages:
            content += page.extract_text()
        
        # Save file
        filename = f"{uuid.uuid4()}_{file.name}"
        file_path = default_storage.save(f'documents/{filename}', file)
        
        # Create document
        document = Document.objects.create(
            user=user,
            filename=filename,
            original_filename=file.name,
            notebook=notebook,
            file_path=file_path,
            file_size=file.size,
            pages=pages,
            content=content
        )
        
        return document
```

**✅ Hito 4:** Servicios de AI y PDF funcionando

---

### **FASE 5: Django Admin Personalizado** (Día 11-12)

#### Paso 5.1: Personalizar Django Admin

##### apps/users/admin.py
```python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'role', 'max_documents', 'total_tokens_used', 'is_active']
    list_filter = ['role', 'is_active', 'date_joined']
    search_fields = ['email', 'username']
    ordering = ['-date_joined']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Permisos PDF_IA', {'fields': ('role', 'max_documents', 'total_tokens_used')}),
    )
```

##### apps/documents/admin.py
```python
from django.contrib import admin
from .models import Document

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['filename', 'user', 'notebook', 'pages', 'file_size', 'created_at']
    list_filter = ['notebook', 'created_at']
    search_fields = ['filename', 'original_filename', 'user__email']
    readonly_fields = ['id', 'created_at', 'updated_at', 'content']
    
    def has_add_permission(self, request):
        return False  # No crear docs desde admin
```

#### Paso 5.2: Instalar y configurar django-admin-interface (opcional)
```bash
pip install django-admin-interface
```

**✅ Hito 5:** Panel de administración funcional

---

### **FASE 6: Testing** (Día 13-14)

#### Paso 6.1: Escribir tests para cada app

##### apps/users/tests.py
```python
from django.test import TestCase
from rest_framework.test import APIClient
from .models import User

class UserTests(TestCase):
    def setUp(self):
        self.client = APIClient()
    
    def test_register_user(self):
        response = self.client.post('/api/v1/auth/register/', {
            'email': 'test@test.com',
            'username': 'testuser',
            'password': 'TestPass123!',
            'password2': 'TestPass123!'
        })
        self.assertEqual(response.status_code, 201)
    
    def test_login_user(self):
        # Test login flow
        pass
```

##### apps/documents/tests.py
```python
# Test de upload, CRUD, límites de usuario, etc.
```

##### apps/chat/tests.py
```python
# Test de mensajes, historial, integración con Groq
```

#### Paso 6.2: Ejecutar tests
```bash
pytest
coverage run -m pytest
coverage report
```

**✅ Hito 6:** Cobertura de tests > 80%

---

### **FASE 7: Docker & Deployment** (Día 15-16)

#### Paso 7.1: Configurar Docker

##### Dockerfile (backend)
```dockerfile
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
```

##### docker-compose.yml
```yaml
version: '3.8'

services:
  db:
    image: pgvector/pgvector:pg15
    environment:
      POSTGRES_DB: pdf_ia_rework
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5434:5432"  # Diferente puerto que PDF_IA original (5433)
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - ./backend:/app
      - media_volume:/app/media
    ports:
      - "8001:8000"  # Diferente puerto que PDF_IA original (8000)
    env_file:
      - ./backend/.env
    depends_on:
      - db

  frontend:
    build: ./frontend
    volumes:
      - ./frontend:/app
      - /app/node_modules
    ports:
      - "5174:5173"  # Diferente puerto que PDF_IA original (5173)
    depends_on:
      - backend

volumes:
  postgres_data:
  media_volume:
```

#### Paso 7.2: Variables de entorno (.env)
```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://postgres:postgres@db:5432/pdf_ia_rework
GROQ_API_KEY=your-groq-api-key
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5174
```

#### Paso 7.3: Comandos de deployment
```bash
docker-compose up --build
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py collectstatic --noinput
```

**✅ Hito 7:** Aplicación corriendo en Docker

---

### **FASE 8: Frontend (Adaptación React)** (Día 17-18)

#### Paso 8.1: Actualizar API service (frontend/src/services/api.js)
```javascript
import axios from 'axios';

const API_URL = 'http://localhost:8001/api/v1';

// Configurar interceptor para JWT
axios.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authAPI = {
  register: (data) => axios.post(`${API_URL}/auth/register/`, data),
  login: (email, password) => axios.post(`${API_URL}/auth/login/`, { email, password }),
  refreshToken: (refresh) => axios.post(`${API_URL}/auth/refresh/`, { refresh }),
  getProfile: () => axios.get(`${API_URL}/users/profile/`),
};

export const documentsAPI = {
  list: (notebook) => axios.get(`${API_URL}/documents/`, { params: { notebook } }),
  upload: (file, notebook) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('notebook', notebook);
    return axios.post(`${API_URL}/documents/upload/`, formData);
  },
  delete: (id) => axios.delete(`${API_URL}/documents/${id}/`),
  generateSummary: (id) => axios.post(`${API_URL}/documents/${id}/generate_summary/`),
};

export const chatAPI = {
  sendMessage: (notebook, question, documentId) => 
    axios.post(`${API_URL}/chat/send_message/`, { notebook, question, document_id: documentId }),
  getHistory: (notebook) => axios.get(`${API_URL}/chat/history/`, { params: { notebook } }),
  clearHistory: (notebook) => axios.delete(`${API_URL}/chat/clear_history/`, { params: { notebook } }),
};
```

#### Paso 8.2: Crear componentes de autenticación
```javascript
// frontend/src/components/Login.jsx
// frontend/src/components/Register.jsx
// frontend/src/components/ProtectedRoute.jsx
```

#### Paso 8.3: Actualizar App.jsx con rutas autenticadas
```javascript
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Login from './components/Login';
import Register from './components/Register';
import Dashboard from './components/Dashboard';
import ProtectedRoute from './components/ProtectedRoute';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/" element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        } />
      </Routes>
    </BrowserRouter>
  );
}
```

**✅ Hito 8:** Frontend adaptado a Django backend

---

### **FASE 9: Features Avanzadas** (Día 19-21)

#### Paso 9.1: Implementar Rate Limiting
```bash
pip install django-ratelimit
```

#### Paso 9.2: Implementar Logs de actividad
```python
# apps/core/models.py
class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    details = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
```

#### Paso 9.3: Implementar compartir documentos
```python
# apps/documents/models.py
class DocumentShare(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    shared_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shares_sent')
    shared_with = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shares_received')
    can_edit = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
```

#### Paso 9.4: Implementar Notebooks personalizados
```python
# Ya creado en Fase 2, ahora endpoints:
# apps/notebooks/views.py - CRUD completo de notebooks
```

**✅ Hito 9:** Features avanzadas implementadas

---

### **FASE 10: Optimización & Deploy Production** (Día 22-23)

#### Paso 10.1: Optimizaciones
- Caché con Redis (django-redis)
- Compresión de respuestas (whitenoise)
- Optimización de queries (select_related, prefetch_related)
- Indexación de base de datos

#### Paso 10.2: Seguridad
- HTTPS forzado
- CSRF protection
- SQL injection protection (Django ORM)
- XSS protection
- Rate limiting

#### Paso 10.3: Monitoring
- Sentry para error tracking
- Django Debug Toolbar (solo dev)
- Logs estructurados

**✅ Hito 10:** Aplicación lista para producción

---

## 📊 Comparación: PDF_IA (FastAPI) vs PDF_IA_Rework (Django)

| Feature | PDF_IA (FastAPI) | PDF_IA_Rework (Django) |
|---------|------------------|------------------------|
| **Auth** | Manual JWT | djangorestframework-simplejwt |
| **Admin Panel** | ❌ No | ✅ Django Admin |
| **User Management** | Básico | Avanzado (roles, límites) |
| **ORM** | SQLAlchemy | Django ORM |
| **Migraciones** | Alembic | Django Migrations |
| **API Docs** | Swagger (manual) | drf-yasg (auto) |
| **Testing** | pytest | pytest-django |
| **Notebooks** | Estáticos (4) | Dinámicos (user-created) |
| **Share Docs** | ❌ No | ✅ Sí |
| **Rate Limiting** | ❌ No | ✅ Sí |
| **Activity Logs** | ❌ No | ✅ Sí |
| **Email Verification** | ❌ No | ✅ Opcional |

---

## 🚀 Comandos Rápidos

### Desarrollo
```bash
# Iniciar proyecto
docker-compose up -d

# Ver logs
docker-compose logs -f backend

# Ejecutar migraciones
docker-compose exec backend python manage.py migrate

# Crear superuser
docker-compose exec backend python manage.py createsuperuser

# Shell de Django
docker-compose exec backend python manage.py shell

# Tests
docker-compose exec backend pytest
```

### Producción
```bash
# Build para producción
docker-compose -f docker-compose.prod.yml up --build -d

# Recolectar estáticos
docker-compose exec backend python manage.py collectstatic --noinput

# Backup de BD
docker-compose exec db pg_dump -U postgres pdf_ia_rework > backup.sql
```

---

## ✅ Checklist de Implementación

### Configuración Inicial
- [ ] Crear estructura de proyecto Django
- [ ] Configurar settings (base, dev, prod)
- [ ] Crear apps (users, documents, chat, notebooks, core)
- [ ] Configurar Docker y docker-compose
- [ ] Variables de entorno (.env)

### Modelos y Base de Datos
- [ ] Crear modelo User personalizado
- [ ] Crear modelo UserProfile
- [ ] Migrar modelo Document
- [ ] Migrar modelo ChatMessage
- [ ] Crear modelo Notebook
- [ ] Ejecutar migraciones iniciales

### API REST
- [ ] Configurar Django REST Framework
- [ ] Configurar JWT authentication
- [ ] Crear serializers (users, documents, chat)
- [ ] Crear ViewSets
- [ ] Configurar URLs y routers
- [ ] Documentación con Swagger (drf-yasg)

### Servicios
- [ ] Migrar LLMService (Groq AI)
- [ ] Migrar PDFProcessorService
- [ ] Integrar servicios con ViewSets

### Admin
- [ ] Personalizar UserAdmin
- [ ] Personalizar DocumentAdmin
- [ ] Personalizar ChatMessageAdmin
- [ ] Instalar django-admin-interface (opcional)

### Testing
- [ ] Tests de users (register, login, profile)
- [ ] Tests de documents (upload, CRUD, limits)
- [ ] Tests de chat (messages, history)
- [ ] Cobertura > 80%

### Frontend
- [ ] Actualizar API service (axios + JWT)
- [ ] Crear Login component
- [ ] Crear Register component
- [ ] Crear ProtectedRoute
- [ ] Actualizar Dashboard con auth

### Features Avanzadas
- [ ] Rate limiting
- [ ] Activity logs
- [ ] Compartir documentos
- [ ] Notebooks personalizados
- [ ] Email verification (opcional)

### Deploy
- [ ] Dockerfile optimizado
- [ ] docker-compose.prod.yml
- [ ] Configurar HTTPS
- [ ] Configurar dominio
- [ ] Monitoring (Sentry)
- [ ] Backups automáticos

---

## 🎯 Próximos Pasos Inmediatos

1. **Confirmar enfoque:** ¿Procedemos con este plan?
2. **Decisión de puertos:** DB en 5434, Backend en 8001, Frontend en 5174 (para no conflictuar con PDF_IA original)
3. **¿Comenzamos con Fase 1?** Crear estructura inicial del proyecto

---

## ❓ Preguntas para Aclarar

1. **¿Quieres mantener PDF_IA (FastAPI) corriendo en paralelo durante el desarrollo de PDF_IA_Rework?**
   - Si sí → Usar puertos diferentes (ya contemplados en el plan)
   
2. **¿Prioridad en features nuevas?**
   - ¿Cuál quieres primero: Admin panel, User roles, o Notebooks dinámicos?

3. **¿Base de datos separada o compartida?**
   - Recomiendo separada (pdf_ia_rework) para evitar conflictos

4. **¿Frontend completamente nuevo o adaptar el actual?**
   - ¿Copiar frontend actual y modificar, o crear desde cero?

5. **¿Alguna tecnología específica que quieras agregar?**
   - ¿Redis para caché?
   - ¿Celery para tareas asíncronas?
   - ¿Websockets para chat en tiempo real?

---

## 📝 Notas Finales

- **Tiempo estimado total:** 2-3 semanas (trabajo full-time)
- **Complejidad:** Media-Alta
- **Ventajas de Django:** Admin panel, ORM maduro, comunidad grande, seguridad built-in
- **Desventajas:** Más código boilerplate que FastAPI, menos rápido para APIs puras

**¿Estás listo para comenzar?** 🚀

Dime si quieres que empiece con la **Fase 1** o si tienes dudas/cambios al plan.
