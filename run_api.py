"""
Run FastAPI server for AI Recruiting Agent
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import uvicorn
from api.app import app

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("AI Recruiting Agent API Server")
    print("=" * 60)
    print("\n🚀 Starting server...")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("📖 ReDoc: http://localhost:8000/redoc")
    print("❤️  Health Check: http://localhost:8000/health")
    print("\n" + "=" * 60 + "\n")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=False,  # Set to True for development
    )
