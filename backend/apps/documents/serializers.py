from rest_framework import serializers
from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    """Serializer para Document"""
    
    class Meta:
        model = Document
        fields = (
            'id',
            'user',
            'notebook',
            'title',
            'original_filename',
            'file_type',
            'file_path',
            'file_size',
            'pages',
            'content',
            'content_markdown',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')


class DocumentCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear Document (MVP: sin archivo aún)"""
    
    class Meta:
        model = Document
        fields = ('notebook', 'title', 'original_filename', 'content', 'file_type')
    
    def validate_content(self, value):
        """Validar que contenido no esté vacío"""
        if not value or not value.strip():
            raise serializers.ValidationError("El contenido no puede estar vacío")
        return value


class DocumentListSerializer(serializers.ModelSerializer):
    """Serializer comprimido para listar documentos"""
    
    class Meta:
        model = Document
        fields = ('id', 'title', 'file_type', 'file_size', 'created_at')
        read_only_fields = ('id', 'created_at')
