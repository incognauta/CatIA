"""
File processors para Fase 4B
Soporta: PDF, DOCX, TXT, Imágenes
"""
import os
import logging
from pathlib import Path
from typing import Dict, Tuple
from io import BytesIO

import PyPDF2
import pytesseract
from PIL import Image
from docx import Document as DocxDocument

logger = logging.getLogger(__name__)

# Tipos de archivo soportados
SUPPORTED_TYPES = {
    'application/pdf': 'pdf',
    'text/plain': 'txt',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
    'image/png': 'image',
    'image/jpeg': 'image',
    'image/jpg': 'image',
}

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


class FileProcessorError(Exception):
    """Error en procesamiento de archivo"""
    pass


class FileProcessor:
    """Procesador centralizado de archivos con OCR"""
    
    @staticmethod
    def validate_file(file, content_type: str) -> Tuple[bool, str]:
        """
        Validar que el archivo sea soportado y esté dentro de límites
        
        Returns:
            (is_valid, error_message)
        """
        if content_type not in SUPPORTED_TYPES:
            supported = ', '.join(SUPPORTED_TYPES.keys())
            return False, f"Tipo no soportado. Soportados: {supported}"
        
        file_size = file.size if hasattr(file, 'size') else len(file.getvalue())
        if file_size > MAX_FILE_SIZE:
            return False, f"Archivo excede límite de {MAX_FILE_SIZE / 1024 / 1024}MB"
        
        return True, ""
    
    @staticmethod
    def process_pdf(file_obj) -> Dict[str, str]:
        """
        Procesar PDF:
        1. Extraer texto con PyPDF2
        2. Si está escaneado, usar OCR con pytesseract
        
        Returns:
            {
                'text': 'Contenido extraído con PDF reader',
                'ocr_text': 'Contenido extraído con OCR (si aplica)',
                'pages': número de páginas,
                'is_scanned': bool (si fue necesario OCR)
            }
        """
        try:
            file_obj.seek(0)
            pdf_reader = PyPDF2.PdfReader(file_obj)
            num_pages = len(pdf_reader.pages)
            
            # Intentar extraer texto con PDF reader
            text_parts = []
            for page in pdf_reader.pages:
                try:
                    text_parts.append(page.extract_text())
                except Exception as e:
                    logger.warning(f"Error extrayendo texto de página: {e}")
            
            extracted_text = "\n".join(text_parts).strip()
            
            # Si PDF es scaneado (poco texto), usar OCR
            is_scanned = len(extracted_text) < 100 and num_pages > 0
            ocr_text = ""
            
            if is_scanned:
                logger.info(f"PDF parece escaneado, aplicando OCR...")
                ocr_text = FileProcessor._extract_text_with_ocr(file_obj)
            
            return {
                'text': extracted_text,
                'ocr_text': ocr_text if is_scanned else "",
                'pages': num_pages,
                'is_scanned': is_scanned,
            }
        
        except Exception as e:
            raise FileProcessorError(f"Error procesando PDF: {str(e)}")
    
    @staticmethod
    def process_image(file_obj) -> Dict[str, str]:
        """
        Procesar imagen con OCR
        
        Returns:
            {
                'text': 'Contenido extraído con OCR',
                'ocr_text': Mismo que text,
                'pages': 1,
                'is_scanned': True
            }
        """
        try:
            file_obj.seek(0)
            img = Image.open(file_obj)
            text = pytesseract.image_to_string(img, lang='spa+eng')
            
            return {
                'text': text.strip(),
                'ocr_text': text.strip(),
                'pages': 1,
                'is_scanned': True,
            }
        
        except Exception as e:
            raise FileProcessorError(f"Error procesando imagen: {str(e)}")
    
    @staticmethod
    def process_docx(file_obj) -> Dict[str, str]:
        """
        Procesar documento DOCX
        
        Returns:
            {
                'text': 'Contenido del documento',
                'ocr_text': '',
                'pages': estimado,
                'is_scanned': False
            }
        """
        try:
            file_obj.seek(0)
            doc = DocxDocument(file_obj)
            
            # Extraer párrafos
            paragraphs = [para.text for para in doc.paragraphs]
            text = "\n".join(paragraphs).strip()
            
            # Estimar páginas (aproximadamente 3000 caracteres por página)
            estimated_pages = max(1, len(text) // 3000)
            
            return {
                'text': text,
                'ocr_text': "",
                'pages': estimated_pages,
                'is_scanned': False,
            }
        
        except Exception as e:
            raise FileProcessorError(f"Error procesando DOCX: {str(e)}")
    
    @staticmethod
    def process_text(file_obj) -> Dict[str, str]:
        """
        Procesar archivo de texto plano
        
        Returns:
            {
                'text': 'Contenido del archivo',
                'ocr_text': '',
                'pages': estimado,
                'is_scanned': False
            }
        """
        try:
            file_obj.seek(0)
            # Detectar encoding
            raw = file_obj.read()
            try:
                text = raw.decode('utf-8')
            except UnicodeDecodeError:
                text = raw.decode('latin-1')
            
            text = text.strip()
            estimated_pages = max(1, len(text) // 3000)
            
            return {
                'text': text,
                'ocr_text': "",
                'pages': estimated_pages,
                'is_scanned': False,
            }
        
        except Exception as e:
            raise FileProcessorError(f"Error procesando TXT: {str(e)}")
    
    @staticmethod
    def _extract_text_with_ocr(file_obj) -> str:
        """
        Extraer texto de PDF con OCR (pytesseract)
        Convierte PDF a imagenes primero
        """
        try:
            from pdf2image import convert_from_bytes
            
            file_obj.seek(0)
            pdf_bytes = file_obj.read()
            
            # Convertir solo primeras 5 páginas (por rendimiento)
            images = convert_from_bytes(pdf_bytes, first_page=1, last_page=5)
            
            ocr_texts = []
            for img in images:
                try:
                    text = pytesseract.image_to_string(img, lang='spa+eng')
                    if text.strip():
                        ocr_texts.append(text)
                except Exception as e:
                    logger.warning(f"Error en OCR de página: {e}")
            
            return "\n".join(ocr_texts)
        
        except ImportError:
            logger.warning("pdf2image no disponible, saltando OCR")
            return ""
        except Exception as e:
            logger.warning(f"Error en OCR: {e}")
            return ""
    
    @staticmethod
    def process_file(file_obj, content_type: str, filename: str) -> Dict:
        """
        Procesar archivo según tipo y devolver metadata + contenido
        
        Args:
            file_obj: File-like object
            content_type: MIME type (ej: 'application/pdf')
            filename: Nombre original del archivo
        
        Returns:
            {
                'file_type': 'pdf',
                'original_filename': filename,
                'file_size': bytes,
                'pages': número de páginas,
                'content': texto extraído,
                'content_markdown': placeholder para futuro,
                'is_scanned': bool,
            }
        """
        # Validar
        is_valid, error = FileProcessor.validate_file(file_obj, content_type)
        if not is_valid:
            raise FileProcessorError(error)
        
        file_size = file_obj.size if hasattr(file_obj, 'size') else len(file_obj.getvalue())
        file_type = SUPPORTED_TYPES.get(content_type, 'unknown')
        
        # Procesar según tipo
        if file_type == 'pdf':
            result = FileProcessor.process_pdf(file_obj)
        elif file_type == 'image':
            result = FileProcessor.process_image(file_obj)
        elif file_type == 'docx':
            result = FileProcessor.process_docx(file_obj)
        elif file_type == 'txt':
            result = FileProcessor.process_text(file_obj)
        else:
            raise FileProcessorError(f"Tipo de archivo no soportado: {file_type}")
        
        return {
            'file_type': file_type,
            'original_filename': filename,
            'file_size': file_size,
            'pages': result.get('pages', 1),
            'content': result.get('text', ''),
            'content_markdown': result.get('text', ''),  # TODO: convertir a markdown
            'is_scanned': result.get('is_scanned', False),
        }
