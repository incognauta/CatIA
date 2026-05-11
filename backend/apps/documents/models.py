import uuid

from django.conf import settings
from django.db import models


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
