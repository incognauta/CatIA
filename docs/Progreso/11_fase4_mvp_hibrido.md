# Fase 4 - MVP Híbrido (Notebooks, Documentos, Chat)

**Decisión:** Opción C - Híbrida (3 semanas de desarrollo)  
**Fecha de Decisión:** 2026-03-24  
**Estado:** Por iniciar  

---

## 🎯 Objetivo Fase 4

Implementar arquitectura MVP que soporte:
- ✅ Gestión de Notebooks (contenedores lógicos)
- ✅ Upload y procesamiento de documentos (texto plano, sin PDF aún)
- ✅ Chat con IA (Groq) usando contenido de documentos
- ✅ Historial de conversaciones persistente
- ⏳ Suscripción (modelos solo, pagos en Fase 5)

---

## 📋 Requisitos a Cumplir (desde `docs/objetivo.md`)

### Nivel MVP (Fase 4)
1. **Carga de archivos:** TXT, Markdown (PDF + OCR en Fase 4B)
2. **Procesamiento:** Conversión básica a Markdown
3. **Chat IA:** Respuestas basadas SOLO en documento cargado
4. **Historial:** Persistencia completa de conversaciones
5. **Auth:** Ya implementada en Fase 3

### Pospuesto para Fase 5
- Múltiples formatos avanzados (Word, Excel, etc)
- OCR robusto (MLKit, Advanced Tesseract)
- Pasarela de pagos (Stripe/MercadoPago)
- S3 storage (por ahora: local)

---

## 🔧 Plan Detallado: Fase 4A, 4B, 4C

### **FASE 4A: Modelos + Suscripción (Semana 1)**

#### Modelos a Crear

```python
# notebooks/models.py
class Notebook(models.Model):
    id = UUIDField(primary_key=True, default=uuid4, editable=False)
    user = ForeignKey(User, on_delete=CASCADE, related_name='notebooks')
    name = CharField(max_length=255)
    slug = SlugField(max_length=255)  # Unique per user
    description = TextField(blank=True, null=True)
    color = CharField(max_length=7, default='#1976d2')  # Hex
    icon = CharField(max_length=50, default='📚')  # Emoji
    is_default = BooleanField(default=False)  # 4 default notebooks
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [['user', 'slug']]
        ordering = ['-created_at']


# documents/models.py
class Document(models.Model):
    id = UUIDField(primary_key=True, default=uuid4, editable=False)
    user = ForeignKey(User, on_delete=CASCADE, related_name='documents')
    notebook = ForeignKey(Notebook, on_delete=CASCADE, related_name='documents')
    
    # Metadata
    title = CharField(max_length=255)
    original_filename = CharField(max_length=255)
    
    # Content
    content = TextField()  # Markdown o texto
    content_markdown = TextField(blank=True, null=True)  # Markdown procesado
    
    # File info (para future PDF)
    file_type = CharField(max_length=20, default='txt', blank=True)  # txt, pdf, docx
    file_path = CharField(max_length=500, blank=True, null=True)  # Path a storage
    file_size = BigIntegerField(null=True, blank=True)  # Bytes
    pages = IntegerField(null=True, blank=True)  # Para PDFs
    
    # Status
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'notebook']),
            models.Index(fields=['created_at']),
        ]


# chat/models.py
class ChatMessage(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
    ]
    
    id = UUIDField(primary_key=True, default=uuid4, editable=False)
    user = ForeignKey(User, on_delete=CASCADE, related_name='chat_messages')
    notebook = ForeignKey(Notebook, on_delete=CASCADE, related_name='chat_messages')
    document = ForeignKey(Document, on_delete=SET_NULL, null=True, blank=True, related_name='chat_messages')
    
    role = CharField(max_length=20, choices=ROLE_CHOICES)
    content = TextField()
    
    # Tracking
    tokens_used = IntegerField(default=0)
    created_at = DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['user', 'notebook']),
            models.Index(fields=['created_at']),
        ]


# En User model (apps/users/models.py) - AGREGAR:
class Plan(models.Model):
    """Planes de suscripción disponibles"""
    PLAN_CHOICES = [
        ('free', 'Free'),
        ('pro', 'Pro'),
        ('enterprise', 'Enterprise'),
    ]
    
    id = UUIDField(primary_key=True, default=uuid4, editable=False)
    name = CharField(max_length=100, unique=True, choices=PLAN_CHOICES)
    description = TextField(blank=True)
    price = DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Límites
    documents_limit = IntegerField(default=5)  # Free: 5, Pro: 100, Enterprise: ilimitado
    messages_per_month = IntegerField(default=100)  # Mensajes con IA
    file_size_limit = BigIntegerField(default=5242880)  # 5MB
    
    # Features
    features = JSONField(default=list)  # ['ocr', 'export', 'sharing']
    
    created_at = DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['price']


class UserSubscription(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('canceled', 'Canceled'),
        ('trial', 'Trial'),
    ]
    
    id = UUIDField(primary_key=True, default=uuid4, editable=False)
    user = ForeignKey(User, on_delete=CASCADE, related_name='subscription')
    plan = ForeignKey(Plan, on_delete=SET_NULL, null=True)
    
    status = CharField(max_length=20, choices=STATUS_CHOICES, default='trial')
    started_at = DateTimeField(auto_now_add=True)
    expires_at = DateTimeField(null=True, blank=True)
    
    # Tracking usage (para Fase 5)
    documents_used = IntegerField(default=0)
    messages_used_this_month = IntegerField(default=0)
    
    updated_at = DateTimeField(auto_now=True)
    
    class Meta:
        pass
```

