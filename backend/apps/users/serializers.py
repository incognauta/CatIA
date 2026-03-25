from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import UserProfile

# Ver: docs/07_contratos_api.md#auth-endpoints (esquemas y validaciones)
User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializar UserProfile.
    Ver: docs/07_contratos_api.md#userprofile-response
    """
    class Meta:
        model = UserProfile
        fields = ('bio', 'avatar_url', 'preferred_language', 'subscription_expires_at', 'created_at')


class UserSerializer(serializers.ModelSerializer):
    """
    Serializar User: datos públicos del usuario.
    Ver: docs/07_contratos_api.md#user-response
    """
    userprofile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'subscription_tier', 'email_verified', 'userprofile', 'created_at')
        read_only_fields = ('id', 'email_verified', 'created_at')


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializar para registro: crear nuevo User.
    Validaciones:
    - email: único, formato válido
    - password: confirmación, no en plaintext
    - username: requerido
    Ver: docs/07_contratos_api.md#register
    """
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm', 'first_name', 'last_name')
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True},
            'first_name': {'required': False},
            'last_name': {'required': False}
        }
    
    def validate(self, data):
        """
        Validar que passwords coinciden.
        Ver: docs/06_estructura_backend.md#validation-pattern
        """
        if data['password'] != data.pop('password_confirm'):
            raise serializers.ValidationError({'password': 'Las contraseñas no coinciden.'})
        return data
    
    def validate_email(self, value):
        """Validar que email es único."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Este email ya está registrado.')
        return value
    
    def validate_username(self, value):
        """Validar que username es único."""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Este nombre de usuario ya existe.')
        return value
    
    def create(self, validated_data):
        """
        Crear User y automáticamente UserProfile (via signal).
        Ver: docs/09_pasos_decisiones.md#fase-2-paso-22 (signals)
        """
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializar para login: validar email + password.
    Ver: docs/07_contratos_api.md#login
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    def validate(self, data):
        """
        Validar que el usuario existe y contraseña es correcta.
        Ver: docs/06_estructura_backend.md#validation-pattern
        """
        email = data.get('email')
        password = data.get('password')
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError('Email o contraseña inválidos.')
        
        if not user.check_password(password):
            raise serializers.ValidationError('Email o contraseña inválidos.')
        
        data['user'] = user
        return data
