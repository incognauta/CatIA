"""
Implementación concreta de LLMService para Groq

Esta es la implementación específica para el proveedor Groq.
El código existente en llm_service.py original se refactoriza aquí.
"""

from typing import Dict, List, Optional
import logging
from functools import lru_cache

from django.conf import settings
from groq import Groq

from .base import LLMServiceBase, RAGServiceBase

logger = logging.getLogger(__name__)


class GroqLLMService(LLMServiceBase):
    """
    Implementación concreta de LLMService usando Groq API
    
    Proporciona generación de respuestas usando los modelos de Groq.
    """
    
    def __init__(self):
        """Inicializar servicio Groq"""
        try:
            api_key = settings.GROQ_CONFIG.get('API_KEY')
            if not api_key:
                raise ValueError("GROQ_CONFIG['API_KEY'] no configurada")
            
            self.client = Groq(api_key=api_key)
            self.model = settings.GROQ_CONFIG.get('MODEL', 'llama-3.1-8b-instant')
            self.temperature = settings.GROQ_CONFIG.get('TEMPERATURE', 0.7)
            self.max_tokens = settings.GROQ_CONFIG.get('MAX_TOKENS', 1024)
            
            logger.info(f"GroqLLMService initialized: model={self.model}")
        except Exception as e:
            logger.error(f"Error initializing GroqLLMService: {e}")
            raise
    
    def generate_response(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
        context_documents: Optional[List[Dict]] = None,
        conversation_history: Optional[List[Dict]] = None,
        notebook_id: Optional[str] = None,
        model_override: Optional[str] = None,
        temperature_override: Optional[float] = None,
        max_tokens_override: Optional[int] = None,
    ) -> Dict:
        """Implementación de generate_response para Groq"""
        
        try:
            # Usar defaults o valores especificados
            system_prompt = system_prompt or (
                "Eres un asistente educativo especializado en análisis de documentos. "
                "Proporciona respuestas claras, concisas y fundamentadas en el contexto suministrado."
            )
            
            context_documents = context_documents or []
            conversation_history = conversation_history or []
            
            # Construir contexto RAG
            rag_service = GroqRAGService()
            rag_context = rag_service.build_context(
                documents=context_documents,
                query=user_message,
                max_chars=settings.DOCUMENT_CONFIG.get('MAX_CHARS_TOTAL', 3000)
            )
            
            # Construir mensajes
            messages = []
            
            # Agregar historial previo (últimos 5 mensajes)
            if conversation_history:
                for msg in conversation_history[-5:]:
                    messages.append({
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", "")
                    })
            
            # Agregar mensaje actual
            message_content = user_message
            if rag_context:
                message_content = f"Contexto de documentos:\n{rag_context}\n\nPregunta: {user_message}"
            
            messages.append({
                "role": "user",
                "content": message_content
            })
            
            # Usar overrides de usuario si se proporcionan
            model_to_use = model_override or self.model
            temperature_to_use = temperature_override if temperature_override is not None else self.temperature
            max_tokens_to_use = max_tokens_override or self.max_tokens
            
            logger.info(
                f"Groq request: model={model_to_use}, "
                f"temp={temperature_to_use}, "
                f"tokens_max={max_tokens_to_use}, "
                f"notebook={notebook_id}"
            )
            
            # Llamada a Groq
            completion = self.client.chat.completions.create(
                model=model_to_use,
                messages=[
                    {"role": "system", "content": system_prompt},
                    *messages
                ],
                max_tokens=max_tokens_to_use,
                temperature=temperature_to_use,
            )
            
            # Extraer respuesta
            response_text = completion.choices[0].message.content
            
            # Contar tokens usados
            tokens_used = getattr(completion.usage, 'completion_tokens', 0)
            
            logger.info(f"Groq response: {len(response_text)} chars, {tokens_used} tokens")
            
            return {
                'response': response_text,
                'tokens_used': tokens_used,
                'model': model_to_use,
            }
        
        except Exception as e:
            logger.error(f"Error generating response with Groq: {e}")
            raise
    
    def validate_api_key(self) -> bool:
        """Validar que API key sea válida"""
        try:
            # Intentar listar modelos disponibles
            models = self.client.models.list()
            return len(list(models)) > 0
        except Exception as e:
            logger.warning(f"Invalid Groq API key: {e}")
            return False
    
    def get_available_models(self) -> List[Dict[str, str]]:
        """Retornar modelos disponibles de Groq"""
        return [
            {
                'value': 'llama-3.1-8b-instant',
                'label': 'Llama 3.1 8B (Rápido, equilibrado)'
            },
            {
                'value': 'mixtral-8x7b-32768',
                'label': 'Mixtral 8x7B (Potente, contexto largo)'
            },
            {
                'value': 'gemma-7b-it',
                'label': 'Gemma 7B (Compacto, rápido)'
            },
        ]


class GroqRAGService(RAGServiceBase):
    """
    Implementación de RAG service para Groq
    
    Construye contexto relevante a partir de documentos.
    """
    
    def build_context(
        self,
        documents: List[Dict],
        query: str,
        max_chars: int = 3000
    ) -> str:
        """Construir contexto RAG"""
        if not documents:
            return ""
        
        # Encontrar chunks relevantes
        all_chunks = []
        for doc in documents:
            title = doc.get('title', 'Documento sin título')
            content = doc.get('content', '')
            
            if content:
                # Dividir en chunks pequeños
                chunks = self._split_text(content, chunk_size=500)
                for chunk in chunks:
                    all_chunks.append({
                        'title': title,
                        'content': chunk
                    })
        
        # Seleccionar chunks relevantes
        relevant_chunks = self.find_relevant_chunks(
            chunks=[c['content'] for c in all_chunks],
            query=query,
            top_k=5
        )
        
        # Construir contexto formateado
        context = "## Contexto de documentos:\n\n"
        total_chars = 0
        
        for i, chunk in enumerate(relevant_chunks, 1):
            # Encontrar el documento original de este chunk
            for doc_chunk in all_chunks:
                if doc_chunk['content'] == chunk:
                    title = doc_chunk['title']
                    break
            else:
                title = "Documento"
            
            chunk_text = f"**{title}** (Fragmento {i}):\n{chunk}\n\n"
            
            if total_chars + len(chunk_text) <= max_chars:
                context += chunk_text
                total_chars += len(chunk_text)
            else:
                # Agregar indicador de truncado
                context += "[... contenido adicional truncado ...]"
                break
        
        return context
    
    def find_relevant_chunks(
        self,
        chunks: List[str],
        query: str,
        top_k: int = 5
    ) -> List[str]:
        """
        Encontrar chunks relevantes basado en keyword matching
        
        (En futuro, puede ser reemplazado con embeddings/semantic search)
        """
        if not chunks:
            return []
        
        query_words = set(query.lower().split())
        
        # Calcular relevancia de cada chunk
        scored_chunks = []
        for chunk in chunks:
            chunk_lower = chunk.lower()
            
            # Contar matches de palabras
            matches = sum(1 for word in query_words if word in chunk_lower)
            
            # Bonus por longitud (más contenido = más útil)
            length_score = min(len(chunk) / 100, 5)
            
            # Score final
            score = matches + length_score
            
            scored_chunks.append((chunk, score))
        
        # Ordenar por score descendente y retornar top_k
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        return [chunk for chunk, _ in scored_chunks[:top_k]]
    
    @staticmethod
    def _split_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Dividir texto en chunks con overlap"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap if end < len(text) else end
        
        return chunks
