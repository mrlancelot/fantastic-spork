#!/usr/bin/env python3
"""Clean TravelAI Backend Entry Point

This is the new, clean entry point for the TravelAI backend.
Replaces the old main.py and app.py with a single, maintainable implementation.

Usage:
    python main-clean.py              # Production server
    python main-clean.py --dev        # Development server with reload
    python main-clean.py --test       # Test configuration
"""

import argparse
import sys
from pathlib import Path

# Add src to Python path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def main():
    """Main entry point with argument parsing"""
    parser = argparse.ArgumentParser(description="TravelAI Backend Server")
    parser.add_argument("--dev", action="store_true", help="Run in development mode with auto-reload")
    parser.add_argument("--test", action="store_true", help="Run with test configuration")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to (default: 8000)")
    parser.add_argument("--workers", type=int, default=1, help="Number of worker processes (production only)")
    
    args = parser.parse_args()
    
    # Import after adding src to path
    import uvicorn
    from core.config import get_settings
    
    settings = get_settings()
    
    # Configure based on arguments
    if args.test:
        import os
        os.environ["ENVIRONMENT"] = "testing"
        print("\n" + "="*60)
        print("🧪 RUNNING IN TEST MODE")
        print("="*60)
    elif args.dev:
        import os
        os.environ["ENVIRONMENT"] = "development"
        os.environ["DEBUG"] = "true"
        print("\n" + "="*60)
        print("🚀 TRAVELAI BACKEND - DEVELOPMENT MODE")
        print("="*60)
        print(f"📍 Server: http://{args.host}:{args.port}")
        print(f"📊 Docs: http://{args.host}:{args.port}/docs")
        print(f"🔄 Auto-reload: Enabled")
        print("="*60 + "\n")
    else:
        print("\n" + "="*60)
        print("🚀 TRAVELAI BACKEND - PRODUCTION MODE")
        print("="*60)
        print(f"📍 Server: http://{args.host}:{args.port}")
        print(f"👥 Workers: {args.workers}")
        print("="*60 + "\n")
    
    # Configure uvicorn
    config = {
        "app": "api:app",
        "host": args.host,
        "port": args.port,
        "log_level": "debug" if args.dev else "info",
    }
    
    if args.dev:
        config["reload"] = True
        config["reload_dirs"] = [str(src_path)]
    elif not args.test:
        config["workers"] = args.workers
    
    # Start the server
    try:
        uvicorn.run(**config)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
