# 🗺️ Roadmap - ARCHIVO ARCHIVED

> **Estado:** [ARCHIVED] - Consolidado en `03_tracking_plan.md`.  
> **Razón:** Duplicación de información de fases y cronograma.  
> **Consultar:** `docs/Planificacion y contexto/03_tracking_plan.md` para tracking actual.

## 🎯 Orden de Prioridades (Definido por el Usuario)

1. **🔐 Gestión de Usuarios** (autenticación, roles, permisos)
2. **📚 Sistema de Notebooks** (crear, editar, gestionar)
3. **📊 Tracking de Interacciones** (guardar todo para referencias futuras)
4. **📄 Gestión de Documentos** (upload, procesamiento, almacenamiento)
5. **💬 Chat con IA** (integración Groq, contexto, historial)
6. **🎨 Interfaz de Usuario** (basada en mockup)
7. **🔍 OCR & Procesamiento Avanzado** (futuro)
8. **💳 Pasarela de Pagos** (suscripciones)

---

## 📅 Cronograma Detallado

### **FASE 1: Configuración Inicial & Base del Proyecto** (Días 1-3)

#### ✅ Objetivo:
Tener el proyecto Django funcionando con estructura básica.

#### 📋 Tareas:

##### **Día 1: Setup del Proyecto**
```bash
# 1. Crear directorio y estructura
mkdir PDF_IA_Rework
cd PDF_IA_Rework
mkdir backend frontend

# 2. Backend: Crear proyecto Django
cd backend
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install Django djangorestframework
django-admin startproject config .

# 3. Configurar settings
# - Crear config/settings/base.py
# - Crear config/settings/development.py
# - Crear config/settings/production.py

# 4. Crear apps
python manage.py startapp users apps/users
python manage.py startapp notebooks apps/notebooks
python manage.py startapp interactions apps/interactions
python manage.py startapp documents apps/documents
python manage.py startapp chat apps/chat
python manage.py startapp core apps/core
```

**Archivos a crear:**
- `backend/requirements.txt`
- `backend/.env.example`
- `backend/config/settings/base.py`
- `backend/config/settings/development.py`

##### **Día 2: Configurar Docker & PostgreSQL**
```yaml
# docker-compose.yml
version: '3.8'

services:
  db:
    image: pgvector/pgvector:pg15
    container_name: pdf_ia_rework_db
    environment:
      POSTGRES_DB: pdf_ia_rework_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres123
    ports:
      - "5434:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - pdf_ia_network

  redis:
    image: redis:7-alpine
    container_name: pdf_ia_rework_redis
    ports:
      - "6380:6379"
    networks:
      - pdf_ia_network

volumes:
  postgres_data:

networks:
  pdf_ia_network:
    driver: bridge
```

