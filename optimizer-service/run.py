#!/usr/bin/env python3
"""
Startup script for SLSQP Optimizer Microservice.
Run this script to start the optimizer service without Docker.

Usage:
    python run.py
    python run.py --host 0.0.0.0 --port 8001
"""
import argparse
import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import main
from app.config import settings


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SLSQP Optimizer Microservice")
    parser.add_argument(
        "--host",
        default=settings.HOST,
        help=f"Host to bind to (default: {settings.HOST})"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=settings.PORT,
        help=f"Port to bind to (default: {settings.PORT})"
    )
    parser.add_argument(
        "--log-level",
        default=settings.LOG_LEVEL,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help=f"Log level (default: {settings.LOG_LEVEL})"
    )

    args = parser.parse_args()

    # Update settings
    os.environ["OPTIMIZER_HOST"] = args.host
    os.environ["OPTIMIZER_PORT"] = str(args.port)
    os.environ["LOG_LEVEL"] = args.log_level

    print("=" * 60)
    print("  SLSQP Optimizer Microservice")
    print("=" * 60)
    print(f"  Host: {args.host}")
    print(f"  Port: {args.port}")
    print(f"  Log Level: {args.log_level}")
    print(f"  API Docs: http://{args.host}:{args.port}/docs")
    print("=" * 60)
    print()

    # Run the application
    main()
