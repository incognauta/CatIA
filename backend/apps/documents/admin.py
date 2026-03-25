from django.contrib import admin
from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """Admin para Documents"""
    
    list_display = ('title', 'user', 'notebook', 'file_type', 'file_size_display', 'created_at')
    list_filter = ('file_type', 'created_at', 'notebook')
    search_fields = ('title', 'user__username', 'original_filename')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Información', {
            'fields': ('id', 'user', 'notebook')
        }),
        ('Metadata', {
            'fields': ('title', 'original_filename', 'file_type', 'file_path', 'file_size', 'pages')
        }),
        ('Contenido', {
            'fields': ('content', 'content_markdown'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ('-created_at',)
    
    def file_size_display(self, obj):
        """Mostrar tamaño de archivo en formato legible"""
        if not obj.file_size:
            return '—'
        size_bytes = obj.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
    file_size_display.short_description = 'Tamaño'