#### Tareas Fase 4A
- [ ] Crear modelos en `apps/notebooks/models.py`, `apps/documents/models.py`, `apps/chat/models.py`
- [ ] Crear modelo `Plan` en `apps/users/models.py`
- [ ] Crear modelo `UserSubscription` en `apps/users/models.py`
- [ ] Crear signal para auto-crear `UserSubscription` al registrar usuario (plan: free)
- [ ] Ejecutar `python manage.py makemigrations`
- [ ] Ejecutar `python manage.py migrate`
- [ ] Crear admin customizado para todos los modelos
- [ ] Crear 4 Notebooks by default (Matemáticas, Leyes, Ciencias, General)
- [ ] Escribir tests: model creation, relationships, constraints
- [ ] `python manage.py check` sin errores

#### Entregables Fase 4A
- ✅ Modelos creados y migraciones ejecutadas
- ✅ Admin funcional
- ✅ 20+ tests pasando
- ✅ Documentación actualizada

---

### **FASE 4B: Procesamiento de Archivos + OCR (Semana 2)**

#### Dependencias a Agregar
```bash
pip install pytesseract Pillow python-docx pypdf2 markdown
```

#### Servicios a Crear

```python
# documents/services.py

from pathlib import Path
import pytesseract
from PIL import Image
from PyPDF2 import PdfReader
import markdown

class FileProcessorService:
    """Procesar diferentes formatos de archivo a Markdown"""
    
    ALLOWED_TYPES = ['txt', 'pdf', 'md', 'jpg', 'png']
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    
    def process_file(self, file, notebook_id, user_id):
        """
        Procesar archivo y retornar contenido en Markdown
        """
        # Validar
        self._validate_file(file)
        
        # Extraer contenido según tipo
        file_ext = file.name.split('.')[-1].lower()
        
        if file_ext == 'txt':
            content = self._process_txt(file)
        elif file_ext == 'md':
            content = self._process_markdown(file)
        elif file_ext == 'pdf':
            content = self._process_pdf(file)
        elif file_ext in ['jpg', 'png']:
            content = self._process_image(file)
        else:
            raise ValueError(f"Tipo de archivo no soportado: {file_ext}")
        
        return {
            'content': content,
            'content_markdown': content,  # Ya está en Markdown
            'file_type': file_ext,
            'file_size': file.size,
        }
    
    def _validate_file(self, file):
        """Validar archivo"""
        if file.size > self.MAX_FILE_SIZE:
            raise ValueError(f"Archivo muy grande. Máximo: {self.MAX_FILE_SIZE} bytes")
        
        ext = file.name.split('.')[-1].lower()
        if ext not in self.ALLOWED_TYPES:
            raise ValueError(f"Tipo no permitido: {ext}")
    
    def _process_txt(self, file):
        """Procesar TXT a Markdown"""
        content = file.read().decode('utf-8')
        return f"```\n{content}\n```"
    
    def _process_markdown(self, file):
        """Procesar Markdown (retornar como está)"""
        return file.read().decode('utf-8')
    
    def _process_pdf(self, file):
        """Extraer texto de PDF"""
        reader = PdfReader(file)
        text = ""
        for page_num, page in enumerate(reader.pages, 1):
            text += f"# Página {page_num}\n\n"
            text += page.extract_text()
            text += "\n\n"
        return text
    
    def _process_image(self, file):
        """OCR de imagen (JPG/PNG)"""
        image = Image.open(file)
        text = pytesseract.image_to_string(image, lang='spa+eng')
        return f"# Contenido extraído por OCR\n\n{text}"
```

#### Storage Service

```python
# documents/storage.py

import os
from django.conf import settings

class StorageService:
    """Gestionar almacenamiento de archivos"""
    
    STORAGE_DIR = os.path.join(settings.BASE_DIR, 'storage', 'documents')
    
    @classmethod
    def save_file(cls, file, user_id, document_id):
        """Guardar archivo localmente"""
        os.makedirs(cls.STORAGE_DIR, exist_ok=True)
        
        ext = file.name.split('.')[-1]
        filename = f"{user_id}_{document_id}.{ext}"
        filepath = os.path.join(cls.STORAGE_DIR, filename)
        
        with open(filepath, 'wb') as f:
            for chunk in file.chunks():
                f.write(chunk)
        
        return filepath
    
    @classmethod
    def delete_file(cls, filepath):
        """Eliminar archivo"""
        if os.path.exists(filepath):
            os.remove(filepath)
```

