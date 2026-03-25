from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, UserProfile, Plan, UserSubscription


class UserProfileInline(admin.TabularInline):
    """
    Mostrar UserProfile dentro del admin de User.
    Ver: docs/06_estructura_backend.md#admin-pattern
    """
    model = UserProfile
    extra = 0
    fields = ('bio', 'avatar_url', 'preferred_language', 'subscription_expires_at')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin customizado para User.
    Ver: docs/06_estructura_backend.md#admin-pattern
    """
    
    inlines = [UserProfileInline]
    
    # Campos mostrados en lista
    list_display = ('username', 'email', 'subscription_tier', 'email_verified', 'is_staff')
    list_filter = ('subscription_tier', 'email_verified', 'is_staff', 'created_at')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    # Agrupar campos en formulario
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Subscription', {
            'fields': ('subscription_tier', 'email_verified')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin para UserProfile.
    Ver: docs/06_estructura_backend.md#admin-pattern
    """
    
    list_display = ('user', 'preferred_language', 'subscription_expires_at', 'created_at')
    list_filter = ('preferred_language', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Usuario', {
            'fields': ('user',)
        }),
        ('Perfil', {
            'fields': ('bio', 'avatar_url', 'preferred_language')
        }),
        ('Suscripción', {
            'fields': ('subscription_expires_at',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    """
    Admin para Plan de suscripción.
    Ver: docs/11_fase4_mvp_hibrido.md#Plan
    """
    
    list_display = ('name', 'price', 'documents_limit', 'messages_per_month', 'created_at')
    list_filter = ('name', 'price', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('id', 'created_at')
    
    fieldsets = (
        ('Información', {
            'fields': ('id', 'name', 'description', 'price')
        }),
        ('Límites', {
            'fields': ('documents_limit', 'messages_per_month', 'file_size_limit')
        }),
        ('Features', {
            'fields': ('features',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    """
    Admin para UserSubscription.
    Ver: docs/11_fase4_mvp_hibrido.md#UserSubscription
    """
    
    list_display = ('user', 'plan', 'status', 'expires_at', 'documents_used', 'started_at')
    list_filter = ('status', 'plan', 'started_at', 'expires_at')
    search_fields = ('user__username', 'user__email', 'plan__name')
    readonly_fields = ('id', 'started_at', 'updated_at')
    
    fieldsets = (
        ('Usuario y Plan', {
            'fields': ('id', 'user', 'plan')
        }),
        ('Estado', {
            'fields': ('status', 'started_at', 'expires_at')
        }),
        ('Uso', {
            'fields': ('documents_used', 'messages_used_this_month')
        }),
        ('Metadata', {
            'fields': ('updated_at',),
            'classes': ('collapse',)
        }),
    )