**Pruebas:**
```bash
docker-compose up -d
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

##### **Día 3: Configurar DRF & CORS**
```python
# config/settings/base.py

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_yasg',
    'django_filters',
    
    # Local apps
    'apps.users',
    'apps.notebooks',
    'apps.interactions',
    'apps.documents',
    'apps.chat',
    'apps.core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# CORS
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5174",  # Vite frontend
]
CORS_ALLOW_CREDENTIALS = True
```

**✅ Hito 1:** Proyecto Django corriendo con Docker

---

### **FASE 2: Gestión de Usuarios (Prioridad #1)** (Días 4-7)

#### ✅ Objetivo:
Sistema completo de autenticación con roles y permisos.

#### 📋 Tareas:

##### **Día 4: Modelo de Usuario Personalizado**

```python
# apps/users/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class User(AbstractUser):
    """Usuario extendido con campos custom"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    
    # Roles
    ROLE_CHOICES = [
        ('FREE', 'Free'),
        ('PREMIUM', 'Premium'),
        ('ADMIN', 'Admin'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='FREE')
    
    # Límites según rol
    max_documents = models.IntegerField(default=5)  # Free: 5, Premium: 999
    max_ai_calls_per_day = models.IntegerField(default=20)  # Free: 20, Premium: 200
    
    # Tracking
    total_documents = models.IntegerField(default=0)
    total_tokens_used = models.BigIntegerField(default=0)
    last_active = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return self.email
    
    def upgrade_to_premium(self):
        """Actualizar a Premium"""
        self.role = 'PREMIUM'
        self.max_documents = 999
        self.max_ai_calls_per_day = 200
        self.save()
    
    def can_upload_document(self):
        """Verificar si puede subir más documentos"""
        return self.total_documents < self.max_documents


class UserProfile(models.Model):
    """Perfil del usuario (datos adicionales)"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Personal info
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(blank=True, max_length=500)
    phone = models.CharField(max_length=20, blank=True)
    
    # Preferences
    theme = models.CharField(max_length=20, default='light', choices=[
        ('light', 'Light'),
        ('dark', 'Dark'),
    ])
    language = models.CharField(max_length=10, default='es', choices=[
        ('es', 'Español'),
        ('en', 'English'),
    ])
    notifications_enabled = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
    
    def __str__(self):
        return f"Profile: {self.user.email}"


class UsageStats(models.Model):
    """Estadísticas de uso por día"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stats')
    date = models.DateField()
    
    # Counters
    documents_uploaded = models.IntegerField(default=0)
    ai_calls = models.IntegerField(default=0)
    tokens_used = models.IntegerField(default=0)
    chat_messages = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'usage_stats'
        unique_together = ['user', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.user.email} - {self.date}"
```

**Migraciones:**
```bash
python manage.py makemigrations users
python manage.py migrate users
```

##### **Día 5: Serializers y ViewSets de Users**

```python
# apps/users/serializers.py

from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio', 'phone', 'theme', 'language', 'notifications_enabled']

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'role', 'max_documents', 'max_ai_calls_per_day',
            'total_documents', 'total_tokens_used',
            'profile', 'created_at', 'last_active'
        ]
        read_only_fields = [
            'id', 'role', 'max_documents', 'max_ai_calls_per_day',
            'total_documents', 'total_tokens_used', 'created_at'
        ]

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'password2', 'first_name', 'last_name']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        UserProfile.objects.create(user=user)
        return user
```

```python
# apps/users/views.py

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
            'message': 'Usuario registrado exitosamente'
        }, status=status.HTTP_201_CREATED)

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout exitoso"}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "Token inválido"}, status=status.HTTP_400_BAD_REQUEST)
```

##### **Día 6: URLs y JWT Config**

```python
# apps/users/urls.py

from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, ProfileView, LogoutView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
]
```

```python
# config/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('apps.users.urls')),
]
```

##### **Día 7: Admin Panel & Tests**

```python
# apps/users/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, UsageStats

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'role', 'total_documents', 'total_tokens_used', 'is_active']
    list_filter = ['role', 'is_active', 'created_at']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Información PDF_IA', {
            'fields': ('role', 'max_documents', 'max_ai_calls_per_day', 'total_documents', 'total_tokens_used')
        }),
    )
    
    actions = ['upgrade_to_premium']
    
    def upgrade_to_premium(self, request, queryset):
        for user in queryset:
            user.upgrade_to_premium()
        self.message_user(request, f"{queryset.count()} usuarios actualizados a Premium")
    upgrade_to_premium.short_description = "Actualizar a Premium"

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'theme', 'language', 'notifications_enabled']
    search_fields = ['user__email']

@admin.register(UsageStats)
class UsageStatsAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'documents_uploaded', 'ai_calls', 'tokens_used']
    list_filter = ['date']
    search_fields = ['user__email']
```

**✅ Hito 2:** Gestión de Usuarios Completa

**Pruebas a realizar:**
```bash
# Registro
curl -X POST http://localhost:8001/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@test.com", "username": "testuser", "password": "Test123!", "password2": "Test123!"}'

# Login
curl -X POST http://localhost:8001/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@test.com", "password": "Test123!"}'

# Profile
curl -X GET http://localhost:8001/api/v1/auth/profile/ \
  -H "Authorization: Bearer {access_token}"
```

---

### **FASE 3: Sistema de Notebooks (Prioridad #2)** (Días 8-10)

#### ✅ Objetivo:
Crear sistema de notebooks dinámicos que usuarios pueden crear/editar.

#### 📋 Tareas:

##### **Día 8: Modelo de Notebooks**

```python
# apps/notebooks/models.py

from django.db import models
from django.conf import settings
from django.utils.text import slugify
import uuid

class Notebook(models.Model):
    """Notebooks personalizables por usuario"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notebooks')
    
    # Básico
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, blank=True)
    description = models.TextField(blank=True, max_length=500)
    
    # Visual
    color = models.CharField(max_length=7, default='#1976d2')  # Hex color
    icon = models.CharField(max_length=50, default='📚')  # Emoji o icon name
    
    # Settings
    is_default = models.BooleanField(default=False)  # Matemáticas, Leyes, etc.
    is_public = models.BooleanField(default=False)  # Compartir con otros
    is_archived = models.BooleanField(default=False)
    
    # Stats (denormalizadas para performance)
    total_documents = models.IntegerField(default=0)
    total_interactions = models.IntegerField(default=0)
    last_activity = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notebooks'
        unique_together = [['user', 'slug']]
        ordering = ['-last_activity', 'name']
        indexes = [
            models.Index(fields=['user', 'is_archived']),
            models.Index(fields=['-last_activity']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.user.email})"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Notebook.objects.filter(user=self.user, slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


