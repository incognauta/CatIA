"""
Tests para FileProcessor (Fase 4B)
"""
from io import BytesIO
from django.test import TestCase
from apps.core.processors import FileProcessor, FileProcessorError, SUPPORTED_TYPES
from apps.core.llm_service import GroqService, LLMServiceError


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

