from django.contrib import admin
from .models import Notebook


@admin.register(Notebook)
class NotebookAdmin(admin.ModelAdmin):
    """Admin para Notebooks"""
    
    list_display = ('name', 'user', 'icon', 'is_default', 'documents_count', 'created_at')
    list_filter = ('is_default', 'created_at', 'color')
    search_fields = ('name', 'user__username', 'slug')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Información', {
            'fields': ('id', 'user', 'name', 'slug', 'description')
        }),
        ('Presentación', {
            'fields': ('icon', 'color')
        }),
        ('Configuración', {
            'fields': ('is_default',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ('-created_at',)
    
    def documents_count(self, obj):
        """Mostrar cantidad de documentos en el notebook"""
        return obj.documents.count()
    documents_count.short_description = 'Documentos'
