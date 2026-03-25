from django.contrib import admin
from .models import ChatMessage


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    """Admin para ChatMessages"""
    
    list_display = ('role_badge', 'user', 'notebook', 'document', 'tokens_used', 'created_at')
    list_filter = ('role', 'created_at', 'notebook')
    search_fields = ('content', 'user__username', 'notebook__name')
    readonly_fields = ('id', 'created_at')
    
    fieldsets = (
        ('Información', {
            'fields': ('id', 'user', 'notebook', 'document')
        }),
        ('Mensaje', {
            'fields': ('role', 'content')
        }),
        ('Tracking', {
            'fields': ('tokens_used',)
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ('-created_at',)
    
    def role_badge(self, obj):
        """Mostrar rol con color"""
        if obj.role == 'user':
            return '👤 User'
        elif obj.role == 'assistant':
            return '🤖 Assistant'
        return obj.role
    role_badge.short_description = 'Rol'
    
    # Hacer el contenido editable pero tomar precauciones
    def get_readonly_fields(self, request, obj=None):
        if obj:  # En edición, no permitir cambiar estos campos
            return self.readonly_fields + ['user', 'notebook', 'document', 'role']
        return self.readonly_fields
