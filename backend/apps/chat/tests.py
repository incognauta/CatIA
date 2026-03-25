from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.notebooks.models import Notebook
from apps.documents.models import Document
from apps.chat.models import ChatMessage

User = get_user_model()


class ChatMessageModelTestCase(TestCase):
    """Tests para modelo ChatMessage"""
    
    def setUp(self):
        """Crear usuario, notebook, documento y datos de prueba"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.notebook = Notebook.objects.create(
            user=self.user,
            name='Chat Test Notebook',
            slug='chat-test'
        )
        self.document = Document.objects.create(
            user=self.user,
            notebook=self.notebook,
            title='Test Doc',
            original_filename='test.txt',
            content='Test content'
        )
    
    def test_create_user_message(self):
        """Test: crear mensaje de usuario"""
        msg = ChatMessage.objects.create(
            user=self.user,
            notebook=self.notebook,
            role='user',
            content='¿Cuál es la capitale de Francia?'
        )
        self.assertEqual(msg.role, 'user')
        self.assertEqual(msg.user, self.user)
        self.assertIsNone(msg.document)
    
    def test_create_assistant_message(self):
        """Test: crear mensaje de asistente"""
        msg = ChatMessage.objects.create(
            user=self.user,
            notebook=self.notebook,
            role='assistant',
            content='La capital de Francia es París.',
            tokens_used=15
        )
        self.assertEqual(msg.role, 'assistant')
        self.assertEqual(msg.tokens_used, 15)
    
    def test_message_with_document_context(self):
        """Test: mensaje asociado a documento"""
        msg = ChatMessage.objects.create(
            user=self.user,
            notebook=self.notebook,
            document=self.document,
            role='user',
            content='¿De qué trata este documento?'
        )
        self.assertEqual(msg.document, self.document)
    
    def test_message_without_document_context(self):
        """Test: mensaje sin documento asociado"""
        msg = ChatMessage.objects.create(
            user=self.user,
            notebook=self.notebook,
            role='user',
            content='Pregunta general'
        )
        self.assertIsNone(msg.document)
    
    def test_document_deletion_nullifies_message(self):
        """Test: eliminar documento pone NULL en mensaje"""
        msg = ChatMessage.objects.create(
            user=self.user,
            notebook=self.notebook,
            document=self.document,
            role='user',
            content='test'
        )
        self.document.delete()
        msg.refresh_from_db()
        self.assertIsNone(msg.document)
    
    def test_notebook_deletion_cascades_messages(self):
        """Test: eliminar notebook elimina mensajes"""
        msg = ChatMessage.objects.create(
            user=self.user,
            notebook=self.notebook,
            role='user',
            content='test'
        )
        msg_id = msg.id
        self.notebook.delete()
        
        self.assertFalse(ChatMessage.objects.filter(id=msg_id).exists())
    
    def test_message_str_representation(self):
        """Test: representación en string del mensaje"""
        msg = ChatMessage.objects.create(
            user=self.user,
            notebook=self.notebook,
            role='user',
            content='test'
        )
        str_repr = str(msg)
        self.assertIn('user', str_repr)
        self.assertIn(self.user.username, str_repr)
    
    def test_message_timestamps(self):
        """Test: timestamps automáticos"""
        msg = ChatMessage.objects.create(
            user=self.user,
            notebook=self.notebook,
            role='user',
            content='test'
        )
        self.assertIsNotNone(msg.created_at)
    
    def test_chat_history_ordering(self):
        """Test: mensajes ordenados por creación"""
        msg1 = ChatMessage.objects.create(user=self.user, notebook=self.notebook, role='user', content='First')
        msg2 = ChatMessage.objects.create(user=self.user, notebook=self.notebook, role='assistant', content='Second')
        msg3 = ChatMessage.objects.create(user=self.user, notebook=self.notebook, role='user', content='Third')
        
        messages = list(ChatMessage.objects.all())
        self.assertEqual(messages[0].id, msg1.id)
        self.assertEqual(messages[1].id, msg2.id)
        self.assertEqual(messages[2].id, msg3.id)
    
    def test_tokens_default_zero(self):
        """Test: tokens por defecto en cero"""
        msg = ChatMessage.objects.create(
            user=self.user,
            notebook=self.notebook,
            role='user',
            content='test'
        )
        self.assertEqual(msg.tokens_used, 0)
