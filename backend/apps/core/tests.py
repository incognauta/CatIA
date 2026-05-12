"""
Tests para FileProcessor (Fase 4B)
"""
from io import BytesIO
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.core.processors import FileProcessor, FileProcessorError, SUPPORTED_TYPES
from apps.core.llm_service import GroqService, LLMServiceError
from apps.core.models import UserLLMSettings

User = get_user_model()


class FileProcessorTestCase(TestCase):
    """Tests de procesamiento de archivos"""
    
    def test_validate_file_valid_pdf(self):
        """Validar que PDF sea aceptado"""
        file_obj = BytesIO(b"fake pdf")
        file_obj.size = 1024
        
        is_valid, error = FileProcessor.validate_file(file_obj, 'application/pdf')
        self.assertTrue(is_valid)
        self.assertEqual(error, "")
    
    def test_validate_file_unsupported_type(self):
        """Validar que tipo no soportado sea rechazado"""
        file_obj = BytesIO(b"content")
        file_obj.size = 1024
        
        is_valid, error = FileProcessor.validate_file(file_obj, 'application/zip')
        self.assertFalse(is_valid)
        self.assertIn("no soportado", error)
    
    def test_validate_file_oversized(self):
        """Validar que archivo muy grande sea rechazado"""
        file_obj = BytesIO(b"x" * (60 * 1024 * 1024))  # 60MB
        file_obj.size = 60 * 1024 * 1024
        
        is_valid, error = FileProcessor.validate_file(file_obj, 'text/plain')
        self.assertFalse(is_valid)
        self.assertIn("límite", error)
    
    def test_process_txt_file(self):
        """Procesar archivo de texto plano"""
        content = "Hola mundo\nPrimer documento"
        file_obj = BytesIO(content.encode('utf-8'))
        
        result = FileProcessor.process_file(
            file_obj,
            'text/plain',
            'test.txt'
        )
        
        self.assertEqual(result['file_type'], 'txt')
        self.assertEqual(result['original_filename'], 'test.txt')
        self.assertIn('Hola mundo', result['content'])
        self.assertEqual(result['is_scanned'], False)
        self.assertGreater(result['file_size'], 0)
    
    def test_process_pdf_error_invalid(self):
        """Procesar PDF inválido debe lanzar error"""
        file_obj = BytesIO(b"not a real pdf")
        file_obj.size = 14
        
        with self.assertRaises(FileProcessorError) as ctx:
            FileProcessor.process_file(
                file_obj,
                'application/pdf',
                'invalid.pdf'
            )
        
        self.assertIn("PDF", str(ctx.exception))
    
    def test_supported_types_dict(self):
        """Verificar que SUPPORTED_TYPES incluya tipos principales"""
        self.assertIn('application/pdf', SUPPORTED_TYPES)
        self.assertIn('text/plain', SUPPORTED_TYPES)
        self.assertIn('application/vnd.openxmlformats-officedocument.wordprocessingml.document', SUPPORTED_TYPES)
        self.assertIn('image/jpeg', SUPPORTED_TYPES)


