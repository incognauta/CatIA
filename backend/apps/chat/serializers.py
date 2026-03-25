from rest_framework import serializers
from .models import ChatMessage


class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializer para ChatMessage"""
    
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = ChatMessage
        fields = (
            'id',
            'user',
            'notebook',
            'document',
            'role',
            'role_display',
            'content',
            'tokens_used',
            'created_at',
        )
        read_only_fields = ('id', 'user', 'created_at', 'tokens_used')


class ChatMessageCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear ChatMessage"""
    
    class Meta:
        model = ChatMessage
        fields = ('notebook', 'document', 'role', 'content')
    
    def validate_content(self, value):
        """Validar que contenido no esté vacío"""
        if not value or not value.strip():
            raise serializers.ValidationError("El mensaje no puede estar vacío")
        return value


class ChatHistorySerializer(serializers.ModelSerializer):
    """Serializer comprimido para historial de chat"""
    
    class Meta:
        model = ChatMessage
        fields = ('id', 'role', 'content', 'created_at', 'tokens_used')
        read_only_fields = ('id', 'created_at', 'tokens_used')
