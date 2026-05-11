from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.


# Opciones de modelos disponibles en Groq
GROQ_MODEL_CHOICES = [
    ('llama-3.1-8b-instant', 'Llama 3.1 8B (Rápido - Recomendado)'),
    ('llama-3.1-70b-versatile', 'Llama 3.1 70B (Versátil)'),
    ('mixtral-8x7b-32768', 'Mixtral 8x7B (Balance)'),
    ('gemma-7b-it', 'Gemma 7B (Ligero)'),
]


class UserLLMSettings(models.Model):
    """
    Configuración personalizada de LLM por usuario.
    Permite que cada usuario tenga sus propias preferencias de modelo,
    temperatura y límite de tokens.
    
    Fase 6: Mejora - UI de Configuración
    """
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='llm_settings',
        help_text="Usuario propietario de estas configuraciones"
    )
    
    model = models.CharField(
        max_length=100,
        default='llama-3.1-8b-instant',  # Valor fijo
        choices=GROQ_MODEL_CHOICES,
        help_text="Modelo de Groq a usar"
    )
    
    temperature = models.FloatField(
        default=0.7,  # Valor fijo
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Temperatura (0=determinístico, 1=creativo)"
    )
    
    max_tokens = models.IntegerField(
        default=1024,  # Valor fijo
        validators=[MinValueValidator(256), MaxValueValidator(4096)],
        help_text="Máximo de tokens en la respuesta"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Configuración de LLM del Usuario"
        verbose_name_plural = "Configuraciones de LLM"
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.model}"
    
    def to_dict(self):
        """Retornar como diccionario para serialización"""
        return {
            'model': self.model,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
        }
    
    @classmethod
    def get_or_create_for_user(cls, user):
        """
        Obtener o crear configuración para un usuario.
        Si no existe, crea con valores por defecto.
        """
        settings_obj, created = cls.objects.get_or_create(user=user)
        return settings_obj, created
    
    @classmethod
    def get_defaults(cls):
        """Retornar diccionario con valores por defecto del sistema"""
        return {
            'model': settings.GROQ_CONFIG['MODEL'],
            'temperature': settings.GROQ_CONFIG['TEMPERATURE'],
            'max_tokens': settings.GROQ_CONFIG['MAX_TOKENS'],
        }