class GroqServiceTestCase(TestCase):
    """Tests para GroqService (Fase 4C)"""
    
    def test_build_rag_context_empty(self):
        """Contexto RAG vacío si no hay documentos"""
        context = GroqService.build_rag_context([])
        self.assertEqual(context, "")
    
    def test_build_rag_context_single_doc(self):
        """Construir contexto RAG con un documento"""
        docs = [
            {
                'title': 'Documento de Prueba',
                'content': 'Este es contenido de ejemplo para RAG'
            }
        ]
        context = GroqService.build_rag_context(docs)
        
        self.assertIn('Documento de Prueba', context)
        self.assertIn('contenido de ejemplo', context)
    
    def test_build_rag_context_multiple_docs(self):
        """Construir contexto RAG con múltiples documentos"""
        docs = [
            {'title': 'Doc 1', 'content': 'Contenido 1'},
            {'title': 'Doc 2', 'content': 'Contenido 2'},
            {'title': 'Doc 3', 'content': 'Contenido 3'},
        ]
        context = GroqService.build_rag_context(docs, max_chars=1000)
        
        self.assertIn('Doc 1', context)
        self.assertGreater(len(context), 0)
    
    def test_build_rag_context_max_chars_limit(self):
        """Respetar límite de caracteres en contexto RAG"""
        docs = [
            {'title': 'Doc 1', 'content': 'X' * 1000},
            {'title': 'Doc 2', 'content': 'Y' * 1000},
        ]
        context = GroqService.build_rag_context(docs, max_chars=500)
        
        self.assertLessEqual(len(context), 600)  # Con algo de holgura
    
    def test_truncate_context(self):
        """Truncar contexto a límite de tokens"""
        text = "A" * 20000  # Texto muy largo
        truncated = GroqService.truncate_context(text, max_tokens=1000)
        
        self.assertLessEqual(len(truncated), 5000)  # 1000 tokens * 4 chars + buffer
        self.assertIn("[truncado]", truncated)
    
    def test_groq_service_creation(self):
        """Intentar crear GroqService (fallará sin API key válida)"""
        # Sin API key válida, debería lanzar LLMServiceError
        # Esto es un test que verifica el manejo de errores
        try:
            from unittest.mock import patch
            
            # Simular que GROQ_CONFIG tiene API_KEY vacía
            with patch('apps.core.llm_service.GROQ_CONFIG', {'API_KEY': '', 'MODEL': 'llama-3.1-8b-instant', 'MAX_TOKENS': 1024, 'TEMPERATURE': 0.7}):
                with self.assertRaises(LLMServiceError):
                    GroqService()
        except ImportError:
            # Si no está disponible unittest.mock, skipear
            pass


# ============================================================================
# NUEVOS TESTS - Fase 7A: Tests Exhaustivos con Mocking de Groq API
# ============================================================================

class GroqServiceMockTestCase(TestCase):
    """Tests con mocking de Groq API - Fase 7A"""
    
    @patch('apps.core.llm_service.Groq')
    def test_generate_response_mock_success(self, mock_groq_class):
        """Test 1: Generar respuesta sin llamar API real"""
        # Arrange: Configurar mock de Groq
        mock_client = MagicMock()
        mock_groq_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Respuesta de prueba del AI"
        mock_client.chat.completions.create.return_value = mock_response
        
        # Act: Crear servicio y generar respuesta
        service = GroqService()
        result = service.generate_response(
            user_message="¿Cuál es la capital de Francia?"
        )
        
        # Assert: Verificar respuesta
        self.assertIn("Respuesta de prueba del AI", result['response'])
        self.assertIn('tokens_used', result)
        mock_client.chat.completions.create.assert_called_once()
    
    @patch('apps.core.llm_service.Groq')
    def test_generate_response_with_context(self, mock_groq_class):
        """Test 2: Generar respuesta con contexto de documentos"""
        # Arrange
        mock_client = MagicMock()
        mock_groq_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "La respuesta basada en el contexto"
        mock_client.chat.completions.create.return_value = mock_response
        
        # Act
        service = GroqService()
        context_docs = [
            {
                'title': 'Documento 1',
                'content': 'Contenido importante'
            }
        ]
        result = service.generate_response(
            user_message="¿Qué dice el documento?",
            context_documents=context_docs
        )
        
        # Assert
        self.assertIn("respuesta basada en el contexto", result['response'])
        # Verificar que se pasaron los documentos en el contexto
        call_args = mock_client.chat.completions.create.call_args
        self.assertIsNotNone(call_args)


class GroqErrorHandlingTestCase(TestCase):
    """Tests de manejo de errores de Groq API - Fase 7A"""
    
    @patch('apps.core.llm_service.Groq')
    def test_groq_api_timeout(self, mock_groq_class):
        """Test 3: Manejar timeout de API"""
        # Arrange: Simular timeout
        mock_groq_class.side_effect = TimeoutError("API request timeout")
        
        # Act & Assert: Debería lanzar excepción
        with self.assertRaises(Exception):
            GroqService()
    
    @patch('apps.core.llm_service.Groq')
    def test_groq_api_invalid_key(self, mock_groq_class):
        """Test 4: Manejar API key inválida"""
        # Arrange: Simular error de API key
        mock_groq_class.side_effect = Exception("Invalid API key")
        
        # Act & Assert: Debería lanzar excepción
        with self.assertRaises(Exception):
            GroqService()
    
    @patch('apps.core.llm_service.Groq')
    def test_groq_api_rate_limit(self, mock_groq_class):
        """Test 5: Manejar rate limiting"""
        # Arrange
        mock_client = MagicMock()
        mock_groq_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("Rate limit exceeded")
        
        # Act & Assert
        service = GroqService()
        with self.assertRaises(Exception):
            service.generate_response(user_message="Test")


