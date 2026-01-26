#!/usr/bin/env python3
# run.py - Main entry point for Loops Visualization System

"""
Loops Visualization System
==========================
A modular visualization system with:
- HTML/CSS/JS Frontend Dashboard
- Python Flask Backend
- Micro Apps (Simulations with dedicated control panels)

Run this file to start the system!
"""

import os
import sys
import webbrowser
import time
import threading
from pathlib import Path

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))


def check_dependencies():
    """Check and install required dependencies."""
    required = ['flask', 'flask-cors']
    missing = []
    
    for package in required:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"📦 Installing missing dependencies: {', '.join(missing)}")
        import subprocess
        subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing)
        print("✅ Dependencies installed!")
    
    return True


def open_browser():
    """Open the dashboard in the default browser after a delay."""
    time.sleep(1.5)
    webbrowser.open('http://127.0.0.1:5000')


def main():
    """Start the Loops Visualization System."""
    print()
    print("=" * 60)
    print("   🔄 LOOPS VISUALIZATION SYSTEM")
    print("=" * 60)
    print()
    
    # Check dependencies
    print("📋 Checking dependencies...")
    check_dependencies()
    print()
    
    # Open browser in background thread
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    # Import and run server
    from backend.server import main as run_server
    run_server()


if __name__ == "__main__":
    main()
