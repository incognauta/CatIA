from django.db import models
from django.conf import settings
import uuid


class ChatMessage(models.Model):
    """
    ChatMessage: Mensaje en conversación con IA
    Cada mensaje está asociado a un Usuario, Notebook y opcionalmente a un Document
    Ver: docs/11_fase4_mvp_hibrido.md#Fase 4A - ChatMessage
    Ver: docs/08_modelo_datos.md#chatmessage
    """
    
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat_messages'
    )
    notebook = models.ForeignKey(
        'notebooks.Notebook',
        on_delete=models.CASCADE,
        related_name='chat_messages'
    )
    
    # Referencia opcional al documento sobre el cual se consulta
    document = models.ForeignKey(
        'documents.Document',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='chat_messages'
    )
    
    # Contenido del mensaje
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
        # 'user' = mensaje del usuario
        # 'assistant' = respuesta de la IA (Groq)
    )
    content = models.TextField()
    
    # Tracking de uso
    tokens_used = models.IntegerField(
        default=0
        # Tokens consumidos de Groq API
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'chat'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['user', 'notebook']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"[{self.role}] {self.user.username} in {self.notebook.name}"
