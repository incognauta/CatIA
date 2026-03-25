from django.test import TestCase
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

from .models import UserProfile


User = get_user_model()


class UserModelTests(TestCase):
    """
    Tests básicos para el modelo User.
    Ver: docs/09_pasos_decisiones.md#fase-2-paso-25 (testing-pattern)
    """
    
    def setUp(self):
        """Datos de prueba"""
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'secure_password_123',
            'first_name': 'Test',
            'last_name': 'User'
        }
    
    def test_create_user(self):
        """Crear user correctamente"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.username, self.user_data['username'])
        self.assertEqual(user.email, self.user_data['email'])
        self.assertTrue(user.check_password(self.user_data['password']))
    
    def test_email_unique(self):
        """Email es único—no se puede duplicar"""
        User.objects.create_user(**self.user_data)
        
        # Intentar crear otro con mismo email
        duplicate_data = self.user_data.copy()
        duplicate_data['username'] = 'different_username'
        
        with self.assertRaises(IntegrityError):
            User.objects.create_user(**duplicate_data)
    
    def test_password_hashed(self):
        """Password no está en plaintext—está hashed"""
        user = User.objects.create_user(**self.user_data)
        self.assertNotEqual(user.password, self.user_data['password'])
        self.assertTrue(user.password.startswith('pbkdf2_sha256$'))
    
    def test_default_subscription_tier(self):
        """Por defecto, subscription_tier es FREE"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.subscription_tier, 'FREE')
    
    def test_user_str_representation(self):
        """Representación en string es útil"""
        user = User.objects.create_user(**self.user_data)
        expected = f"{self.user_data['username']} ({self.user_data['email']})"
        self.assertEqual(str(user), expected)


class UserProfileSignalTests(TestCase):
    """
    Tests para los signals: auto-crear Profile al crear User.
    Ver: docs/09_pasos_decisiones.md#fase-2-paso-22 (por qué signal)
    """
    
    def setUp(self):
        """Datos de prueba"""
        self.user_data = {
            'username': 'profiletest',
            'email': 'profile@example.com',
            'password': 'secure_password_123'
        }
    
    def test_profile_auto_created(self):
        """Al crear User, automáticamente se crea su Profile"""
        user = User.objects.create_user(**self.user_data)
        
        # Profile debe existir sin haberlo creado manualmente
        self.assertTrue(UserProfile.objects.filter(user=user).exists())
        profile = user.userprofile
        self.assertIsNotNone(profile)
    
    def test_profile_cascade_delete(self):
        """Al eliminar User, Profile se elimina también (CASCADE)"""
        user = User.objects.create_user(**self.user_data)
        profile_id = user.userprofile.id
        
        # Eliminar User
        user.delete()
        
        # Profile no debe existir
        self.assertFalse(UserProfile.objects.filter(id=profile_id).exists())
    
    def test_profile_one_to_one_relation(self):
        """Un User solo puede tener un Profile (1-a-1)"""
        user = User.objects.create_user(**self.user_data)
        
        # El Profile debe ser accesible via user.userprofile (reverse relation)
        self.assertEqual(user.userprofile.user.id, user.id)


class RegisterViewTests(APITestCase):
    """
    Tests para endpoint de registro.
    Ver: docs/09_pasos_decisiones.md#fase-3-paso-34 (testing-pattern)
    """
    
    def setUp(self):
        """Datos de prueba"""
        self.register_url = '/api/v1/auth/register/'
        self.valid_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
            'first_name': 'New',
            'last_name': 'User'
        }
    
    def test_register_successfully(self):
        """POST /auth/register/ con datos válidos crea User + Profile"""
        response = self.client.post(self.register_url, self.valid_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        
        # Verificar que User se creó
        user = User.objects.get(email=self.valid_data['email'])
        self.assertEqual(user.username, self.valid_data['username'])
        
        # Verificar que UserProfile se creó (via signal)
        self.assertTrue(hasattr(user, 'userprofile'))
    
    def test_register_email_duplicate(self):
        """Email duplicado retorna 400"""
        User.objects.create_user(
            username='existing',
            email='existing@example.com',
            password='pass123'
        )
        
        duplicate_data = self.valid_data.copy()
        duplicate_data['email'] = 'existing@example.com'
        duplicate_data['username'] = 'different'
        
        response = self.client.post(self.register_url, duplicate_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_register_password_mismatch(self):
        """Passwords no coinciden retorna 400"""
        bad_data = self.valid_data.copy()
        bad_data['password_confirm'] = 'DifferentPass123!'
        
        response = self.client.post(self.register_url, bad_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginViewTests(APITestCase):
    """
    Tests para endpoint de login.
    Ver: docs/09_pasos_decisiones.md#fase-3-paso-34 (testing-pattern)
    """
    
    def setUp(self):
        """Crear usuario de prueba"""
        self.login_url = '/api/v1/auth/login/'
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='SecurePass123!'
        )
    
    def test_login_successfully(self):
        """POST /auth/login/ con credenciales válidas retorna tokens"""
        data = {
            'email': 'test@example.com',
            'password': 'SecurePass123!'
        }
        
        response = self.client.post(self.login_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
    
    def test_login_invalid_password(self):
        """Contraseña incorrecta retorna 400"""
        data = {
            'email': 'test@example.com',
            'password': 'WrongPassword123!'
        }
        
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_login_nonexistent_email(self):
        """Email no existe retorna 400"""
        data = {
            'email': 'nonexistent@example.com',
            'password': 'SecurePass123!'
        }
        
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserMeViewTests(APITestCase):
    """
    Tests para endpoint GET /users/me/ (perfil del usuario autenticado).
    Ver: docs/09_pasos_decisiones.md#fase-3-paso-34 (testing-pattern)
    """
    
    def setUp(self):
        """Crear usuario y generar token"""
        self.me_url = '/api/v1/users/me/'
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='SecurePass123!'
        )
    
    def test_get_user_me_authenticated(self):
        """GET /users/me/ con token retorna perfil del usuario"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.me_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.user.id)
        self.assertEqual(response.data['username'], self.user.username)
        self.assertEqual(response.data['email'], self.user.email)
        self.assertIn('userprofile', response.data)
    
    def test_get_user_me_unauthenticated(self):
        """GET /users/me/ sin autenticación retorna 401"""
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PermissionsTests(APITestCase):
    """
    Tests para validar permisos.
    Ver: docs/05_arquitectura_general.md#security
    """
    
    def setUp(self):
        """Crear usuarios"""
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='AdminPass123!',
            subscription_tier='ADMIN',
            is_staff=True
        )
        self.regular_user = User.objects.create_user(
            username='regular',
            email='regular@example.com',
            password='RegularPass123!'
        )
    
    def test_admin_can_list_users(self):
        """Admin puede ver lista de todos los usuarios"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/v1/users/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 1)
    
    def test_regular_user_can_list_only_themselves(self):
        """Usuario regular solo ve su propio usuario"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get('/api/v1/users/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # response.data is paginated, so check if regular user is in results
        if isinstance(response.data, list):
            user_ids = [u['id'] for u in response.data]
            self.assertIn(self.regular_user.id, user_ids)
            self.assertNotIn(self.admin_user.id, user_ids)
        else:
            # Si está paginada, verificar que el admin user no esté
            self.assertIn('results', response.data)
            user_ids = [u['id'] for u in response.data['results']]
            self.assertIn(self.regular_user.id, user_ids)
            self.assertNotIn(self.admin_user.id, user_ids)

