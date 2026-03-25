from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Document
from .serializers import DocumentSerializer, DocumentCreateSerializer, DocumentListSerializer
from apps.core.processors import FileProcessor, FileProcessorError
import logging

logger = logging.getLogger(__name__)


class DocumentViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Document - CRUD completo
    Endpoints:
    - GET /api/v1/documents/ - Listar mis documentos
    - POST /api/v1/documents/ - Crear documento
    - GET /api/v1/documents/{id}/ - Ver detalles
    - PUT /api/v1/documents/{id}/ - Actualizar
    - DELETE /api/v1/documents/{id}/ - Eliminar
    - POST /api/v1/documents/upload/ - Cargar archivo con OCR
    """
    
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['notebook']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Usar diferentes serializers según la acción"""
        if self.action == 'create':
            return DocumentCreateSerializer
        elif self.action == 'list':
            return DocumentListSerializer
        return DocumentSerializer
    
    def get_queryset(self):
        """Solo devolver documentos del usuario autenticado"""
        return Document.objects.filter(user=self.request.user).order_by('-created_at')
    
    def perform_create(self, serializer):
        """Asignar usuario automáticamente al crear"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def content(self, request, pk=None):
        """
        Endpoint: GET /api/v1/documents/{id}/content/
        Devolver contenido completo del documento
        """
        document = self.get_object()
        return Response({
            'id': str(document.id),
            'title': document.title,
            'content': document.content,
            'content_markdown': document.content_markdown,
            'file_type': document.file_type,
        })
    
    @action(detail=False, methods=['post'], parser_classes=(MultiPartParser, FormParser))
    def upload(self, request):
        """
        Endpoint: POST /api/v1/documents/upload/
        Cargar y procesar archivo (PDF, DOCX, TXT, Imágenes)
        
        Expected params:
        - file: archivo a cargar (multipart/form-data)
        - notebook: UUID del notebook (optional, si no lo proporciona usa el default)
        - title: título del documento (optional, usa filename si no lo proporciona)
        """
        
        # Validar que exista archivo
        if 'file' not in request.FILES:
            return Response(
                {'error': 'Campo file es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        uploaded_file = request.FILES['file']
        
        # Obtener notebook (default o especificado)
        notebook_id = request.data.get('notebook')
        if notebook_id:
            from apps.notebooks.models import Notebook
            try:
                notebook = Notebook.objects.get(id=notebook_id, user=request.user)
            except Notebook.DoesNotExist:
                return Response(
                    {'error': 'Notebook no encontrado'},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            # Usar default notebook del usuario
            from apps.notebooks.models import Notebook
            notebook, _ = Notebook.objects.get_or_create(
                user=request.user,
                is_default=True,
                defaults={
                    'name': 'Sin clasificar',
                    'slug': 'sin-clasificar',
                }
            )
        
        # Procesar archivo
        try:
            content_type = uploaded_file.content_type
            file_data = FileProcessor.process_file(
                uploaded_file,
                content_type,
                uploaded_file.name
            )
        
        except FileProcessorError as e:
            logger.error(f"Error procesando archivo: {e}")
            return Response(
                {'error': f'Error procesando archivo: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            return Response(
                {'error': 'Error interno al procesar archivo'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Crear documento
        title = request.data.get('title', uploaded_file.name)
        document = Document.objects.create(
            user=request.user,
            notebook=notebook,
            title=title,
            original_filename=file_data['original_filename'],
            file_type=file_data['file_type'],
            file_size=file_data['file_size'],
            pages=file_data['pages'],
            content=file_data['content'],
            content_markdown=file_data['content_markdown'],
        )
        
        serializer = DocumentSerializer(document)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
