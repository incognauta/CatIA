# 10. Fase 4 - Arquitectura Detallada: Notebooks + Documentos + Chat

**Propósito:** Analizar relaciones complejas entre Notebooks, Documentos, y Chat. Explorar opciones de diseño para soportar PDF + OCR en el futuro, y definir qué funciones específicas se habilitan.

**Fecha:** 18 de marzo 2026
**Estado:** Decisiones pendientes del usuario

---

## 1. Contexto: Flujo de Usuario (MVP)

```
Usuario crea Notebook
    ↓
Usuario sube Documento (text content) al Notebook
    ↓
Usuario chatea sobre el Documento dentro del Notebook
    ↓
Chat puede referenciar el Documento para context
    ↓
Interacciones se guardan para memoria histórica
```

---

## 2. OPCIÓN A: Estructura Simple (MVP 1.0)

### Modelos

```python
class Notebook(models.Model):
    id = UUIDField(primary_key=True)
    user = ForeignKey(User)
    name = CharField()
    slug = SlugField(unique_for_user=True)
    created_at = DateTimeField(auto_now_add=True)

class Document(models.Model):
    id = UUIDField(primary_key=True)
    user = ForeignKey(User)
    notebook = ForeignKey(Notebook, on_delete=CASCADE)
    
    # MVP: Solo texto plano
    title = CharField(max_length=255)
    content = TextField()  # Texto puro, sin binarios
    
    created_at = DateTimeField(auto_now_add=True)
    
    # Preparación para PDF (campos pero no usados aún)
    # file_path = CharField(null=True, blank=True)  # Path a S3/local
    # file_type = CharField(choices=['txt', 'pdf'], default='txt')
    # pages = IntegerField(null=True)  # Para PDF
    # extracted_text = TextField(blank=True)  # OCR output

class ChatMessage(models.Model):
    id = UUIDField(primary_key=True)
    user = ForeignKey(User)
    notebook = ForeignKey(Notebook)
    
    # Optional: referenciar documento específico
    document_context = ForeignKey(Document, null=True, blank=True, on_delete=SET_NULL)
    
    role = CharField(choices=['user', 'assistant'])
    content = TextField()
    tokens_used = IntegerField(default=0)
    
    created_at = DateTimeField(auto_now_add=True)
```

**Pros:**
- ✅ Simple, MVP rápido
- ✅ User ve documentos en notebook
- ✅ Chat accede a documento si `document_context` no es null
- ✅ Fácil migración a PDF después (agregar campos)

**Contras:**
- ❌ No está optimizado para búsqueda dentro de documento
- ❌ OCR no se integra naturalmente
- ❌ Sin versioning de documento (si se edita, se pierde original)

**Nuevas funciones que trae:**
```
Notebook.documents.all()
    → lista de documentos en notebook
    
ChatMessage.document_context
    → qué documento se usó para esta respuesta
    
# Búsqueda simple
Document.objects.filter(notebook=notebook, content__icontains=query)
    → buscar dentro del documento
```

---

## 3. OPCIÓN B: Estructura con PDF + OCR Ready (MVP 1.5)

### Modelos

```python
class DocumentVersion(models.Model):
    """Versioning para soportar múltiples PDFs / actualizaciones"""
    id = UUIDField(primary_key=True)
    document = ForeignKey('Document', on_delete=CASCADE)
    
    # Metadata de esta versión
    file_type = CharField(choices=['txt', 'pdf', 'image'])
    file_path = CharField(max_length=1000)  # S3 path o local
    file_size = IntegerField()
    upload_date = DateTimeField(auto_now_add=True)
    
    # OCR + Extraction
    extracted_text = TextField(blank=True)  # Text from PDF/OCR
    pages = IntegerField(null=True)  # Para PDF/images
    ocr_status = CharField(
        choices=['pending', 'processing', 'completed', 'failed'],
        default='pending'
    )
    
    # Metadata para búsqueda
    language = CharField(default='es')
    confidence_score = FloatField(null=True)  # OCR confidence

class Document(models.Model):
    id = UUIDField(primary_key=True)
    user = ForeignKey(User)
    notebook = ForeignKey(Notebook, on_delete=CASCADE)
    
    title = CharField(max_length=255)
    description = TextField(blank=True)
    
    # Current version (pointer)
    current_version = ForeignKey(
        DocumentVersion, 
        null=True, 
        on_delete=SET_NULL,
        related_name='+'
    )
    
    # Metadata
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    
    def get_content(self):
        """Obtener texto actual (desde versión o texto directo)"""
        if self.current_version and self.current_version.extracted_text:
            return self.current_version.extracted_text
        return None
    
    def add_pdf(self, file):
        """Crear nueva versión con PDF"""
        version = DocumentVersion.objects.create(
            document=self,
            file_type='pdf',
            file_path=file.path,
            file_size=file.size,
            ocr_status='pending'
        )
        # Signal: disparar Celery task para OCR
        extract_text_from_pdf.delay(version.id)
        return version

class ChatMessage(models.Model):
    # ... mismo que antes
    document_version = ForeignKey(
        DocumentVersion, 
        null=True, 
        blank=True,
        on_delete=SET_NULL
    )
```

