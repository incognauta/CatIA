"""
LLM Service: Groq API integration + RAG (Retrieval Augmented Generation)
Fase 4C
"""
import logging
from typing import List, Dict, Optional
from decouple import config

try:
    from groq import Groq
except ImportError:
    Groq = None

logger = logging.getLogger(__name__)

# Configuración
GROQ_API_KEY = config('GROQ_API_KEY', default='')
GROQ_MODEL = 'llama-3.1-8b-instant'
MAX_TOKENS = 1024


class LLMServiceError(Exception):
    """Error en servicio LLM"""
    pass


class GroqService:
    """Servicio centralizado para Groq API con RAG"""
    
    def __init__(self):
        """Inicializar cliente Groq"""
        if not GROQ_API_KEY:
            raise LLMServiceError("GROQ_API_KEY no configurada en .env")
        
        if Groq is None:
            raise LLMServiceError("groq no instalado. Instala: pip install groq")
        
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = GROQ_MODEL
    
    @staticmethod
    def build_rag_context(documents: List[Dict], max_chars: int = 3000) -> str:
        """
        Construir contexto RAG a partir de documentos relevantes
        
        Args:
            documents: Lista de dicts con 'title' y 'content'
            max_chars: Máximo de caracteres del contexto
        
        Returns:
            String con contexto formateado
        """
        if not documents:
            return ""
        
        context_parts = []
        total_chars = 0
        
        for doc in documents:
            title = doc.get('title', 'Documento sin título')
            content = doc.get('content', '')[:500]  # Limitar por documento
            
            part = f"📄 **{title}**\n{content}\n"
            if total_chars + len(part) > max_chars:
                break
            
            context_parts.append(part)
            total_chars += len(part)
        
        return "\n".join(context_parts)
    
    def generate_response(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
        context_documents: Optional[List[Dict]] = None,
        conversation_history: Optional[List[Dict]] = None,
        notebook_id: Optional[str] = None,
    ) -> Dict:
        """
        Generar respuesta con Groq + contexto RAG
        
        Args:
            user_message: Mensaje del usuario
            system_prompt: Prompt del sistema (default: assistente educativo)
            context_documents: Documentos para RAG
            conversation_history: Historial de conversación previo
            notebook_id: ID del notebook (para logging)
        
        Returns:
            {
                'response': str,
                'tokens_used': int,
                'model': str,
                'stop_reason': str,
            }
        """
        try:
            # Sistema prompt por default
            if system_prompt is None:
                system_prompt = (
                    "Eres un asistente educativo especializado en procesar documentos. "
                    "Responde preguntas basadas en los documentos proporcionados. "
                    "Si la información no está en los documentos, indícalo claramente. "
                    "Mantén respuestas concisas y precisas."
                )
            
            # Construir contexto RAG
            rag_context = ""
            if context_documents:
                rag_context = self.build_rag_context(context_documents)
                system_prompt += f"\n\n**Contexto de documentos disponibles:**\n{rag_context}"
            
            # Preparar mensajes
            messages = []
            
            # Agregar historial previo (limitar a últimos 5 mensajes para evitar token overflow)
            if conversation_history:
                for msg in conversation_history[-5:]:
                    messages.append({
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", "")
                    })
            
            # Agregar mensaje actual
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            # Llamada a Groq
            logger.info(
                f"Groq request: model={self.model}, "
                f"tokens_max={MAX_TOKENS}, "
                f"messages={len(messages)}, "
                f"notebook={notebook_id}"
            )
            
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    *messages
                ],
                max_tokens=MAX_TOKENS,
                temperature=0.7,
            )
            
            # Extraer respuesta
            response_text = completion.choices[0].message.content
            tokens_used = completion.usage.total_tokens
            stop_reason = completion.choices[0].finish_reason
            
            logger.info(
                f"Groq response: tokens={tokens_used}, "
                f"stop_reason={stop_reason}, "
                f"notebook={notebook_id}"
            )
            
            return {
                'response': response_text,
                'tokens_used': tokens_used,
                'model': self.model,
                'stop_reason': stop_reason,
            }
        
        except Exception as e:
            logger.error(f"Groq error: {str(e)}", exc_info=True)
            raise LLMServiceError(f"Error llamando a Groq: {str(e)}")
    
    @staticmethod
    def truncate_context(text: str, max_tokens: int = 4096) -> str:
        """
        Truncar texto a aproximadamente max_tokens
        (Groq usa ~4 caracteres por token en promedio)
        """
        chars_per_token = 4
        max_chars = max_tokens * chars_per_token
        
        if len(text) > max_chars:
            return text[:max_chars] + "... [truncado]"
        return text


# Global instance
_groq_service = None


def get_groq_service() -> GroqService:
    """Singleton para GroqService"""
    global _groq_service
    if _groq_service is None:
        try:
            _groq_service = GroqService()
        except LLMServiceError as e:
            logger.warning(f"Groq no disponible: {e}")
            return None
    return _groq_service
