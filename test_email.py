"""
Test script for email integration
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from email_integration import EmailClient, AttachmentHandler
from config import settings


def test_connection():
    """Test email connection"""
    print("=" * 60)
    print("Testing Email Connection")
    print("=" * 60)

    client = EmailClient(
        host=settings.email_host,
        port=settings.email_port,
        email_address=settings.email_address,
        password=settings.email_password
    )

    if client.connect():
        print(f"✓ Successfully connected to {settings.email_host}")

        # List folders
        folders = client.get_folder_list()
        print(f"\nAvailable folders ({len(folders)}):")
        for folder in folders[:10]:  # Show first 10
            print(f"  - {folder}")

        client.disconnect()
        return True
    else:
        print("✗ Failed to connect")
        return False


def fetch_and_process_resumes(limit: int = 5):
    """Fetch and process resume emails"""
    print("\n" + "=" * 60)
    print("Fetching Resume Emails")
    print("=" * 60)

    # Initialize components
    client = EmailClient(
        host=settings.email_host,
        port=settings.email_port,
        email_address=settings.email_address,
        password=settings.email_password
    )

    handler = AttachmentHandler(
        storage_path=settings.resume_storage_path,
        processed_db_path=settings.processed_emails_db
    )

    # Connect and fetch
    if not client.connect():
        print("✗ Failed to connect")
        return

    print(f"Searching for unread emails in '{settings.email_folder}'...\n")

    emails = client.fetch_unread_emails(
        folder=settings.email_folder,
        subject_filter=settings.email_subject_filter,
        limit=limit
    )

    if not emails:
        print("No unread emails found")
        client.disconnect()
        return

    print(f"Found {len(emails)} unread email(s)\n")

    # Process each email
    total_resumes = 0
    for i, email_data in enumerate(emails, 1):
        print(f"\n--- Email {i}/{len(emails)} ---")
        print(f"From: {email_data['from']}")
        print(f"Subject: {email_data['subject']}")
        print(f"Date: {email_data['date']}")
        print(f"Attachments: {len(email_data['attachments'])}")

        if email_data['attachments']:
            print("\nAttachments:")
            for att in email_data['attachments']:
                print(f"  - {att['filename']} ({att['content_type']})")

        # Process attachments
        processed = handler.process_attachments(email_data, save_attachments=True)

        if processed:
            print(f"\n✓ Saved {len(processed)} resume(s)")
            total_resumes += len(processed)

            # Mark as read (optional - comment out if you want to keep as unread)
            # client.mark_as_read(email_data['id'])
        else:
            if handler.is_email_processed(email_data['id']):
                print("  (Already processed)")
            else:
                print("  No valid resume attachments found")

    client.disconnect()

    print("\n" + "=" * 60)
    print(f"Processing complete: {total_resumes} new resume(s) saved")
    print("=" * 60)


def show_statistics():
    """Show processing statistics"""
    print("\n" + "=" * 60)
    print("Statistics")
    print("=" * 60)

    handler = AttachmentHandler(
        storage_path=settings.resume_storage_path,
        processed_db_path=settings.processed_emails_db
    )

    stats = handler.get_processed_stats()
    print(f"\nTotal emails processed: {stats['total_emails_processed']}")
    print(f"Total resumes saved: {stats['total_resumes_saved']}")
    print(f"Storage path: {stats['storage_path']}")
    print(f"Supported formats: {', '.join(stats['supported_formats'])}")

    # List all resumes
    resumes = handler.get_all_resumes()
    if resumes:
        print(f"\nSaved resumes:")
        for resume in resumes:
            print(f"  - {resume['filename']} (from: {resume['from']})")


def main():
    """Main test function"""
    print("\n" + "=" * 60)
    print("AI Recruiting Agent - Email Integration Test")
    print("=" * 60)

    try:
        # Test connection
        if not test_connection():
            print("\n⚠ Connection failed. Please check your .env configuration:")
            print("  - EMAIL_ADDRESS")
            print("  - EMAIL_PASSWORD")
            print("  - EMAIL_HOST")
            print("  - EMAIL_PORT")
            return

        # Fetch and process
        fetch_and_process_resumes(limit=10)

        # Show stats
        show_statistics()

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
