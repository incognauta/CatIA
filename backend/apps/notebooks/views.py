from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Notebook
from .serializers import NotebookSerializer, NotebookCreateUpdateSerializer
from apps.core.services.notebook_service import DjangoNotebookService

# Instancia única del servicio de notebooks
_notebook_service = None

def get_notebook_service():
    """Obtener instancia del servicio de notebooks (singleton)"""
    global _notebook_service
    if _notebook_service is None:
        _notebook_service = DjangoNotebookService()
    return _notebook_service


class NotebookViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Notebook - CRUD completo
    Endpoints:
    - GET /api/v1/notebooks/ - Listar mis notebooks
    - POST /api/v1/notebooks/ - Crear notebook
    - GET /api/v1/notebooks/{id}/ - Ver detalles
    - PUT /api/v1/notebooks/{id}/ - Actualizar
    - DELETE /api/v1/notebooks/{id}/ - Eliminar
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """Usar diferentes serializers según la acción"""
        if self.action in ['create', 'update', 'partial_update']:
            return NotebookCreateUpdateSerializer
        return NotebookSerializer
    
    def get_queryset(self):
        """Solo devolver notebooks del usuario autenticado"""
        return Notebook.objects.filter(user=self.request.user).order_by('-created_at')
    
    def perform_create(self, serializer):
        """Asignar usuario automáticamente al crear"""
        serializer.save(user=self.request.user)
    
    def perform_update(self, serializer):
        """Asignar usuario al actualizar"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def documents(self, request, pk=None):
        """
        Endpoint: GET /api/v1/notebooks/{id}/documents/
        Devolver documentos del notebook
        """
        notebook = self.get_object()
        documents = notebook.documents.all()
        from apps.documents.serializers import DocumentListSerializer
        serializer = DocumentListSerializer(documents, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def chat_history(self, request, pk=None):
        """
        Endpoint: GET /api/v1/notebooks/{id}/chat_history/
        Devolver historial de chat del notebook
        """
        notebook = self.get_object()
        messages = notebook.chat_messages.all().order_by('created_at')[:50]  # Últimos 50
        from apps.chat.serializers import ChatHistorySerializer
        serializer = ChatHistorySerializer(messages, many=True)
        return Response(serializer.data)
