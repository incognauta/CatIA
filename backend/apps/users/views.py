from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserSerializer, RegisterSerializer, LoginSerializer

# Ver: docs/06_estructura_backend.md#views-pattern (patrón de views)
User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    POST /api/v1/auth/register/
    Crear nuevo usuario + perfil.
    
    Permisos: AllowAny (anónimo)
    Request: {username, email, password, password_confirm, first_name?, last_name?}
    Response: {id, username, email, subscription_tier, userprofile, created_at}
    
    Ver: docs/07_contratos_api.md#register
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        """
        Override para retornar User data + tokens.
        Ver: docs/07_contratos_api.md#register-response
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generar tokens JWT
        refresh = RefreshToken.for_user(user)
        
        user_data = UserSerializer(user).data
        
        return Response({
            'user': user_data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    """
    POST /api/v1/auth/login/
    Autenticar usuario y retornar tokens.
    
    Permisos: AllowAny (anónimo)
    Request: {email, password}
    Response: {access, refresh}
    
    Ver: docs/07_contratos_api.md#login
    """
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        
        # Generar tokens JWT
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data,
        }, status=status.HTTP_200_OK)


class UserMeView(generics.RetrieveUpdateAPIView):
    """
    GET /api/v1/users/me/
    PUT /api/v1/users/me/
    Retornar/actualizar perfil del usuario autenticado.
    
    Permisos: IsAuthenticated
    Response: {id, username, email, subscription_tier, userprofile, created_at}
    
    Ver: docs/07_contratos_api.md#get-user-me
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        """Retornar el usuario autenticado."""
        return self.request.user


class UserListView(generics.ListAPIView):
    """
    GET /api/v1/users/
    Listar usuarios (admin solo).
    
    Permisos: IsAuthenticated + IsAdmin
    Response: [{id, username, email, subscription_tier, ...}, ...]
    
    Ver: docs/07_contratos_api.md#get-users-list
    """
    queryset = User.objects.all().order_by('-created_at')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Solo admins ven la lista.
        Ver: docs/05_arquitectura_general.md#security
        """
        user = self.request.user
        if user.is_staff or user.subscription_tier == 'ADMIN':
            return User.objects.all().order_by('-created_at')
        # No-admin solo ve su propio usuario
        return User.objects.filter(id=user.id)
