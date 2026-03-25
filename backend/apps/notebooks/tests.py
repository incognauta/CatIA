from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Notebook

User = get_user_model()


class NotebookModelTestCase(TestCase):
    """Tests para modelo Notebook"""
    
    def setUp(self):
        """Crear usuario y datos de prueba"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_notebook(self):
        """Test: crear notebook básico"""
        notebook = Notebook.objects.create(
            user=self.user,
            name='Matemáticas',
            slug='matematicas',
            description='Notebook de matemáticas'
        )
        self.assertEqual(notebook.name, 'Matemáticas')
        self.assertEqual(notebook.slug, 'matematicas')
        self.assertEqual(notebook.user, self.user)
        self.assertFalse(notebook.is_default)
    
    def test_notebook_with_custom_icon_color(self):
        """Test: crear notebook con color e ícono personalizados"""
        notebook = Notebook.objects.create(
            user=self.user,
            name='Física',
            slug='fisica',
            color='#FF5733',
            icon='🔬'
        )
        self.assertEqual(notebook.color, '#FF5733')
        self.assertEqual(notebook.icon, '🔬')
    
    def test_unique_slug_per_user(self):
        """Test: slug debe ser único por usuario"""
        Notebook.objects.create(
            user=self.user,
            name='Notebook 1',
            slug='unique-slug'
        )
        # Intentar crear otro con mismo slug y mismo user debe fallar
        with self.assertRaises(Exception):  # IntegrityError
            Notebook.objects.create(
                user=self.user,
                name='Notebook 2',
                slug='unique-slug'
            )
    
    def test_different_users_same_slug(self):
        """Test: diferentes usuarios pueden tener mismo slug"""
        user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        nb1 = Notebook.objects.create(
            user=self.user,
            name='Notebook 1',
            slug='shared-slug'
        )
        nb2 = Notebook.objects.create(
            user=user2,
            name='Notebook 2',
            slug='shared-slug'
        )
        self.assertNotEqual(nb1.user, nb2.user)
        self.assertEqual(nb1.slug, nb2.slug)
    
    def test_notebook_str_representation(self):
        """Test: representación en string del notebook"""
        notebook = Notebook.objects.create(
            user=self.user,
            name='Química',
            slug='quimica'
        )
        self.assertIn('Química', str(notebook))
        self.assertIn(self.user.username, str(notebook))
    
    def test_notebook_timestamps(self):
        """Test: verificar timestamps automáticos"""
        notebook = Notebook.objects.create(
            user=self.user,
            name='Timestamp Test',
            slug='timestamp-test'
        )
        self.assertIsNotNone(notebook.created_at)
        self.assertIsNotNone(notebook.updated_at)
        # Los timestamps pueden tener pequeñas diferencias de microsegundos
        # Verificar que están muy cercanos (menos de 1 segundo de diferencia)
        time_diff = abs((notebook.updated_at - notebook.created_at).total_seconds())
        self.assertLess(time_diff, 1)
    
    def test_notebook_update_timestamp(self):
        """Test: updated_at debe cambiar al actualizar"""
        notebook = Notebook.objects.create(
            user=self.user,
            name='Original Name',
            slug='test-slug'
        )
        original_updated = notebook.updated_at
        
        # Esperar un pequeño tiempo y actualizar
        import time
        time.sleep(0.1)
        
        notebook.name = 'Updated Name'
        notebook.save()
        
        self.assertGreater(notebook.updated_at, original_updated)
    
    def test_default_values(self):
        """Test: valores por defecto"""
        notebook = Notebook.objects.create(
            user=self.user,
            name='Defaults Test',
            slug='defaults'
        )
        self.assertEqual(notebook.color, '#1976d2')
        self.assertEqual(notebook.icon, '📚')
        self.assertFalse(notebook.is_default)
    
    def test_notebook_filtering_by_user(self):
        """Test: filtrar notebooks por usuario"""
        user2 = User.objects.create_user(
            username='testuser3',
            email='test3@example.com',
            password='testpass123'
        )
        Notebook.objects.create(user=self.user, name='NB1', slug='nb1')
        Notebook.objects.create(user=self.user, name='NB2', slug='nb2')
        Notebook.objects.create(user=user2, name='NB3', slug='nb3')
        
        user1_notebooks = Notebook.objects.filter(user=self.user)
        self.assertEqual(user1_notebooks.count(), 2)
        
        user2_notebooks = Notebook.objects.filter(user=user2)
        self.assertEqual(user2_notebooks.count(), 1)
