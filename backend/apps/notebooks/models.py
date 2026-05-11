import uuid

from django.conf import settings
from django.db import models


class Notebook(models.Model):
    """
    Notebook: Contenedor lógico para documentos
    Un usuario puede tener múltiples notebooks (Matemáticas, Leyes, etc)
    Ver: docs/11_fase4_mvp_hibrido.md#Fase 4A - Notebooks
    Ver: docs/08_modelo_datos.md#notebook
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notebooks'
    )
    
    # Datos básicos
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    # Presentación
    color = models.CharField(
        max_length=7,
        default='#1976d2'  # Hex color
    )
    icon = models.CharField(
        max_length=50,
        default='📚'  # Emoji
    )
    
    # Metadata
    is_default = models.BooleanField(
        default=False  # Los 4 notebooks iniciales son default
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'notebooks'
        # La combinación (user, slug) es única
        unique_together = [['user', 'slug']]
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.name} (user: {self.user.username})"
