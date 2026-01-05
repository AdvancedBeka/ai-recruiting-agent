# Makefile for AI Recruiting Agent
# Windows compatible commands

.PHONY: help install test clean run demo stats

help:
	@echo "AI Recruiting Agent - Available Commands:"
	@echo ""
	@echo "  make install     - Install dependencies"
	@echo "  make test        - Run email integration test"
	@echo "  make demo        - Run examples"
	@echo "  make stats       - Show processing statistics"
	@echo "  make clean       - Clean data directory"
	@echo "  make setup       - Initial setup (install + config)"
	@echo ""

install:
	pip install -r requirements.txt

setup: install
	@echo "Copying .env.example to .env..."
	@if not exist .env copy .env.example .env
	@echo ""
	@echo "Please edit .env file with your email credentials"
	@echo ""

test:
	python test_email.py

demo:
	python examples/email_integration_demo.py

stats:
	@python -c "import sys; sys.path.insert(0, 'src'); from email_integration import AttachmentHandler; from config import settings; h = AttachmentHandler(settings.resume_storage_path, settings.processed_emails_db); stats = h.get_processed_stats(); print(f\"Emails processed: {stats['total_emails_processed']}\"); print(f\"Resumes saved: {stats['total_resumes_saved']}\")"

clean:
	@echo "Cleaning data directory..."
	@if exist data rmdir /s /q data
	@echo "Done!"

lint:
	flake8 src/ --max-line-length=100
	black --check src/

format:
	black src/