def create_default_notebooks(user):
    """Crear notebooks por defecto para nuevo usuario"""
    defaults = [
        {'name': 'Matemáticas', 'icon': '📐', 'color': '#2962FF', 'description': 'Cálculo, álgebra, estadística'},
        {'name': 'Leyes', 'icon': '⚖️', 'color': '#D50000', 'description': 'Derecho, legislación'},
        {'name': 'Ciencias', 'icon': '🧪', 'color': '#00C853', 'description': 'Física, química, biología'},
        {'name': 'General', 'icon': '📚', 'color': '#FF6F00', 'description': 'Documentos generales'},
    ]
    
    for data in defaults:
        Notebook.objects.create(
            user=user,
            is_default=True,
            **data
        )
```

##### **Día 9: Serializers, ViewSets y URLs**

```python
# apps/notebooks/serializers.py

from rest_framework import serializers
from .models import Notebook

class NotebookSerializer(serializers.ModelSerializer):
    document_count = serializers.IntegerField(source='total_documents', read_only=True)
    interaction_count = serializers.IntegerField(source='total_interactions', read_only=True)
    
    class Meta:
        model = Notebook
        fields = [
            'id', 'name', 'slug', 'description', 'color', 'icon',
            'is_default', 'is_public', 'is_archived',
            'document_count', 'interaction_count',
            'last_activity', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'is_default', 'created_at', 'updated_at']
    
    def validate_name(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("El nombre debe tener al menos 3 caracteres")
        return value
```

```python
# apps/notebooks/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Notebook
from .serializers import NotebookSerializer

class NotebookViewSet(viewsets.ModelViewSet):
    serializer_class = NotebookSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Notebook.objects.filter(user=self.request.user)
        
        # Filtros
        is_archived = self.request.query_params.get('archived')
        if is_archived == 'true':
            queryset = queryset.filter(is_archived=True)
        elif is_archived == 'false':
            queryset = queryset.filter(is_archived=False)
        
        return queryset
    
    def perform_create(self, serializer):
        # Verificar límite de notebooks para usuarios Free
        user = self.request.user
        if user.role == 'FREE':
            notebook_count = Notebook.objects.filter(user=user, is_archived=False).count()
            if notebook_count >= 5:  # Free: máximo 5 notebooks activos
                raise serializers.ValidationError(
                    "Límite de notebooks alcanzado. Actualiza a Premium para notebooks ilimitados."
                )
        
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        notebook = self.get_object()
        if notebook.is_default:
            return Response(
                {'error': 'No puedes archivar notebooks por defecto'},
                status=status.HTTP_400_BAD_REQUEST
            )
        notebook.is_archived = True
        notebook.save()
        return Response({'message': 'Notebook archivado'})
    
    @action(detail=True, methods=['post'])
    def unarchive(self, request, pk=None):
        notebook = self.get_object()
        notebook.is_archived = False
        notebook.save()
        return Response({'message': 'Notebook restaurado'})
```

```python
# apps/notebooks/urls.py

from rest_framework.routers import DefaultRouter
from .views import NotebookViewSet

router = DefaultRouter()
router.register(r'notebooks', NotebookViewSet, basename='notebook')

urlpatterns = router.urls
```

##### **Día 10: Admin & Signal para crear notebooks por defecto**

```python
# apps/notebooks/admin.py

from django.contrib import admin
from .models import Notebook

@admin.register(Notebook)
class NotebookAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'is_default', 'is_archived', 'total_documents', 'created_at']
    list_filter = ['is_default', 'is_archived', 'created_at']
    search_fields = ['name', 'user__email']
    readonly_fields = ['total_documents', 'total_interactions', 'created_at', 'updated_at']
