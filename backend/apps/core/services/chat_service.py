"""
Implementación de ChatService - Orquestación de lógica de chat

Encapsula toda la lógica de negocio para procesar preguntas del usuario,
construir contexto RAG, obtener respuestas de IA y guardar historial.
"""

import logging
from typing import Dict, List, Optional

from .base import ChatServiceBase
from apps.core.llm_service import get_llm_service, LLMServiceError

logger = logging.getLogger(__name__)


class DjangoChatService(ChatServiceBase):
    """
    Implementación de ChatService usando Django models
    
    Orquesta:
    1. Obtención de contexto RAG de documentos
    2. Recuperación de historial de conversación
    3. Llamada al servicio LLM (Groq/OpenAI/etc.)
    4. Persistencia de mensajes
    5. Configuración personalizada del usuario
    """
    
    def process_query(
        self,
        user_id: str,
        notebook_id: str,
        message: str,
        system_prompt: Optional[str] = None,
    ) -> Dict:
        """
        Procesar pregunta del usuario: RAG + LLM + persistencia
        
        Flujo:
        1. Validar inputs (notebook existe y pertenece al usuario)
        2. Obtener contexto RAG (documentos del notebook)
        3. Obtener historial previo (últimos 10 mensajes)
        4. Obtener configuración personalizada del usuario
        5. Llamar LLM con contexto
        6. Guardar mensaje del usuario y respuesta
        7. Retornar resultado completo
        
        Args:
            user_id: ID del usuario
            notebook_id: ID del notebook
            message: Mensaje del usuario
            system_prompt: Prompt del sistema opcional
        
        Returns:
            Dict con resultado del chat
        
        Raises:
            ValueError: Si inputs no son válidos
            LLMServiceError: Si falla el servicio LLM
        """
        from django.contrib.auth import get_user_model

        User = get_user_model()
        from apps.notebooks.models import Notebook
        from apps.documents.models import Document
        from apps.chat.models import ChatMessage
        from apps.core.models import UserLLMSettings
        
        # 1. Validar inputs
        if not message or not message.strip():
            raise ValueError("Mensaje no puede estar vacío")
        
        message = message.strip()
        
        # 2. Verificar que el notebook existe y pertenece al usuario
        try:
            user = User.objects.get(id=user_id)
            notebook = Notebook.objects.get(id=notebook_id, user=user)
        except (User.DoesNotExist, Notebook.DoesNotExist):
            raise ValueError("Notebook no encontrado o no pertenece al usuario")
        
        # 3. Obtener contexto RAG (documentos del notebook)
        documents = Document.objects.filter(
            notebook=notebook,
            user=user
        ).values('title', 'content', 'file_type')[:5]  # Top 5
        
        context_docs = [
            {
                'title': f"{doc['title']} ({doc['file_type']})",
                'content': doc['content'][:500] if doc['content'] else ''
            }
            for doc in documents
        ]
        
        logger.info(
            f"RAG: {len(context_docs)} documentos para notebook={notebook_id}"
        )
        
        # 4. Obtener historial previo (últimos 10 mensajes)
        prev_messages = ChatMessage.objects.filter(
            user=user,
            notebook=notebook
        ).order_by('-created_at')[:10].values('role', 'content')
        
        conversation_history = [
            {'role': msg['role'], 'content': msg['content']}
            for msg in reversed(prev_messages)
        ]
        
        # 5. Obtener configuración personalizada del usuario
        try:
            user_settings, _ = UserLLMSettings.get_or_create_for_user(user)
            model_override = user_settings.model
            temperature_override = user_settings.temperature
            max_tokens_override = user_settings.max_tokens
        except Exception as e:
            logger.warning(f"Error obteniendo configuración del usuario: {e}")
            model_override = None
            temperature_override = None
            max_tokens_override = None
        
        # 6. Obtener servicio LLM y generar respuesta
        try:
            llm_service = get_llm_service()
        except LLMServiceError as e:
            logger.warning(f"Groq no disponible: {e}")
            raise LLMServiceError("Servicio de IA no disponible")
        
        try:
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
        except Exception as e:
            logger.error(f"Error en LLM: {e}")
            raise LLMServiceError(f"Error generando respuesta: {str(e)}")
        
        # 7. Guardar mensajes
        user_msg = ChatMessage.objects.create(
            user=user,
            notebook=notebook,
            role='user',
            content=message,
        )
        
        assistant_msg = ChatMessage.objects.create(
            user=user,
            notebook=notebook,
            role='assistant',
            content=groq_response['response'],
            tokens_used=groq_response['tokens_used'],
        )
        
        logger.info(
            f"Chat procesado: user_msg={user_msg.id}, "
            f"assistant_msg={assistant_msg.id}, "
            f"tokens={groq_response['tokens_used']}"
        )
        
        # 8. Retornar resultado completo
        from apps.chat.serializers import ChatMessageSerializer
        
        return {
            'user_message': ChatMessageSerializer(user_msg).data,
            'assistant_message': ChatMessageSerializer(assistant_msg).data,
            'tokens_used': groq_response['tokens_used'],
            'context_docs': len(context_docs),
            'model': groq_response['model'],
        }
    
    def get_conversation_history(
        self,
        user_id: str,
        notebook_id: str,
        limit: int = 10,
    ) -> List[Dict]:
        """
        Obtener historial de conversación formateado para el cliente
        
        Args:
            user_id: ID del usuario
            notebook_id: ID del notebook
            limit: Número máximo de mensajes
        
        Returns:
            Lista de mensajes [{'role': 'user'/'assistant', 'content': ...}]
        """
        from django.contrib.auth import get_user_model

        User = get_user_model()
        from apps.notebooks.models import Notebook
        from apps.chat.models import ChatMessage
        
        try:
            user = User.objects.get(id=user_id)
            notebook = Notebook.objects.get(id=notebook_id, user=user)
        except (User.DoesNotExist, Notebook.DoesNotExist):
            raise ValueError("Usuario o notebook no encontrado")
        
        messages = ChatMessage.objects.filter(
            user=user,
            notebook=notebook
        ).order_by('-created_at')[:limit].values('role', 'content')
        
        history = [
            {'role': msg['role'], 'content': msg['content']}
            for msg in reversed(messages)
        ]
        
        return history
    
    def clear_history(
        self,
        user_id: str,
        notebook_id: str,
    ) -> int:
        """
        Limpiar historial de conversación
        
        Args:
            user_id: ID del usuario
            notebook_id: ID del notebook
        
        Returns:
            Número de mensajes eliminados
        """
        from django.contrib.auth import get_user_model

        User = get_user_model()
        from apps.notebooks.models import Notebook
        from apps.chat.models import ChatMessage
        
        try:
            user = User.objects.get(id=user_id)
            notebook = Notebook.objects.get(id=notebook_id, user=user)
        except (User.DoesNotExist, Notebook.DoesNotExist):
            raise ValueError("Usuario o notebook no encontrado")
        
        deleted_count, _ = ChatMessage.objects.filter(
            user=user,
            notebook=notebook
        ).delete()
        
        logger.info(f"Historial limpiado: {deleted_count} mensajes eliminados")
        
        return deleted_count
