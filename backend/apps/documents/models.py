import uuid

from django.conf import settings
from django.db import models
from pgvector.django import VectorField


class Document(models.Model):
    """
    Document: Documento cargado por usuario
    Contiene contenido en texto/markdown y es parte de un Notebook
    Ver: docs/11_fase4_mvp_hibrido.md#Fase 4A - Documents
    Ver: docs/08_modelo_datos.md#document
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    notebook = models.ForeignKey(
        'notebooks.Notebook',
        on_delete=models.CASCADE,
        related_name='documents'
    )
    
    # Metadata del archivo
    title = models.CharField(max_length=255)
    original_filename = models.CharField(max_length=255)
    
    # Contenido
    content = models.TextField()  # Contenido en texto o markdown
    content_markdown = models.TextField(
        blank=True,
        null=True
    )  # Markdown procesado (para Fase 4B)
    
    # Información del archivo (preparado para Fase 4B - PDF processing)
    file_type = models.CharField(
        max_length=20,
        default='txt',
        blank=True
        # Opciones: 'txt', 'md', 'pdf', 'jpg', 'png', etc
    )
    file_path = models.CharField(
        max_length=500,
        blank=True,
        null=True
        # Path a almacenamiento (local o S3)
    )
    file_size = models.BigIntegerField(
        null=True,
        blank=True
        # Bytes
    )
    pages = models.IntegerField(
        null=True,
        blank=True
        # Para PDFs: número de páginas
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'documents'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'notebook']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} (notebook: {self.notebook.name})"


class DocumentChunk(models.Model):
    """
    Fragmento de documento con embedding vectorial para búsqueda semántica.

    Cada chunk contiene una porción del documento original y su vector
    de embedding (384 dimensiones) para búsqueda por similitud coseno.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='chunks'
    )
    chunk_index = models.IntegerField(
        help_text="Índice del chunk dentro del documento"
    )
    content = models.TextField(
        help_text="Contenido textual de este fragmento"
    )
    embedding = VectorField(
        dimensions=384,
        null=True,
        blank=True,
        help_text="Vector de embedding (384 dimensiones)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'documents'
        ordering = ['document', 'chunk_index']
        indexes = [
            models.Index(fields=['document', 'chunk_index']),
        ]

    def __str__(self):
        return f"Chunk {self.chunk_index} de {self.document.title}"
