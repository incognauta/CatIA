from rest_framework import serializers
from django.conf import settings
from .models import UserLLMSettings, GROQ_MODEL_CHOICES


class UserLLMSettingsSerializer(serializers.ModelSerializer):
    """Serializer para UserLLMSettings"""
    
    available_models = serializers.SerializerMethodField()
    temperature_range = serializers.SerializerMethodField()
    max_tokens_range = serializers.SerializerMethodField()
    
    class Meta:
        model = UserLLMSettings
        fields = [
            'id',
            'user',
            'model',
            'temperature',
            'max_tokens',
            'created_at',
            'updated_at',
            'available_models',
            'temperature_range',
            'max_tokens_range',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_available_models(self, obj):
        """Retornar lista de modelos disponibles con etiquetas"""
        return [
            {'value': choice[0], 'label': choice[1]} 
            for choice in GROQ_MODEL_CHOICES
        ]
    
    def get_temperature_range(self, obj):
        """Retornar rango válido de temperatura"""
        return {
            'min': 0.0,
            'max': 1.0,
            'step': 0.1,
            'description': '0 = Determinístico (respuestas consistentes), 1 = Creativo (respuestas variadas)'
        }
    
    def get_max_tokens_range(self, obj):
        """Retornar rango válido de tokens"""
        return {
            'min': 256,
            'max': 4096,
            'step': 256,
            'description': 'Máximo número de tokens en la respuesta'
        }
    
    def validate_temperature(self, value):
        """Validar que temperatura esté en rango [0, 1]"""
        if not (0.0 <= value <= 1.0):
            raise serializers.ValidationError(
                "Temperatura debe estar entre 0.0 y 1.0"
            )
        return value
    
    def validate_max_tokens(self, value):
        """Validar que max_tokens esté en rango [256, 4096]"""
        if not (256 <= value <= 4096):
            raise serializers.ValidationError(
                "Max tokens debe estar entre 256 y 4096"
            )
        return value


class LLMSettingsDefaultsSerializer(serializers.Serializer):
    """Serializer para obtener valores por defecto del sistema"""
    
    model = serializers.CharField()
    temperature = serializers.FloatField()
    max_tokens = serializers.IntegerField()
    available_models = serializers.ListField()
    temperature_range = serializers.DictField()
    max_tokens_range = serializers.DictField()
