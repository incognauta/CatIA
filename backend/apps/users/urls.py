from django.urls import path
from .views import RegisterView, LoginView, UserMeView, UserListView

# Ver: docs/07_contratos_api.md (rutas y métodos HTTP)
app_name = 'users'

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('users/me/', UserMeView.as_view(), name='user-me'),
    path('users/', UserListView.as_view(), name='user-list'),
]