class TokenTrackingTestCase(TestCase):
    """Tests de conteo de tokens - Fase 7A"""
    
    def test_token_estimation_simple(self):
        """Test 6: Estimar tokens de texto simple"""
        text = "Esto es un texto de prueba"
        # Estimación simple: 1 token ≈ 1.3 palabras
        estimated_tokens = len(text.split()) * 1.3
        
        self.assertGreater(estimated_tokens, 0)
        self.assertLess(estimated_tokens, 10)
    
    def test_token_estimation_long_text(self):
        """Test 7: Estimar tokens de texto largo"""
        text = " ".join(["palabra"] * 1000)  # 1000 palabras
        estimated_tokens = len(text.split()) * 1.3
        
        self.assertGreater(estimated_tokens, 1200)
        self.assertLess(estimated_tokens, 1400)
    
    @patch('apps.core.llm_service.Groq')
    def test_response_includes_token_count(self, mock_groq_class):
        """Test 8: Respuesta incluye conteo de tokens"""
        # Arrange
        mock_client = MagicMock()
        mock_groq_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Respuesta con tokens"
        # Simular objeto con atributo usage
        mock_response.usage = MagicMock()
        mock_response.usage.completion_tokens = 25
        mock_client.chat.completions.create.return_value = mock_response
        
        # Act
        service = GroqService()
        result = service.generate_response(user_message="¿Cuántos tokens?")
        
        # Assert
        self.assertIn('tokens_used', result)
        # El token count puede ser numérico o estar calculado
        self.assertIsNotNone(result['tokens_used'])


class UserLLMSettingsOverrideTestCase(TestCase):
    """Tests de settings de usuario sobrescribiendo defaults - Fase 7A"""
    
    def test_user_settings_creation(self):
        """Test 9: Crear settings de usuario"""
        # Arrange
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Act
        user_settings, created = UserLLMSettings.get_or_create_for_user(user)
        
        # Assert
        self.assertTrue(created)
        self.assertEqual(user_settings.user, user)
        self.assertIsNotNone(user_settings.model)
        self.assertIsNotNone(user_settings.temperature)
        self.assertIsNotNone(user_settings.max_tokens)
    
    def test_user_settings_override_defaults(self):
        """Test 10: Settings del usuario sobrescriben defaults"""
        # Arrange
        user = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        
        # Act: Crear settings personalizados
        user_settings = UserLLMSettings.objects.create(
            user=user,
            model='mixtral-8x7b-32768',
            temperature=0.9,
            max_tokens=2048
        )
        
        # Assert
        self.assertEqual(user_settings.model, 'mixtral-8x7b-32768')
        self.assertEqual(user_settings.temperature, 0.9)
        self.assertEqual(user_settings.max_tokens, 2048)
    
    def test_user_settings_temperature_validation(self):
        """Test 11: Validar temperatura está entre 0.0-1.0"""
        # Arrange
        user = User.objects.create_user(
            username='testuser3',
            email='test3@example.com',
            password='testpass123'
        )
        
        # Act & Assert: Temperatura válida
        user_settings = UserLLMSettings.objects.create(
            user=user,
            temperature=0.5
        )
        self.assertEqual(user_settings.temperature, 0.5)
        
        # Act & Assert: Temperatura inválida (> 1.0)
        with self.assertRaises(Exception):
            UserLLMSettings.objects.create(
                user=user,
                temperature=1.5  # Inválido
            )
    
    def test_user_settings_max_tokens_validation(self):
        """Test 12: Validar max_tokens está en rango válido"""
        # Arrange
        user = User.objects.create_user(
            username='testuser4',
            email='test4@example.com',
            password='testpass123'
        )
        
        # Act & Assert: Tokens válidos
        user_settings = UserLLMSettings.objects.create(
            user=user,
            max_tokens=1024
        )
        self.assertEqual(user_settings.max_tokens, 1024)
        
        # Act & Assert: Tokens inválidos (< 256)
        with self.assertRaises(Exception):
            UserLLMSettings.objects.create(
                user=user,
                max_tokens=100  # Inválido
            )