#### Tareas Fase 4B
- [ ] Crear `FileProcessorService` en `apps/documents/services.py`
- [ ] Crear `StorageService` en `apps/documents/storage.py`
- [ ] Crear serializers para Document
- [ ] Crear ViewSet para Document (GET, POST, DELETE)
- [ ] Endpoint: `POST /api/v1/documents/upload/` → procesar + guardar
- [ ] Endpoint: `GET /api/v1/documents/` → listar por notebook
- [ ] Endpoint: `GET /api/v1/documents/{id}/` → ver contenido
- [ ] Endpoint: `DELETE /api/v1/documents/{id}/` → eliminar
- [ ] Escribir tests para upload, validation, processing
- [ ] Tests: múltiples formatos, archivos grandes, error handling

#### Entregables Fase 4B
- ✅ Servicios funcionales (TXT, PDF, Images con OCR)
- ✅ Endpoints de documentos CRUD
- ✅ 15+ tests pasando
- ✅ Almacenamiento funcional

---

### **FASE 4C: Chat + IA (Semana 3)**

#### Servicios IA

```python
# chat/services.py

from groq import Groq
from django.conf import settings

class LLMService:
    """Integración con Groq AI"""
    
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = "llama-3.1-8b-instant"
    
    def generate_response(self, question, document_content, chat_history=None):
        """
        Generar respuesta basada en documento
        """
        # System prompt: responder SOLO basándose en el documento
        system_prompt = f"""Eres un asistente de IA especializado en responder preguntas sobre documentos.
IMPORTANTE: Solo responde usando la información del documento proporcionado.
Si la respuesta no se encuentra en el documento, di: "Esta información no se encuentra en el documento."

Documento:
{document_content}
"""
        
        # Construir mensajes
        messages = [
            {"role": "system", "content": system_prompt},
        ]
        
        if chat_history:
            messages.extend(chat_history)
        
        messages.append({"role": "user", "content": question})
        
        # Llamar Groq
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
        )
        
        return {
            'response': response.choices[0].message.content,
            'tokens_used': response.usage.total_tokens,
        }
    
    def generate_summary(self, document_content):
        """Generar resumen del documento"""
        messages = [
            {
                "role": "user",
                "content": f"Resume este documento en máximo 3 párrafos:\n\n{document_content}"
            }
        ]
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=512,
        )
        
        return {
            'summary': response.choices[0].message.content,
            'tokens_used': response.usage.total_tokens,
        }
```

#### Tareas Fase 4C
- [ ] Crear serializers para ChatMessage (`ChatMessageSerializer`, `ChatRequestSerializer`)
- [ ] Crear ViewSet para Chat
- [ ] Endpoint: `POST /api/v1/chat/send_message/` → procesar pregunta + Groq
- [ ] Endpoint: `GET /api/v1/chat/history/` → historial por notebook
- [ ] Endpoint: `DELETE /api/v1/chat/clear_history/` → limpiar chat
- [ ] Implementar `LLMService` (Groq integration)
- [ ] Tests: send message, history retrieval, context handling
- [ ] Tests: error handling, token tracking

#### Entregables Fase 4C
- ✅ Chat CRUD funcional
- ✅ Groq AI integration
- ✅ Endpoints de chat completos
- ✅ 15+ tests pasando
- ✅ Historial persistente

---

## 📊 Resumen de Requisitos vs Fase 4

| Requisito | Fase 4A | Fase 4B | Fase 4C | Fase 5 |
|-----------|---------|---------|---------|--------|
| Modelos de Notebook | ✅ | - | - | - |
| Procesamiento TXT | - | ✅ | - | - |
| Procesamiento PDF | - | ✅ | - | - |
| OCR (Tesseract) | - | ✅ | - | - |
| Conversión Markdown | - | ✅ | - | - |
| Chat IA (Groq) | - | - | ✅ | - |
| Historial | - | - | ✅ | - |
| Pasarela de Pagos | - | - | Modelos | ✅ |
| S3 Storage | - | Local | - | ✅ |
| Formatos avanzados | - | - | - | ✅ |

---

## 🎯 Criterios de Éxito Fase 4

Al finalizar Fase 4C:
- ✅ 50+ tests pasando (incluyendo Fases 1-3)
- ✅ `python manage.py check` sin errores
- ✅ Endpoints funcionando: notebooks CRUD, documents CRUD, chat CRUD
- ✅ Chat respondiendo preguntas basado en documentos
- ✅ Historial de conversaciones persistente
- ✅ Admin panel actualizado
- ✅ Documentación:
  - API contracts actualizados
  - Modelo de datos actualizado
  - Tracking actualizado

---

## 📚 Referencias

- `docs/08_modelo_datos.md` - Relaciones entidades
- `docs/07_contratos_api.md` - Endpoints esperados
- `docs/objetivo.md` - Requisitos del proyecto
- `docs/03_tracking_plan.md` - Tracking oficial

---

## 🚀 Próximo Paso

**INICIAR FASE 4A:** Crear modelos (Notebook, Document, ChatMessage, Plan, UserSubscription)
