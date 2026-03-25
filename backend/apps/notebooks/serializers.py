from rest_framework import serializers
from .models import Notebook


class NotebookSerializer(serializers.ModelSerializer):
    """Serializer para Notebook"""
    
    documents_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Notebook
        fields = (
            'id',
            'user',
            'name',
            'slug',
            'description',
            'color',
            'icon',
            'is_default',
            'documents_count',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def get_documents_count(self, obj):
        """Contar documentos en el notebook"""
        return obj.documents.count()
    
    def validate_slug(self, value):
        """Validar que slug sea único por usuario"""
        user = self.context['request'].user
        queryset = Notebook.objects.filter(user=user, slug=value)
        
        # Si estamos editando, excluir la instancia actual
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError("Ya existe un notebook con este slug")
        
        return value


class NotebookCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para crear/actualizar Notebook"""
    
    class Meta:
        model = Notebook
        fields = ('name', 'slug', 'description', 'color', 'icon', 'is_default')
