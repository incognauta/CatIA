import logging

from django.db.models import Q
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import ChatMessage
from .serializers import ChatMessageSerializer, ChatMessageCreateSerializer, ChatHistorySerializer
from apps.core.llm_service import get_groq_service, LLMServiceError

logger = logging.getLogger(__name__)


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
        Preguntar a Groq con contexto RAG de documentos del notebook
        
        Expected body:
        {
            "notebook": "uuid-del-notebook",
            "message": "Tu pregunta aqui",
            "system_prompt": "Sistema prompt opcional"
        }
        """
        
        # Validar inputs
        notebook_id = request.data.get('notebook')
        message = request.data.get('message', '').strip()
        system_prompt = request.data.get('system_prompt')
        
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
        
        # Verificar que el notebook existe y pertenece al usuario
        from apps.notebooks.models import Notebook
        try:
            notebook = Notebook.objects.get(id=notebook_id, user=request.user)
        except Notebook.DoesNotExist:
            return Response(
                {'error': 'Notebook no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Obtener servicio Groq
        try:
            llm_service = get_groq_service()
        except LLMServiceError as e:
            logger.warning(f"Groq no disponible: {e}")
            return Response(
                {'error': 'Servicio de IA no disponible'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        # Obtener configuración personalizada del usuario (Fase 6: settings de usuario)
        try:
            from apps.core.models import UserLLMSettings
            user_settings, _ = UserLLMSettings.get_or_create_for_user(request.user)
            model_override = user_settings.model
            temperature_override = user_settings.temperature
            max_tokens_override = user_settings.max_tokens
        except Exception as e:
            logger.warning(f"Error obteniendo configuración LLM del usuario: {e}")
            model_override = None
            temperature_override = None
            max_tokens_override = None
        
        try:
            # 1. Buscar documentos relevantes (RAG)
            from apps.documents.models import Document
            documents = Document.objects.filter(
                notebook=notebook,
                user=request.user
            ).values('title', 'content', 'file_type')[:5]  # Top 5 documentos
            
            context_docs = [
                {
                    'title': f"{doc['title']} ({doc['file_type']})",
                    'content': doc['content'][:500] if doc['content'] else ''
                }
                for doc in documents
            ]
            
            logger.info(
                f"RAG: {len(context_docs)} documentos seleccionados para "
                f"notebook={notebook_id}, user={request.user.id}"
            )
            
            # 2. Obtener historial previo (últimos 10 mensajes)
            prev_messages = ChatMessage.objects.filter(
                user=request.user,
                notebook=notebook
            ).order_by('-created_at')[:10].values('role', 'content')
            
            conversation_history = [
                {'role': msg['role'], 'content': msg['content']}
                for msg in reversed(prev_messages)
            ]
            
            # 3. Llamar Groq con configuración personalizada del usuario
            groq_response = llm_service.generate_response(
                user_message=message,
                system_prompt=system_prompt,
                context_documents=context_docs,
                conversation_history=conversation_history,
                notebook_id=str(notebook_id),
                model_override=model_override,
                temperature_override=temperature_override,
                max_tokens_override=max_tokens_override,
            )
            
            # 4. Guardar mensaje del usuario
            user_msg = ChatMessage.objects.create(
                user=request.user,
                notebook=notebook,
                role='user',
                content=message,
            )
            
            # 5. Guardar respuesta del asistente
            assistant_msg = ChatMessage.objects.create(
                user=request.user,
                notebook=notebook,
                role='assistant',
                content=groq_response['response'],
                tokens_used=groq_response['tokens_used'],
            )
            
            logger.info(
                f"Chat completo: user_msg={user_msg.id}, "
                f"assistant_msg={assistant_msg.id}, "
                f"tokens={groq_response['tokens_used']}"
            )
            
            # 6. Devolver respuesta
            return Response({
                'user_message': ChatMessageSerializer(user_msg).data,
                'assistant_message': ChatMessageSerializer(assistant_msg).data,
                'tokens_used': groq_response['tokens_used'],
                'context_docs': len(context_docs),
                'model': groq_response['model'],
            }, status=status.HTTP_201_CREATED)
        
        except LLMServiceError as e:
            logger.error(f"LLM error: {e}")
            return Response(
                {'error': f'Error en servicio de IA: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            return Response(
                {'error': 'Error interno del servidor'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