**Pros:**
- ✅ Versioning: guardar múltiples PDFs
- ✅ OCR listo: DocumentVersion con extracted_text
- ✅ Auditoria: quién subió qué cuándo
- ✅ Chat sabe exactamente qué versión usó para responder
- ✅ Futuro fácil: agregar Celery para OCR async

**Contras:**
- ⚠️ Más complejo (3 modelos en lugar de 2)
- ⚠️ Necesita migración cuando pasamos de MVP a this

**Nuevas funciones que trae:**
```
document.get_content()
    → obtener texto actual (auto-resuelve de versión o campo)

document.add_pdf(file)
    → crear versión + disparar OCR

document_version.extracted_text
    → acceder a texto extraído por OCR

ChatMessage.document_version
    → rastrear exactamente qué versión se usó

# Búsqueda avanzada
DocumentVersion.objects.filter(
    document__notebook=notebook,
    extracted_text__icontains=query,
    ocr_status='completed'
)
    → buscar solo en OCRs completados
```

---

## 4. OPCIÓN C: Chunks + Embeddings (MVP 2.0 con IA)

### Modelos

```python
class DocumentChunk(models.Model):
    """Dividir documento en chunks para RAG (Retrieval Augmented Generation)"""
    id = UUIDField(primary_key=True)
    document = ForeignKey(Document, on_delete=CASCADE)
    
    # Content chunk
    text = TextField()
    chunk_index = IntegerField()  # 1, 2, 3... para ordenar
    
    # Embeddings (para búsqueda semántica)
    embedding = VectorField(dimensions=1536)  # OpenAI ada-002 dims
    
    # Metadata
    page_number = IntegerField(null=True)  # Para PDFs: qué página
    character_start = IntegerField()  # Char index en documento
    character_end = IntegerField()
    
class ChatMessage(models.Model):
    # ... mismo que antes
    retrieved_chunks = ManyToManyField(
        DocumentChunk,
        blank=True,
        related_name='chat_messages_using_this'
    )
```

**Pros:**
- ✅ RAG: buscar chunks relevantes por similitud semántica
- ✅ Chat sabe exactamente qué fragmentos usó
- ✅ Escalable: chunks pequeños, embeddings reutilizables
- ✅ Futuro con Groq: pasar chunks a LLM para responder

**Contras:**
- ❌ Complejo: necesita pgvector + Celery
- ❌ Costo: generar embeddings (API calls)
- ❌ No es MVP, es Fase 5+

**Nuevas funciones que trae:**
```
DocumentChunk.find_relevant(query_text, top_k=5)
    → buscar chunks relevantes por embedding

ChatMessage.retrieved_chunks.all()
    → qué fragmentos se usaron para esta respuesta

# RAG pipeline
chunks = DocumentChunk.find_relevant(user_question)
groq_response = call_groq(question=user_question, context=chunks)
```

---

## 5. RECOMENDACIÓN: Ruta Híbrida (OPCIÓN B + upgrade)

### Fase 4 (MVP ahora)
- ✅ Usar **OPCIÓN A** (simple): solo Notebook + Document con `content` text
- ✅ Preparar campos vacíos para PDF: `file_path`, `file_type`, `pages`
- ✅ Chat puede referenciar Document sin versioning

### Fase 5 (PDF + OCR)
- Upgrade a **OPCIÓN B**: agregar DocumentVersion
- Implementar PDF upload a S3
- Disparar Celery task para OCR automático

