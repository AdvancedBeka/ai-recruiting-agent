"""
Example: Email Integration Usage

This script demonstrates how to use the email integration module
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from email_integration import EmailClient, AttachmentHandler
from config import settings


def example_1_basic_connection():
    """Example 1: Basic IMAP connection"""
    print("\n" + "="*60)
    print("Example 1: Basic IMAP Connection")
    print("="*60)

    # Create email client
    client = EmailClient(
        host=settings.email_host,
        port=settings.email_port,
        email_address=settings.email_address,
        password=settings.email_password
    )

    # Connect
    if client.connect():
        print(f"✓ Connected to {settings.email_host}")

        # List folders
        folders = client.get_folder_list()
        print(f"\nFound {len(folders)} folders:")
        for folder in folders[:5]:
            print(f"  - {folder}")

        client.disconnect()
    else:
        print("✗ Connection failed")


def example_2_fetch_emails():
    """Example 2: Fetch unread emails"""
    print("\n" + "="*60)
    print("Example 2: Fetch Unread Emails")
    print("="*60)

    client = EmailClient(
        host=settings.email_host,
        port=settings.email_port,
        email_address=settings.email_address,
        password=settings.email_password
    )

    if not client.connect():
        print("✗ Connection failed")
        return

    # Fetch emails
    emails = client.fetch_unread_emails(limit=5)
    print(f"\nFetched {len(emails)} unread emails")

    for i, email_data in enumerate(emails, 1):
        print(f"\n--- Email {i} ---")
        print(f"From: {email_data['from']}")
        print(f"Subject: {email_data['subject'][:50]}...")
        print(f"Has attachments: {email_data['has_attachments']}")
        print(f"Number of attachments: {len(email_data['attachments'])}")

    client.disconnect()


def example_3_process_attachments():
    """Example 3: Process and save attachments"""
    print("\n" + "="*60)
    print("Example 3: Process and Save Attachments")
    print("="*60)

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

    if not client.connect():
        print("✗ Connection failed")
        return

    # Fetch and process
    emails = client.fetch_unread_emails(limit=3)
    print(f"\nProcessing {len(emails)} emails...")

    total_saved = 0
    for email_data in emails:
        if email_data['has_attachments']:
            processed = handler.process_attachments(email_data)
            total_saved += len(processed)

            print(f"\nEmail from {email_data['from']}")
            print(f"  Saved {len(processed)} attachment(s)")

    print(f"\n✓ Total: {total_saved} new resume(s) saved")
    client.disconnect()


def example_4_context_manager():
    """Example 4: Using context manager"""
    print("\n" + "="*60)
    print("Example 4: Using Context Manager")
    print("="*60)

    # Context manager automatically connects/disconnects
    with EmailClient(
        host=settings.email_host,
        port=settings.email_port,
        email_address=settings.email_address,
        password=settings.email_password
    ) as client:
        emails = client.fetch_unread_emails(limit=1)
        print(f"Fetched {len(emails)} email(s)")

    print("✓ Connection automatically closed")


def example_5_statistics():
    """Example 5: Get processing statistics"""
    print("\n" + "="*60)
    print("Example 5: Processing Statistics")
    print("="*60)

    handler = AttachmentHandler(
        storage_path=settings.resume_storage_path,
        processed_db_path=settings.processed_emails_db
    )

    # Get stats
    stats = handler.get_processed_stats()
    print(f"\nTotal emails processed: {stats['total_emails_processed']}")
    print(f"Total resumes saved: {stats['total_resumes_saved']}")
    print(f"Storage path: {stats['storage_path']}")
    print(f"Supported formats: {', '.join(stats['supported_formats'])}")

    # List all resumes
    resumes = handler.get_all_resumes()
    if resumes:
        print(f"\nSaved resumes:")
        for resume in resumes[:5]:  # Show first 5
            print(f"\n  Filename: {resume['filename']}")
            print(f"  From: {resume['from']}")
            print(f"  Date: {resume['date']}")
            print(f"  Saved: {resume['saved_path']}")


def example_6_custom_filter():
    """Example 6: Filter emails by subject"""
    print("\n" + "="*60)
    print("Example 6: Filter Emails by Subject")
    print("="*60)

    with EmailClient(
        host=settings.email_host,
        port=settings.email_port,
        email_address=settings.email_address,
        password=settings.email_password
    ) as client:
        # Only fetch emails with "Resume" in subject
        emails = client.fetch_unread_emails(
            subject_filter="Resume",
            limit=10
        )
        print(f"\nFound {len(emails)} email(s) with 'Resume' in subject")

        for email_data in emails:
            print(f"  - {email_data['subject']}")


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print(" "*15 + "EMAIL INTEGRATION EXAMPLES")
    print("="*70)

    examples = [
        ("Basic Connection", example_1_basic_connection),
        ("Fetch Emails", example_2_fetch_emails),
        ("Process Attachments", example_3_process_attachments),
        ("Context Manager", example_4_context_manager),
        ("Statistics", example_5_statistics),
        ("Custom Filter", example_6_custom_filter),
    ]

    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")

    print("\n" + "-"*70)

    # Run all examples
    for name, example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"\n✗ Error in {name}: {e}")

    print("\n" + "="*70)
    print("Done!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
