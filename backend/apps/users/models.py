import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):
    """
    Usuario personalizado que extiende AbstractUser.
    Ver: docs/08_modelo_datos.md#user (campos y validaciones)
    """
    
    SUBSCRIPTION_TIERS = [
        ('FREE', 'Free'),
        ('PREMIUM', 'Premium'),
        ('ADMIN', 'Admin'),
    ]
    
    email = models.EmailField(unique=True)  # Email único (constraint BD)
    subscription_tier = models.CharField(
        max_length=10,
        choices=SUBSCRIPTION_TIERS,
        default='FREE'
    )
    email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        # Ver: docs/06_estructura_backend.md#naming-convention
        app_label = 'users'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.username} ({self.email})"


class UserProfile(models.Model):
    """
    Perfil del usuario con datos adicionales.
    Relación 1-a-1 con User.
    Ver: docs/08_modelo_datos.md#userprofile (campos y relaciones)
    """
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    bio = models.TextField(blank=True, null=True, max_length=500)
    avatar_url = models.URLField(blank=True, null=True)
    preferred_language = models.CharField(
        max_length=10,
        default='es',
        choices=[('es', 'Español'), ('en', 'English')]
    )
    subscription_expires_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        # Ver: docs/06_estructura_backend.md#naming-convention
        app_label = 'users'
    
    def __str__(self):
        return f"Profile: {self.user.username}"


class Plan(models.Model):
    """
    Plan de suscripción disponible en la plataforma.
    Define límites y features según el plan.
    Ver: docs/11_fase4_mvp_hibrido.md#Fase 4A - Plan model
    """
    
    PLAN_CHOICES = [
        ('free', 'Free'),
        ('pro', 'Pro'),
        ('enterprise', 'Enterprise'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=100,
        unique=True,
        choices=PLAN_CHOICES
    )
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Límites de uso
    documents_limit = models.IntegerField(
        default=5
        # Free: 5, Pro: 100, Enterprise: ilimitado
    )
    messages_per_month = models.IntegerField(
        default=100
        # Mensajes con IA por mes (Groq)
    )
    file_size_limit = models.BigIntegerField(
        default=5242880
        # Bytes (5MB por default)
    )
    
    # Features (qué funcionalidades están habilitadas)
    features = models.JSONField(
        default=list
        # Ej: ['ocr', 'export', 'sharing']
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'users'
        ordering = ['price']
    
    def __str__(self):
        return f"{self.name} - ${self.price}"


class UserSubscription(models.Model):
    """
    Suscripción actual del usuario a un plan específico.
    Relación 1-a-1 con User (un usuario, un plan vigente).
    Ver: docs/11_fase4_mvp_hibrido.md#Fase 4A - UserSubscription model
    """
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('canceled', 'Canceled'),
        ('trial', 'Trial'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='subscription'
    )
    plan = models.ForeignKey(
        Plan,
        on_delete=models.SET_NULL,
        null=True
    )
    
    # Estado
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='trial'
    )
    started_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Tracking de uso (para Fase 5)
    documents_used = models.IntegerField(default=0)
    messages_used_this_month = models.IntegerField(default=0)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'users'
    
    def __str__(self):
        return f"{self.user.username} - {self.plan.name if self.plan else 'No Plan'}"


# ============================================================================
# SIGNALS: Auto-crear relaciones al crear User
# ============================================================================

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal: crear UserProfile automáticamente al crear User.
    Ver: docs/09_pasos_decisiones.md#fase-2-paso-22 (por qué signal)
    """
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Signal: guardar UserProfile al guardar User (si existe).
    """
    try:
        instance.userprofile.save()
    except UserProfile.DoesNotExist:
        pass


@receiver(post_save, sender=User)
def create_user_subscription(sender, instance, created, **kwargs):
    """
    Signal: crear UserSubscription automáticamente al crear User.
    El usuario nuevo comienza con plan 'free' en estado 'trial'.
    Ver: docs/11_fase4_mvp_hibrido.md#Fase 4A - Signals
    """
    if created:
        # Obtener o crear Plan 'free'
        free_plan, _ = Plan.objects.get_or_create(
            name='free',
            defaults={
                'description': 'Free plan with limited features',
                'price': 0,
                'documents_limit': 5,
                'messages_per_month': 100,
                'file_size_limit': 5242880,
                'features': []
            }
        )
        UserSubscription.objects.create(
            user=instance,
            plan=free_plan,
            status='trial'
        )