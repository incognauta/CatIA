from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Document
from .serializers import DocumentSerializer, DocumentCreateSerializer, DocumentListSerializer
from apps.core.services.document_service import DjangoDocumentUploadService
import logging

logger = logging.getLogger(__name__)

# Instancia única del servicio de carga de documentos
_document_service = None

def get_document_service():
    """Obtener instancia del servicio de documentos (singleton)"""
    global _document_service
    if _document_service is None:
        _document_service = DjangoDocumentUploadService()
    return _document_service


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
        notebook_id = request.data.get('notebook')
        title = request.data.get('title')
        
        # Usar servicio de documentos para procesar la carga
        try:
            document_service = get_document_service()
            document_data = document_service.process_upload(
                uploaded_file=uploaded_file,
                notebook_id=notebook_id,
                user_id=str(request.user.id),
                title=title,
            )
            
            return Response(document_data, status=status.HTTP_201_CREATED)
        
        except ValueError as e:
            logger.warning(f"Validación error: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST if "no encontrado" not in str(e) else status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error procesando archivo: {e}", exc_info=True)
            return Response(
                {'error': 'Error interno al procesar archivo'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
