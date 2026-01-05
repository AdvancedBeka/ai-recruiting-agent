"""
Handler for processing email attachments (resumes)
"""
import logging
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AttachmentHandler:
    """
    Handles saving and tracking email attachments (resumes)
    """

    # Supported resume file extensions
    SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.doc', '.txt', '.rtf'}

    def __init__(self, storage_path: Path, processed_db_path: Path):
        """
        Initialize attachment handler

        Args:
            storage_path: Directory to save attachments
            processed_db_path: Path to JSON file tracking processed emails
        """
        self.storage_path = Path(storage_path)
        self.processed_db_path = Path(processed_db_path)

        # Create storage directory
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Load processed emails database
        self.processed_emails = self._load_processed_db()

    def _load_processed_db(self) -> Dict[str, Any]:
        """
        Load database of processed emails

        Returns:
            Dictionary of processed email data
        """
        if self.processed_db_path.exists():
            try:
                with open(self.processed_db_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading processed emails DB: {e}")
                return {}
        return {}

    def _save_processed_db(self):
        """Save processed emails database to file"""
        try:
            self.processed_db_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.processed_db_path, 'w', encoding='utf-8') as f:
                json.dump(self.processed_emails, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving processed emails DB: {e}")

    def is_email_processed(self, email_id: int) -> bool:
        """
        Check if email has already been processed

        Args:
            email_id: Email message ID

        Returns:
            True if email was already processed
        """
        return str(email_id) in self.processed_emails

    def process_attachments(
        self,
        email_data: Dict[str, Any],
        save_attachments: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Process attachments from email

        Args:
            email_data: Email data dictionary
            save_attachments: Whether to save attachments to disk

        Returns:
            List of processed attachment info
        """
        email_id = email_data['id']

        # Check if already processed
        if self.is_email_processed(email_id):
            logger.info(f"Email {email_id} already processed, skipping")
            return []

        attachments = email_data.get('attachments', [])
        processed_attachments = []

        for attachment in attachments:
            filename = attachment['filename']
            file_ext = Path(filename).suffix.lower()

            # Check if it's a supported resume file
            if file_ext not in self.SUPPORTED_EXTENSIONS:
                logger.warning(f"Skipping unsupported file type: {filename}")
                continue

            attachment_info = {
                'original_filename': filename,
                'email_id': email_id,
                'email_from': email_data['from'],
                'email_subject': email_data['subject'],
                'email_date': email_data['date'],
                'content_type': attachment['content_type'],
                'file_size': len(attachment['data']),
                'processed_date': datetime.now().isoformat()
            }

            if save_attachments:
                saved_path = self._save_attachment(
                    attachment['data'],
                    filename,
                    email_id
                )
                if saved_path:
                    attachment_info['saved_path'] = str(saved_path)
                    attachment_info['file_hash'] = self._get_file_hash(attachment['data'])

            processed_attachments.append(attachment_info)
            logger.info(f"Processed attachment: {filename} from email {email_id}")

        # Mark email as processed
        if processed_attachments:
            self._mark_email_processed(email_id, email_data, processed_attachments)

        return processed_attachments

    def _save_attachment(
        self,
        data: bytes,
        filename: str,
        email_id: int
    ) -> Optional[Path]:
        """
        Save attachment to storage

        Args:
            data: File binary data
            filename: Original filename
            email_id: Email message ID

        Returns:
            Path to saved file or None if error
        """
        try:
            # Create unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_ext = Path(filename).suffix
            safe_filename = self._sanitize_filename(Path(filename).stem)
            new_filename = f"{timestamp}_{email_id}_{safe_filename}{file_ext}"

            # Save file
            file_path = self.storage_path / new_filename
            with open(file_path, 'wb') as f:
                f.write(data)

            logger.info(f"Saved attachment to: {file_path}")
            return file_path

        except Exception as e:
            logger.error(f"Error saving attachment {filename}: {e}")
            return None

    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename for safe storage

        Args:
            filename: Original filename

        Returns:
            Sanitized filename
        """
        # Remove unsafe characters
        unsafe_chars = '<>:"/\\|?*'
        for char in unsafe_chars:
            filename = filename.replace(char, '_')

        # Limit length
        max_length = 100
        if len(filename) > max_length:
            filename = filename[:max_length]

        return filename

    def _get_file_hash(self, data: bytes) -> str:
        """
        Calculate SHA256 hash of file data

        Args:
            data: File binary data

        Returns:
            Hex digest of file hash
        """
        return hashlib.sha256(data).hexdigest()

    def _mark_email_processed(
        self,
        email_id: int,
        email_data: Dict[str, Any],
        attachments: List[Dict[str, Any]]
    ):
        """
        Mark email as processed in database

        Args:
            email_id: Email message ID
            email_data: Email data dictionary
            attachments: List of processed attachment info
        """
        self.processed_emails[str(email_id)] = {
            'from': email_data['from'],
            'subject': email_data['subject'],
            'date': email_data['date'],
            'processed_date': datetime.now().isoformat(),
            'attachments': attachments
        }
        self._save_processed_db()
        logger.info(f"Marked email {email_id} as processed")

    def get_processed_stats(self) -> Dict[str, Any]:
        """
        Get statistics about processed emails

        Returns:
            Dictionary with processing statistics
        """
        total_emails = len(self.processed_emails)
        total_attachments = sum(
            len(email['attachments'])
            for email in self.processed_emails.values()
        )

        return {
            'total_emails_processed': total_emails,
            'total_resumes_saved': total_attachments,
            'supported_formats': list(self.SUPPORTED_EXTENSIONS),
            'storage_path': str(self.storage_path)
        }

    def get_all_resumes(self) -> List[Dict[str, Any]]:
        """
        Get list of all saved resumes

        Returns:
            List of resume information dictionaries
        """
        resumes = []
        for email_id, email_info in self.processed_emails.items():
            for attachment in email_info['attachments']:
                resumes.append({
                    'email_id': email_id,
                    'filename': attachment['original_filename'],
                    'saved_path': attachment.get('saved_path'),
                    'from': email_info['from'],
                    'date': email_info['date'],
                    'processed_date': attachment['processed_date']
                })
        return resumes