### Fase 6 (IA + RAG)
- Upgrade a **OPCIÓN C**: agregar DocumentChunk + embeddings
- Integrar Groq LLM
- RAG sobre chunks

**Ventajas de esta ruta:**
- 🚀 Rápido: Fase 4 ultra-simple
- 📦 Modular: cada fase agrega sin reescribir
- 🔄 Reversible: si necesitamos cambiar, lo hacemos después
- 📊 Validado: probamos MVP antes de invertir en PDF/OCR

---

## 6. Funciones Específicas que se Habilitan (Fase 4 MVP)

### 6.1 Notebook → Documents

```python
# GET /api/v1/notebooks/{id}/
Response:
{
    "id": "notebook-uuid",
    "name": "Semanal 2026-03",
    "document_count": 5,  ← Cuenta en serializer
    "documents": [        ← Serializer anidado
        {
            "id": "doc-uuid",
            "title": "Resumen ejecutivo",
            "created_at": "2026-03-18"
        },
        ...
    ]
}

# GET /api/v1/documents/?notebook=notebook-uuid
Response: [
    {"id": "...", "title": "...", "content": "..."},
    ...
]
# Función: filtrar docs de un notebook específico para mostrar en UI
```

### 6.2 Document → Chat Context

```python
# Cuando usuario chatea sobre un documento
POST /api/v1/chatmessages/
{
    "notebook": "notebook-uuid",
    "document_context": "doc-uuid",  ← Opcional pero recomendado
    "content": "¿Cuál es el resumen de este documento?"
}

# Backend usa document_context para:
document = Document.objects.get(id=document_context)
context = document.content  # Texto completo
# Pasar a Groq: "Dado este documento: {context}, responde: {user_question}"

Response:
{
    "id": "msg-uuid",
    "role": "assistant",
    "content": "Basado en el documento, el resumen es...",
    "document_context": "doc-uuid"  ← Rastrear qué documento se usó
}
```

### 6.3 Chat History Dentro de Notebook

```python
# GET /api/v1/chatmessages/?notebook=notebook-uuid
Response: [
    {
        "id": "msg-1",
        "role": "user",
        "content": "¿Cuál es el tema?",
        "document_context": null,
        "created_at": "2026-03-18T10:00"
    },
    {
        "id": "msg-2",
        "role": "assistant",
        "content": "El tema es...",
        "document_context": "doc-uuid",
        "created_at": "2026-03-18T10:01"
    }
]

# Función: mostrar timeline de conversación con referencias a documentos
```

### 6.4 Búsqueda Rápida (Prep para OCR)

```python
# GET /api/v1/documents/search/?q=tema&notebook=notebook-uuid
QuerySet:
    Document.objects.filter(
        notebook=notebook,
        content__icontains=query  # Simple text search (MVP)
    )

# Futuro (Fase 5):
# Si tiene OCR, buscar en extracted_text en lugar de content
DocumentVersion.objects.filter(
    document__notebook=notebook,
    extracted_text__icontains=query,
    ocr_status='completed'
)
```

---

## 7. Decisiones Finales para Confirmar

| Decisión | Opción | Impacto |
|----------|--------|--------|
| **Estructura de Document** | A (simple) vs B (versioning) | A = rápido; B = futuro-ready |
| **PDF upload en Fase 4** | No (solo text) | Acelera MVP, PDF en Fase 5 |
| **Chat referencia document** | Sí (`document_context` FK) | Habilita RAG prep |
| **Primero Notebooks, luego Chat** | Sí | Orden correcto: datos → interacción |
| **Nested serializers** | `/notebooks/{id}/` incluye docs | Mejor UX vs más queries |

**Mi recomendación:** 
- ✅ **OPCIÓN A** para Fase 4 (simple, rápido)
- ✅ Campos preparados para OPCIÓN B (futura migración)
- ✅ Chat con `document_context` ahora (costo bajo, valor alto)
- ✅ Primero Notebooks, luego Chat

¿De acuerdo? O prefieres algo diferente?

---

## Referencias

- Ver: `docs/08_modelo_datos.md` (relaciones)
- Ver: `docs/07_contratos_api.md` (endpoints planificados)
- Ver: `docs/09_pasos_decisiones.md` (paso a paso Fase 4)