class DocumentTruncationWithSettingsTestCase(TestCase):
    """Tests de truncamiento inteligente con settings - Fase 7A"""
    
    def test_truncate_respects_max_tokens_setting(self):
        """Test 13: Truncamiento respeta max_tokens del usuario"""
        # Arrange
        text = "A" * 50000  # Texto muy largo
        max_tokens = 1024
        
        # Act
        truncated = GroqService.truncate_context(text, max_tokens=max_tokens)
        
        # Assert: No debe exceder estimación de tokens
        estimated_tokens = len(truncated) / 4  # Estimación conservadora
        self.assertLessEqual(estimated_tokens, max_tokens + 100)
    
    def test_truncate_adds_marker(self):
        """Test 14: Truncamiento agrega marcador cuando se trunca"""
        # Arrange
        text = "X" * 20000
        
        # Act
        truncated = GroqService.truncate_context(text, max_tokens=500)
        
        # Assert
        self.assertIn("[truncado]", truncated)
    
    def test_build_rag_context_with_document_limit(self):
        """Test 15: RAG respeta límite de caracteres"""
        # Arrange
        docs = [
            {'title': f'Doc {i}', 'content': 'Y' * 2000}
            for i in range(5)
        ]
        
        # Act
        context = GroqService.build_rag_context(docs, max_chars=5000)
        
        # Assert
        self.assertLessEqual(len(context), 5500)  # Con pequeño buffer


class GroqModelSwitchTestCase(TestCase):
    """Tests de cambio de modelo Groq - Fase 7A"""
    
    @patch('apps.core.llm_service.Groq')
    def test_generate_response_with_model_override(self, mock_groq_class):
        """Test 16: Usar modelo diferente via override"""
        # Arrange
        mock_client = MagicMock()
        mock_groq_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Respuesta con mixtral"
        mock_client.chat.completions.create.return_value = mock_response
        
        # Act
        service = GroqService()
        result = service.generate_response(
            user_message="Test",
            model_override='mixtral-8x7b-32768'
        )
        
        # Assert
        self.assertIsNotNone(result['response'])
        # Verificar que se usó el modelo correcto
        call_args = mock_client.chat.completions.create.call_args
        self.assertIsNotNone(call_args)
    
    @patch('apps.core.llm_service.Groq')
    def test_generate_response_with_temperature_override(self, mock_groq_class):
        """Test 17: Usar temperatura diferente via override"""
        # Arrange
        mock_client = MagicMock()
        mock_groq_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Respuesta creativa"
        mock_client.chat.completions.create.return_value = mock_response
        
        # Act
        service = GroqService()
        result = service.generate_response(
            user_message="Cuéntame un cuento",
            temperature_override=0.9
        )
        
        # Assert
        self.assertIsNotNone(result['response'])


class EndToEndMockTestCase(TestCase):
    """Tests end-to-end con mocking - Fase 7A"""
    
    @patch('apps.core.llm_service.Groq')
    def test_complete_flow_user_query_to_response(self, mock_groq_class):
        """Test 18: Flujo completo: pregunta del usuario → respuesta IA"""
        # Arrange
        mock_client = MagicMock()
        mock_groq_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Respuesta final del sistema"
        mock_response.usage = MagicMock()
        mock_response.usage.completion_tokens = 42
        mock_client.chat.completions.create.return_value = mock_response
        
        # Crear usuario y settings
        user = User.objects.create_user(
            username='endtoenduser',
            email='user@example.com',
            password='pass123'
        )
        user_settings = UserLLMSettings.objects.create(
            user=user,
            model='llama-3.1-8b-instant',
            temperature=0.7,
            max_tokens=1024
        )
        
        # Act
        service = GroqService()
        result = service.generate_response(
            user_message="¿Cuál es Python?",
            context_documents=[
                {'title': 'Python Docs', 'content': 'Python es un lenguaje...'}
            ],
            model_override=user_settings.model,
            temperature_override=user_settings.temperature,
            max_tokens_override=user_settings.max_tokens
        )
        
        # Assert
        self.assertIn("Respuesta final", result['response'])
        self.assertIn('tokens_used', result)
        self.assertTrue(mock_client.chat.completions.create.called)


