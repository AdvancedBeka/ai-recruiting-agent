"""
PDF Parser для извлечения текста из PDF файлов
"""
import logging
from pathlib import Path
from typing import Optional
from PyPDF2 import PdfReader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PDFParser:
    """Парсер для PDF файлов"""

    def __init__(self):
        """Инициализация PDF парсера"""
        self.supported_extensions = ['.pdf']

    def can_parse(self, file_path: str) -> bool:
        """
        Проверка, может ли парсер обработать файл

        Args:
            file_path: Путь к файлу

        Returns:
            True если файл можно обработать
        """
        return Path(file_path).suffix.lower() in self.supported_extensions

    def extract_text(self, file_path: str) -> Optional[str]:
        """
        Извлечение текста из PDF файла

        Args:
            file_path: Путь к PDF файлу

        Returns:
            Извлеченный текст или None при ошибке
        """
        if not self.can_parse(file_path):
            logger.error(f"Unsupported file type: {file_path}")
            return None

        try:
            path = Path(file_path)
            if not path.exists():
                logger.error(f"File not found: {file_path}")
                return None

            # Читаем PDF
            with open(path, 'rb') as file:
                pdf_reader = PdfReader(file)

                # Получаем количество страниц
                num_pages = len(pdf_reader.pages)
                logger.info(f"PDF has {num_pages} page(s)")

                # Извлекаем текст со всех страниц
                text_parts = []
                for page_num in range(num_pages):
                    try:
                        page = pdf_reader.pages[page_num]
                        page_text = page.extract_text()

                        if page_text:
                            text_parts.append(page_text)
                            logger.debug(f"Extracted {len(page_text)} chars from page {page_num + 1}")
                    except Exception as e:
                        logger.warning(f"Error extracting page {page_num + 1}: {e}")
                        continue

                # Объединяем текст всех страниц
                full_text = "\n\n".join(text_parts)

                if not full_text.strip():
                    logger.warning(f"No text extracted from {file_path}")
                    return None

                logger.info(f"Successfully extracted {len(full_text)} characters from {path.name}")
                return full_text

        except Exception as e:
            logger.error(f"Error parsing PDF {file_path}: {e}")
            return None

    def get_metadata(self, file_path: str) -> dict:
        """
        Получение метаданных PDF

        Args:
            file_path: Путь к PDF файлу

        Returns:
            Словарь с метаданными
        """
        metadata = {
            'num_pages': 0,
            'author': None,
            'title': None,
            'subject': None,
            'creator': None,
            'producer': None,
            'creation_date': None
        }

        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                metadata['num_pages'] = len(pdf_reader.pages)

                if pdf_reader.metadata:
                    metadata.update({
                        'author': pdf_reader.metadata.get('/Author'),
                        'title': pdf_reader.metadata.get('/Title'),
                        'subject': pdf_reader.metadata.get('/Subject'),
                        'creator': pdf_reader.metadata.get('/Creator'),
                        'producer': pdf_reader.metadata.get('/Producer'),
                        'creation_date': pdf_reader.metadata.get('/CreationDate')
                    })

        except Exception as e:
            logger.error(f"Error getting PDF metadata: {e}")

        return metadata
