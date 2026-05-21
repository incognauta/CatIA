import logging

from django.db.models import Q
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import ChatMessage
from .serializers import ChatMessageSerializer, ChatMessageCreateSerializer, ChatHistorySerializer
from apps.core.services.chat_service import DjangoChatService
from apps.core.llm_service import LLMServiceError

logger = logging.getLogger(__name__)

# Instancia única del servicio de chat
_chat_service = None

def get_chat_service():
    """Obtener instancia del servicio de chat (singleton)"""
    global _chat_service
    if _chat_service is None:
        _chat_service = DjangoChatService()
    return _chat_service


class ChatMessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet para ChatMessage - CRUD de mensajes
    Endpoints:
    - GET /api/v1/chat/ - Listar mis mensajes
    - POST /api/v1/chat/ - Crear mensaje
    - GET /api/v1/chat/{id}/ - Ver detalle
    - DELETE /api/v1/chat/{id}/ - Eliminar mensaje
    - POST /api/v1/chat/ask_ai/ - Preguntar a Groq con RAG
    """
    
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['notebook', 'role']
    ordering = ['created_at']
    
    def get_serializer_class(self):
        """Usar diferentes serializers según la acción"""
        if self.action == 'create':
            return ChatMessageCreateSerializer
        return ChatMessageSerializer
    
    def get_queryset(self):
        """Solo devolver mensajes del usuario autenticado"""
        return ChatMessage.objects.filter(user=self.request.user).order_by('created_at')
    
    def perform_create(self, serializer):
        """Asignar usuario automáticamente al crear"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """
        Endpoint: GET /api/v1/chat/history/?notebook={notebook_id}
        Devolver historial de chat para un notebook
        """
        notebook_id = request.query_params.get('notebook')
        
        if not notebook_id:
            return Response(
                {'error': 'Parámetro notebook es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        messages = ChatMessage.objects.filter(
            user=request.user,
            notebook_id=notebook_id
        ).order_by('created_at')
        
        serializer = ChatHistorySerializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['delete'])
    def clear_history(self, request):
        """
        Endpoint: DELETE /api/v1/chat/clear_history/?notebook={notebook_id}
        Borrar historial de chat de un notebook
        """
        notebook_id = request.query_params.get('notebook')
        
        if not notebook_id:
            return Response(
                {'error': 'Parámetro notebook es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        deleted_count, _ = ChatMessage.objects.filter(
            user=request.user,
            notebook_id=notebook_id
        ).delete()
        
        return Response({
            'deleted': deleted_count,
            'message': f'Se eliminaron {deleted_count} mensajes'
        })
    
    @action(detail=False, methods=['post'])
    def ask_ai(self, request):
        """
        Endpoint: POST /api/v1/chat/ask_ai/
        Preguntar a IA con contexto RAG de documentos del notebook
        
        Expected body:
        {
            "notebook": "uuid-del-notebook",
            "message": "Tu pregunta aqui",
            "system_prompt": "Sistema prompt opcional",
            "language": "es" or "en"  (optional, default: "es")
        }
        """
        
        # Validar inputs
        notebook_id = request.data.get('notebook')
        message = request.data.get('message', '').strip()
        system_prompt = request.data.get('system_prompt')
        language = request.data.get('language', 'es')
        
        if not notebook_id:
            return Response(
                {'error': 'Parámetro notebook es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not message:
            return Response(
                {'error': 'Mensaje no puede estar vacío'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar que language sea válido
        if language not in ['es', 'en']:
            language = 'es'
        
        # Usar servicio de chat para procesar la pregunta
        try:
            chat_service = get_chat_service()
            result = chat_service.process_query(
                user_id=str(request.user.id),
                notebook_id=str(notebook_id),
                message=message,
                system_prompt=system_prompt,
                language=language,
            )
            
            return Response(result, status=status.HTTP_201_CREATED)
        
        except ValueError as e:
            logger.warning(f"Validación error: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST if "vacío" not in str(e) else status.HTTP_404_NOT_FOUND
            )
        
        except LLMServiceError as e:
            logger.error(f"LLM error: {e}")
            return Response(
                {'error': f'Error en servicio de IA: {str(e)}'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            return Response(
                {'error': 'Error interno del servidor'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