```

```python
# apps/users/signals.py (NUEVO ARCHIVO)

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from apps.notebooks.models import create_default_notebooks

@receiver(post_save, sender=User)
def create_user_defaults(sender, instance, created, **kwargs):
    """Crear notebooks y profile por defecto para nuevo usuario"""
    if created:
        create_default_notebooks(instance)
```

```python
# apps/users/apps.py

from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
    
    def ready(self):
        import apps.users.signals  # Registrar signals
```

**✅ Hito 3:** Sistema de Notebooks Completo

---

### **FASE 4: Tracking de Interacciones (Prioridad #3)** (Días 11-13)

#### ✅ Objetivo:
Guardar TODAS las interacciones para referencias futuras del chatbot.

#### 📋 Tareas:

##### **Día 11: Modelo de Interacciones**

```python
# apps/interactions/models.py

from django.db import models
from django.conf import settings
import uuid

class Interaction(models.Model):
    """
    Registra TODA interacción del usuario con el sistema.
    
    Propósito:
    - Historial completo para el chatbot (referencias futuras)
    - Analytics de uso
    - Patrones de aprendizaje
    - Timeline de actividad
    """
    
    INTERACTION_TYPES = [
        # Documentos
        ('UPLOAD', 'Subió documento'),
        ('VIEW', 'Vio documento'),
        ('DOWNLOAD', 'Descargó documento'),
        ('DELETE', 'Eliminó documento'),
        
        # AI
        ('SUMMARY', 'Generó resumen'),
        ('CHAT', 'Preguntó en chat'),
        ('QUESTIONS', 'Generó preguntas'),
        
        # Contenido
        ('HIGHLIGHT', 'Marcó texto'),
        ('NOTE', 'Añadió nota'),
        ('EXPORT', 'Exportó contenido'),
        
        # Notebooks
        ('CREATE_NOTEBOOK', 'Creó notebook'),
        ('EDIT_NOTEBOOK', 'Editó notebook'),
        ('ARCHIVE_NOTEBOOK', 'Archivó notebook'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='interactions')
    notebook = models.ForeignKey('notebooks.Notebook', on_delete=models.SET_NULL, null=True, blank=True)
    document = models.ForeignKey('documents.Document', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Tipo de interacción
    interaction_type = models.CharField(max_length=50, choices=INTERACTION_TYPES)
    
    # Contenido
    content = models.TextField(blank=True)  # Pregunta, nota, texto marcado, etc.
    ai_response = models.TextField(blank=True)  # Respuesta de la IA (si aplica)
    
    # Metadata flexible
    metadata = models.JSONField(default=dict, blank=True)
    # Ejemplos de metadata:
    # - CHAT: {'question': '...', 'tokens_used': 150, 'model': 'llama-3.1'}
    # - HIGHLIGHT: {'page': 5, 'text': '...', 'color': '#FFFF00'}
    # - SUMMARY: {'length': 'short', 'tokens': 200}
    
    # Context preservation (CLAVE)
    context_snapshot = models.JSONField(default=dict, blank=True)
    # Ejemplo: {'notebook_state': 'studying chapter 3', 'previous_topics': ['derivatives', 'limits']}
    
    # Relaciones
    related_interactions = models.ManyToManyField('self', blank=True, symmetrical=False)
    
    # Analytics
    tokens_used = models.IntegerField(default=0)
    processing_time_ms = models.IntegerField(default=0)  # Milisegundos
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'interactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['notebook', '-created_at']),
            models.Index(fields=['interaction_type', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.interaction_type} - {self.created_at}"
```

##### **Día 12: Serializers y ViewSets**

```python
# apps/interactions/serializers.py

from rest_framework import serializers
from .models import Interaction

class InteractionSerializer(serializers.ModelSerializer):
    notebook_name = serializers.CharField(source='notebook.name', read_only=True)
    document_name = serializers.CharField(source='document.filename', read_only=True)
    
    class Meta:
        model = Interaction
        fields = [
            'id', 'interaction_type', 
            'notebook', 'notebook_name',
            'document', 'document_name',
            'content', 'ai_response',
            'metadata', 'context_snapshot',
            'tokens_used', 'processing_time_ms',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class InteractionTimelineSerializer(serializers.Serializer):
    """Serializer para timeline agrupado por fecha"""
    date = serializers.DateField()
    interactions = InteractionSerializer(many=True)
    total_interactions = serializers.IntegerField()
```

```python
# apps/interactions/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from .models import Interaction
from .serializers import InteractionSerializer, InteractionTimelineSerializer

class InteractionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet de solo lectura para consultar interacciones.
    Las interacciones se crean automáticamente desde otros endpoints.
    """
    serializer_class = InteractionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Interaction.objects.filter(user=self.request.user)
        
        # Filtros
        notebook = self.request.query_params.get('notebook')
        interaction_type = self.request.query_params.get('type')
        days = self.request.query_params.get('days')
        
        if notebook:
            queryset = queryset.filter(notebook_id=notebook)
        if interaction_type:
            queryset = queryset.filter(interaction_type=interaction_type)
        if days:
            start_date = timezone.now() - timedelta(days=int(days))
            queryset = queryset.filter(created_at__gte=start_date)
        
        return queryset.select_related('notebook', 'document')
    
    @action(detail=False, methods=['get'])
    def timeline(self, request):
        """Timeline agrupado por fecha"""
        interactions = self.get_queryset()
        
        # Agrupar por fecha
        grouped = {}
        for interaction in interactions:
            date = interaction.created_at.date()
            if date not in grouped:
                grouped[date] = []
            grouped[date].append(interaction)
        
        # Serializar
        timeline_data = [
            {
                'date': date,
                'interactions': interactions,
                'total_interactions': len(interactions)
            }
            for date, interactions in sorted(grouped.items(), reverse=True)
        ]
        
from django.db.models.functions import TruncDate

        serializer = InteractionTimelineSerializer(timeline_data, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Estadísticas de interacciones"""
        queryset = self.get_queryset()
        
        stats = {
            'total_interactions': queryset.count(),
            'by_type': list(queryset.values('interaction_type').annotate(count=Count('id'))),
            'total_tokens': sum(queryset.values_list('tokens_used', flat=True)),
            'last_7_days': queryset.filter(
                created_at__gte=timezone.now() - timedelta(days=7)
            ).count(),
        }
        
        return Response(stats)
```

##### **Día 13: Helpers para crear interacciones automáticamente**

```python
# apps/interactions/helpers.py

from .models import Interaction
from django.utils import timezone

def log_interaction(
    user,
    interaction_type,
    notebook=None,
    document=None,
    content='',
    ai_response='',
    metadata=None,
    context_snapshot=None,
    tokens_used=0,
    processing_time_ms=0
):
    """
    Helper para crear interacciones fácilmente desde otros endpoints.
    
    Uso:
    from apps.interactions.helpers import log_interaction
    
    log_interaction(
        user=request.user,
        interaction_type='CHAT',
        notebook=notebook,
        document=document,
        content=question,
        ai_response=answer,
        metadata={'model': 'llama-3.1', 'temperature': 0.7},
        tokens_used=tokens
    )
    """
    return Interaction.objects.create(
        user=user,
        notebook=notebook,
        document=document,
        interaction_type=interaction_type,
        content=content,
        ai_response=ai_response,
        metadata=metadata or {},
        context_snapshot=context_snapshot or {},
        tokens_used=tokens_used,
        processing_time_ms=processing_time_ms
    )
```

**✅ Hito 4:** Sistema de Tracking Completo

---

## 🔄 Siguientes Fases (Resumen)

### **FASE 5: Gestión de Documentos** (Días 14-17)
- Modelo Document
- Upload de PDFs
- Extracción de texto con PyPDF2
- CRUD completo
- Integración con Interactions

### **FASE 6: Chat con IA** (Días 18-21)
- Integración Groq AI
- Chat con historial
- Resúmenes
- Preguntas de estudio
- Log de interacciones automático

### **FASE 7: Frontend (basado en mockup)** (Días 22-28)
- Setup React + Vite
- Login/Register
- Dashboard
- DocumentList
- ChatWindow
- Notebooks UI

### **FASE 8: OCR (opcional)** (Días 29-31)
- Tesseract para PDFs escaneados
- Soporte para imágenes

### **FASE 9: Pagos con Stripe** (Días 32-35)
- Integración Stripe
- Webhooks
- Suscripciones

### **FASE 10: Deploy & Production** (Días 36-40)
- Docker optimizado
- Variables de entorno
- SSL/HTTPS
- Monitoring

---

## ✅ Checklist de Progreso

- [ ] **FASE 1:** Configuración Inicial
  - [ ] Proyecto Django creado
  - [ ] Docker Compose funcionando
  - [ ] PostgreSQL conectada
  - [ ] Apps creadas

- [ ] **FASE 2:** Gestión de Usuarios
  - [ ] Modelo User personalizado
  - [ ] UserProfile
  - [ ] Register/Login/Logout
  - [ ] JWT tokens
  - [ ] Admin panel

- [ ] **FASE 3:** Sistema de Notebooks
  - [ ] Modelo Notebook
  - [ ] CRUD notebooks
  - [ ] Notebooks por defecto (signal)
  - [ ] Límites por rol

- [ ] **FASE 4:** Tracking de Interacciones
  - [ ] Modelo Interaction
  - [ ] Timeline endpoint
  - [ ] Stats endpoint
  - [ ] Helper log_interaction()

- [ ] **FASE 5:** Gestión de Documentos
- [ ] **FASE 6:** Chat con IA
- [ ] **FASE 7:** Frontend
- [ ] **FASE 8:** OCR
- [ ] **FASE 9:** Pagos
- [ ] **FASE 10:** Deploy

---

## 📝 Próximo Paso Inmediato

**¿Comenzamos con FASE 1?**

Si dices "adelante", empezaré con:
1. Crear la estructura de backend
2. Configurar docker-compose.yml
3. Setup de Django con las apps

**También esperando:**
- Mockup del frontend (para FASE 7)

¿Listo? 🚀
