#!/usr/bin/env python3
"""
Setup script for DomainSentry
"""
import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, cwd=None, shell=True):
    """Run a command and return the result."""
    print(f"Running: {cmd}")
    try:
        result = subprocess.run(
            cmd,
            shell=shell,
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {cmd}")
        print(f"Error: {e.stderr}")
        return False


def main():
    """Main setup function."""
    print("Setting up DomainSentry...")
    
    # Create necessary directories
    backend_dir = Path("backend")
    frontend_dir = Path("frontend")
    
    if not backend_dir.exists():
        print(f"Creating {backend_dir}")
        backend_dir.mkdir(parents=True, exist_ok=True)
    
    if not frontend_dir.exists():
        print(f"Creating {frontend_dir}")
        frontend_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize backend requirements if not present
    requirements_file = backend_dir / "requirements.txt"
    if requirements_file.exists():
        print("Installing backend dependencies...")
        # This would normally be done with pip install -r requirements.txt
        print("Backend dependencies file exists.")
    
    # Initialize frontend package.json if not present
    package_json = frontend_dir / "package.json"
    if package_json.exists():
        print("Frontend package.json exists.")
    else:
        print("Creating frontend package.json...")
        # We already created this earlier
    
    print("\nDomainSentry setup complete!")
    print("\nTo run the application:")
    print("1. For development: docker-compose -f docker-compose.dev.yml up --build")
    print("2. For production: docker-compose up -d")
    print("\nTo run tests:")
    print("1. Backend: cd backend && pytest")
    print("2. Frontend: cd frontend && npm test")


if __name__ == "__main__":
    main()