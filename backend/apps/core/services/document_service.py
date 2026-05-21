"""
Implementación de DocumentUploadService - Procesamiento de archivos

Encapsula toda la lógica de carga, validación y procesamiento de documentos.
Soporta múltiples formatos: PDF, DOCX, TXT, Imágenes.
"""

import logging
from typing import Dict, Optional

from .base import DocumentUploadServiceBase
from apps.core.processors import FileProcessor, FileProcessorError

logger = logging.getLogger(__name__)


class DjangoDocumentUploadService(DocumentUploadServiceBase):
    """
    Implementación de DocumentUploadService usando Django models y FileProcessor
    
    Orquesta:
    1. Validación del archivo
    2. Procesamiento (OCR, text extraction, etc.)
    3. Obtención/creación del notebook
    4. Persistencia en base de datos
    """
    
    def process_upload(
        self,
        uploaded_file,
        notebook_id: Optional[str],
        user_id: str,
        title: Optional[str] = None,
    ) -> Dict:
        """
        Procesar archivo cargado: validación + procesamiento + persistencia
        
        Flujo:
        1. Validar archivo
        2. Obtener/crear notebook (default si no lo proporciona)
        3. Procesar archivo con FileProcessor (OCR, extracción, etc.)
        4. Crear documento en DB
        5. Retornar documento procesado
        
        Args:
            uploaded_file: Archivo cargado desde request.FILES
            notebook_id: ID del notebook (usa default si es None)
            user_id: ID del usuario
            title: Título del documento (usa filename si no lo proporciona)
        
        Returns:
            Dict con documento {'id', 'title', 'content', 'file_size', ...}
        
        Raises:
            ValueError: Si archivo no es válido
            FileProcessorError: Si falla el procesamiento
        """
        from apps.users.models import User
        from apps.notebooks.models import Notebook
        from apps.documents.models import Document
        from apps.documents.serializers import DocumentSerializer
        
        # 1. Validar archivo
        is_valid, error_msg = self.validate_file(uploaded_file)
        if not is_valid:
            raise ValueError(f"Archivo inválido: {error_msg}")
        
        # 2. Obtener usuario
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValueError("Usuario no encontrado")
        
        # 3. Obtener o crear notebook
        if notebook_id:
            try:
                notebook = Notebook.objects.get(id=notebook_id, user=user)
            except Notebook.DoesNotExist:
                raise ValueError("Notebook no encontrado o no pertenece al usuario")
        else:
            # Usar primer notebook del usuario, o crear uno default
            notebook = Notebook.objects.filter(user=user).first()
            if not notebook:
                # Si el usuario no tiene notebooks, crear uno por defecto
                notebook = Notebook.objects.create(
                    user=user,
                    name='Mi Notebook',
                    slug='mi-notebook',
                    is_default=True,
                    description='Notebook por defecto'
                )
                logger.info(f"Notebook creado por defecto para usuario {user.id}: {notebook.id}")
        
        # 4. Procesar archivo
        try:
            content_type = uploaded_file.content_type
            file_data = FileProcessor.process_file(
                uploaded_file,
                content_type,
                uploaded_file.name
            )
            
            logger.info(
                f"Archivo procesado: {uploaded_file.name} "
                f"({file_data['file_type']}, {file_data['file_size']} bytes)"
            )
        
        except FileProcessorError as e:
            logger.error(f"Error procesando archivo: {e}")
            raise FileProcessorError(f"Error procesando archivo: {str(e)}")
        except Exception as e:
            logger.error(f"Error inesperado procesando archivo: {e}")
            raise FileProcessorError("Error interno al procesar archivo")
        
        # 5. Crear documento en DB
        document_title = title or uploaded_file.name
        document = Document.objects.create(
            user=user,
            notebook=notebook,
            title=document_title,
            original_filename=file_data['original_filename'],
            file_type=file_data['file_type'],
            file_size=file_data['file_size'],
            pages=file_data.get('pages', 1),
            content=file_data['content'],
            content_markdown=file_data.get('content_markdown', ''),
        )
        
        logger.info(f"Documento creado: {document.id} - {document.title}")
        
        # 6. Generar chunks + embeddings para búsqueda semántica
        try:
            self._create_embeddings(document)
        except Exception as e:
            logger.warning(f"Error generando embeddings (no crítico): {e}")
        
        # 7. Retornar documento serializado
        serializer = DocumentSerializer(document)
        return serializer.data
    
    def _create_embeddings(self, document):
        """
        Dividir documento en chunks y generar embeddings.
        """
        from apps.documents.models import DocumentChunk
        from .rag_semantic_service import SemanticRAGService
        from .embedding_service import get_embedding_service

        content = document.content or ''
        if not content.strip():
            return

        rag = SemanticRAGService()
        emb = get_embedding_service()

        chunks = rag._split_text(content)
        if not chunks:
            return

        texts_to_embed = []
        chunk_objs = []

        for i, chunk_text in enumerate(chunks):
            if not chunk_text.strip():
                continue
            chunk = DocumentChunk(
                document=document,
                chunk_index=i,
                content=chunk_text,
            )
            chunk_objs.append(chunk)
            texts_to_embed.append(chunk_text)

        if not chunk_objs:
            return

        # Generar embeddings en batch
        vectors = emb.encode_batch(texts_to_embed)

        # Asignar vectores
        for chunk, vector in zip(chunk_objs, vectors):
            chunk.embedding = vector

        # Guardar en DB
        DocumentChunk.objects.bulk_create(chunk_objs)
        logger.info(
            f"Embeddings generados: {len(chunk_objs)} chunks "
            f"para documento {document.id}"
        )
    
    def validate_file(self, uploaded_file) -> tuple[bool, str]:
        """
        Validar que el archivo sea soportado
        
        Verifica:
        - Que exista el archivo
        - Que el tipo MIME sea soportado
        - Que el tamaño esté dentro de límites
        
        Args:
            uploaded_file: Archivo a validar
        
        Returns:
            Tupla (es_válido, mensaje_error)
        """
        from django.conf import settings
        
        # Validar que exista
        if not uploaded_file:
            return False, "Archivo no encontrado"
        
        # Validar tamaño máximo (configuración: 50MB por defecto)
        max_size = getattr(settings, 'MAX_UPLOAD_SIZE', 50 * 1024 * 1024)
        if uploaded_file.size > max_size:
            return False, f"Archivo excede tamaño máximo ({max_size} bytes)"
        
        # Validar tipo MIME
        supported_types = {
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain',
            'image/jpeg',
            'image/png',
            'image/gif',
            'image/webp',
        }
        
        if uploaded_file.content_type not in supported_types:
            return False, f"Tipo de archivo no soportado: {uploaded_file.content_type}"
        
        logger.info(f"Archivo validado: {uploaded_file.name} ({uploaded_file.content_type})")
        return True, ""
