"""
Email client for fetching resumes from IMAP server
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import email
from email.message import Message
from imapclient import IMAPClient
from imapclient.exceptions import IMAPClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailClient:
    """
    Client for connecting to IMAP server and fetching emails with resume attachments
    """

    def __init__(
        self,
        host: str,
        port: int,
        email_address: str,
        password: str,
        use_ssl: bool = True
    ):
        """
        Initialize email client

        Args:
            host: IMAP server host
            port: IMAP server port
            email_address: Email address for authentication
            password: Password or app-specific password
            use_ssl: Whether to use SSL connection
        """
        self.host = host
        self.port = port
        self.email_address = email_address
        self.password = password
        self.use_ssl = use_ssl
        self.client: Optional[IMAPClient] = None

    def connect(self) -> bool:
        """
        Connect to IMAP server

        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.client = IMAPClient(self.host, port=self.port, use_uid=True, ssl=self.use_ssl)
            self.client.login(self.email_address, self.password)
            logger.info(f"Successfully connected to {self.host} as {self.email_address}")
            return True
        except IMAPClientError as e:
            logger.error(f"Failed to connect to IMAP server: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during connection: {e}")
            return False

    def disconnect(self):
        """Disconnect from IMAP server"""
        if self.client:
            try:
                self.client.logout()
                logger.info("Disconnected from IMAP server")
            except Exception as e:
                logger.error(f"Error during disconnect: {e}")

    def select_folder(self, folder: str = "INBOX") -> bool:
        """
        Select email folder

        Args:
            folder: Folder name to select

        Returns:
            True if folder selected successfully
        """
        if not self.client:
            logger.error("Not connected to server")
            return False

        try:
            self.client.select_folder(folder)
            logger.info(f"Selected folder: {folder}")
            return True
        except Exception as e:
            logger.error(f"Failed to select folder {folder}: {e}")
            return False

    def fetch_unread_emails(
        self,
        folder: str = "INBOX",
        subject_filter: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch unread emails from specified folder

        Args:
            folder: Email folder to search
            subject_filter: Optional subject filter
            limit: Maximum number of emails to fetch

        Returns:
            List of email data dictionaries
        """
        if not self.client:
            logger.error("Not connected to server")
            return []

        try:
            self.select_folder(folder)

            # Search for unread emails
            search_criteria = ['UNSEEN']
            if subject_filter:
                search_criteria.append(f'SUBJECT "{subject_filter}"')

            message_ids = self.client.search(search_criteria)

            if limit:
                message_ids = message_ids[:limit]

            logger.info(f"Found {len(message_ids)} unread emails")

            if not message_ids:
                return []

            # Fetch email data
            emails = []
            response = self.client.fetch(message_ids, ['RFC822', 'FLAGS'])

            for msg_id, data in response.items():
                email_data = self._parse_email(msg_id, data)
                if email_data:
                    emails.append(email_data)

            return emails

        except Exception as e:
            logger.error(f"Error fetching emails: {e}")
            return []

    def _parse_email(self, msg_id: int, data: Dict[bytes, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse email message data

        Args:
            msg_id: Message ID
            data: Raw email data from IMAP

        Returns:
            Parsed email data dictionary
        """
        try:
            raw_email = data[b'RFC822']
            msg = email.message_from_bytes(raw_email)

            # Extract basic info
            email_data = {
                'id': msg_id,
                'from': self._decode_header(msg.get('From', '')),
                'to': self._decode_header(msg.get('To', '')),
                'subject': self._decode_header(msg.get('Subject', '')),
                'date': msg.get('Date', ''),
                'body': '',
                'attachments': [],
                'has_attachments': False
            }

            # Extract body and attachments
            if msg.is_multipart():
                for part in msg.walk():
                    self._process_email_part(part, email_data)
            else:
                content_type = msg.get_content_type()
                if content_type == 'text/plain' or content_type == 'text/html':
                    email_data['body'] = self._get_payload(msg)

            email_data['has_attachments'] = len(email_data['attachments']) > 0

            return email_data

        except Exception as e:
            logger.error(f"Error parsing email {msg_id}: {e}")
            return None

    def _process_email_part(self, part: Message, email_data: Dict[str, Any]):
        """
        Process individual part of multipart email

        Args:
            part: Email message part
            email_data: Email data dictionary to update
        """
        content_type = part.get_content_type()
        content_disposition = str(part.get("Content-Disposition", ""))

        # Extract body
        if content_type == "text/plain" and "attachment" not in content_disposition:
            if not email_data['body']:
                email_data['body'] = self._get_payload(part)

        # Extract attachments
        if "attachment" in content_disposition:
            filename = part.get_filename()
            if filename:
                email_data['attachments'].append({
                    'filename': self._decode_header(filename),
                    'content_type': content_type,
                    'data': part.get_payload(decode=True)
                })

    def _get_payload(self, part: Message) -> str:
        """
        Get decoded payload from email part

        Args:
            part: Email message part

        Returns:
            Decoded text content
        """
        try:
            payload = part.get_payload(decode=True)
            if payload:
                # Try different encodings
                for encoding in ['utf-8', 'windows-1251', 'latin-1']:
                    try:
                        return payload.decode(encoding)
                    except (UnicodeDecodeError, AttributeError):
                        continue
                return str(payload)
            return ""
        except Exception as e:
            logger.error(f"Error decoding payload: {e}")
            return ""

    def _decode_header(self, header: str) -> str:
        """
        Decode email header

        Args:
            header: Encoded header string

        Returns:
            Decoded header string
        """
        try:
            decoded_parts = email.header.decode_header(header)
            decoded_header = ""
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    decoded_header += part.decode(encoding or 'utf-8', errors='ignore')
                else:
                    decoded_header += part
            return decoded_header
        except Exception as e:
            logger.error(f"Error decoding header: {e}")
            return header

    def mark_as_read(self, msg_id: int):
        """
        Mark email as read

        Args:
            msg_id: Message ID to mark as read
        """
        if not self.client:
            logger.error("Not connected to server")
            return

        try:
            self.client.add_flags([msg_id], ['\\Seen'])
            logger.info(f"Marked email {msg_id} as read")
        except Exception as e:
            logger.error(f"Error marking email as read: {e}")

    def get_folder_list(self) -> List[str]:
        """
        Get list of available folders

        Returns:
            List of folder names
        """
        if not self.client:
            logger.error("Not connected to server")
            return []

        try:
            folders = self.client.list_folders()
            return [folder[-1] for folder in folders]
        except Exception as e:
            logger.error(f"Error getting folder list: {e}")
            return []

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
