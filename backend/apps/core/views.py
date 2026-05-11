import logging

from django.conf import settings
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import UserLLMSettings, GROQ_MODEL_CHOICES
from .serializers import UserLLMSettingsSerializer, LLMSettingsDefaultsSerializer

logger = logging.getLogger(__name__)


class UserLLMSettingsViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar configuración personalizada de LLM por usuario.
    
    Endpoints:
    - GET /api/v1/llm-settings/ - Ver mi configuración
    - PUT /api/v1/llm-settings/{id}/ - Actualizar mi configuración
    - PATCH /api/v1/llm-settings/{id}/ - Actualizar parcialmente
    - POST /api/v1/llm-settings/defaults/ - Obtener valores por defecto
    
    Fase 6: Mejora - UI de Configuración
    """
    
    serializer_class = UserLLMSettingsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Solo devolver la configuración del usuario autenticado"""
        return UserLLMSettings.objects.filter(user=self.request.user)
    
    def get_object(self):
        """Obtener o crear la configuración del usuario autenticado"""
        obj, created = UserLLMSettings.get_or_create_for_user(self.request.user)
        return obj
    
    def list(self, request, *args, **kwargs):
        """
        GET /api/v1/llm-settings/
        Retorna la configuración del usuario o crea una nueva con defaults.
        """
        settings_obj, created = UserLLMSettings.get_or_create_for_user(request.user)
        serializer = self.get_serializer(settings_obj)
        
        if created:
            logger.info(f"Configuración LLM creada para usuario: {request.user}")
        
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        """GET /api/v1/llm-settings/{id}/ - Obtener configuración específica"""
        return super().retrieve(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        """PUT /api/v1/llm-settings/{id}/ - Actualizar toda la configuración"""
        settings_obj = self.get_object()
        serializer = self.get_serializer(settings_obj, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        logger.info(
            f"Configuración LLM actualizada para {request.user}: "
            f"model={serializer.data['model']}, "
            f"temp={serializer.data['temperature']}, "
            f"tokens={serializer.data['max_tokens']}"
        )
        
        return Response(serializer.data)
    
    def partial_update(self, request, *args, **kwargs):
        """PATCH /api/v1/llm-settings/{id}/ - Actualizar solo algunos campos"""
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'])
    def defaults(self, request):
        """
        GET /api/v1/llm-settings/defaults/
        
        Obtener valores por defecto del sistema y opciones disponibles.
        Útil para inicializar formulario en frontend.
        """
        defaults = {
            'model': settings.GROQ_CONFIG['MODEL'],
            'temperature': settings.GROQ_CONFIG['TEMPERATURE'],
            'max_tokens': settings.GROQ_CONFIG['MAX_TOKENS'],
            'available_models': [
                {'value': choice[0], 'label': choice[1]} 
                for choice in GROQ_MODEL_CHOICES
            ],
            'temperature_range': {
                'min': 0.0,
                'max': 1.0,
                'step': 0.1,
            },
            'max_tokens_range': {
                'min': 256,
                'max': 4096,
                'step': 256,
            },
        }
        
        return Response(defaults, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def reset(self, request):
        """
        POST /api/v1/llm-settings/reset/
        
        Resetear la configuración del usuario a valores por defecto del sistema.
        """
        settings_obj = self.get_object()
        
        settings_obj.model = settings.GROQ_CONFIG['MODEL']
        settings_obj.temperature = settings.GROQ_CONFIG['TEMPERATURE']
        settings_obj.max_tokens = settings.GROQ_CONFIG['MAX_TOKENS']
        settings_obj.save()
        
        logger.info(f"Configuración LLM reseteada para {request.user}")
        
        serializer = self.get_serializer(settings_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

