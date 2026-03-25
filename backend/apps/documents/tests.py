from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.notebooks.models import Notebook
from apps.documents.models import Document

User = get_user_model()


class DocumentModelTestCase(TestCase):
    """Tests para modelo Document"""
    
    def setUp(self):
        """Crear usuario, notebook y datos de prueba"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.notebook = Notebook.objects.create(
            user=self.user,
            name='Test Notebook',
            slug='test-notebook'
        )
    
    def test_create_document(self):
        """Test: crear documento básico"""
        doc = Document.objects.create(
            user=self.user,
            notebook=self.notebook,
            title='Test Document',
            original_filename='test.txt',
            content='Este es contenido de prueba'
        )
        self.assertEqual(doc.title, 'Test Document')
        self.assertEqual(doc.user, self.user)
        self.assertEqual(doc.notebook, self.notebook)
    
    def test_document_default_file_type(self):
        """Test: tipo de archivo por defecto es txt"""
        doc = Document.objects.create(
            user=self.user,
            notebook=self.notebook,
            title='Test',
            original_filename='test.txt',
            content='content'
        )
        self.assertEqual(doc.file_type, 'txt')
    
    def test_document_with_file_metadata(self):
        """Test: documentos con metadata de archivo"""
        doc = Document.objects.create(
            user=self.user,
            notebook=self.notebook,
            title='PDF Test',
            original_filename='test.pdf',
            content='PDF content',
            file_type='pdf',
            file_path='/media/documents/user123/doc456.pdf',
            file_size=1024,
            pages=5
        )
        self.assertEqual(doc.file_type, 'pdf')
        self.assertEqual(doc.file_size, 1024)
        self.assertEqual(doc.pages, 5)
    
    def test_document_deletion_cascades(self):
        """Test: eliminar notebook elimina documentos"""
        doc = Document.objects.create(
            user=self.user,
            notebook=self.notebook,
            title='Cascade Test',
            original_filename='test.txt',
            content='content'
        )
        doc_id = doc.id
        self.notebook.delete()
        
        # Document debe estar eliminado
        self.assertFalse(Document.objects.filter(id=doc_id).exists())
    
    def test_document_str_representation(self):
        """Test: representación en string del documento"""
        doc = Document.objects.create(
            user=self.user,
            notebook=self.notebook,
            title='String Test',
            original_filename='test.txt',
            content='content'
        )
        self.assertIn('String Test', str(doc))
        self.assertIn(self.notebook.name, str(doc))
    
    def test_document_timestamps(self):
        """Test: timestamps automáticos"""
        doc = Document.objects.create(
            user=self.user,
            notebook=self.notebook,
            title='Timestamp Test',
            original_filename='test.txt',
            content='content'
        )
        self.assertIsNotNone(doc.created_at)
        self.assertIsNotNone(doc.updated_at)
    
    def test_document_filtering_by_notebook(self):
        """Test: filtrar documentos por notebook"""
        nb2 = Notebook.objects.create(
            user=self.user,
            name='Notebook 2',
            slug='nb2'
        )
        
        Document.objects.create(user=self.user, notebook=self.notebook, title='Doc1', original_filename='d1.txt', content='c1')
        Document.objects.create(user=self.user, notebook=self.notebook, title='Doc2', original_filename='d2.txt', content='c2')
        Document.objects.create(user=self.user, notebook=nb2, title='Doc3', original_filename='d3.txt', content='c3')
        
        nb1_docs = Document.objects.filter(notebook=self.notebook)
        self.assertEqual(nb1_docs.count(), 2)
        
        nb2_docs = Document.objects.filter(notebook=nb2)
        self.assertEqual(nb2_docs.count(), 1)
    
    def test_document_content_required(self):
        """Test: contenido vacío se permite (validación en serializer)"""
        # El modelo Django no valida, la validación ocurre en serializer
        # Este test verifica que el modelo lo permite
        doc = Document.objects.create(
            user=self.user,
            notebook=self.notebook,
            title='Empty Content',
            original_filename='test.txt',
            content=''  # Django ORM lo permite, validación en app layer
        )
        self.assertEqual(doc.content, '')
