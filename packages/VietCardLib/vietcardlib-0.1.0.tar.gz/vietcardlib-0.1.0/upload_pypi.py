#!/usr/bin/env python3
"""
PyPI Upload Script with Proxy Support
Handles SSL certificate issues and proxy configuration for PyPI uploads.
"""

import os
import sys
import subprocess
import ssl
import urllib3
from pathlib import Path

def setup_proxy_environment():
    """Configure proxy environment variables"""
    proxy_url = "http://cuongbo:bohem2805@160.30.112.35:3128"
    
    os.environ['HTTP_PROXY'] = proxy_url
    os.environ['HTTPS_PROXY'] = proxy_url
    os.environ['http_proxy'] = proxy_url
    os.environ['https_proxy'] = proxy_url
    
    # Disable SSL verification for corporate proxy
    os.environ['PYTHONHTTPSVERIFY'] = '0'
    os.environ['CURL_CA_BUNDLE'] = ''
    
    print(f"✅ Proxy configured: {proxy_url}")

def disable_ssl_warnings():
    """Disable SSL warnings"""
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    print("✅ SSL warnings disabled")

def check_and_install_twine():
    """Check if twine is installed, install if not"""
    try:
        result = subprocess.run([sys.executable, "-m", "twine", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Twine is already installed")
            return True
    except FileNotFoundError:
        pass
    
    print("📦 Installing twine...")
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "install", "twine"],
                              check=True, capture_output=True, text=True)
        print("✅ Twine installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install twine: {e}")
        print(f"Error output: {e.stderr}")
        return False

def upload_to_testpypi():
    """Upload to TestPyPI first for testing"""
    print("🔧 Uploading to TestPyPI...")
    
    # Check and install twine if needed
    if not check_and_install_twine():
        return False
    
    cmd = [
        sys.executable, "-m", "twine", "upload", 
        "--repository", "testpypi",
        "--config-file", ".pypirc",
        "--cert", "",  # Disable cert verification
        "--verbose",
        "dist/*"
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Upload to TestPyPI successful!")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Upload to TestPyPI failed:")
        print(e.stderr)
        return False

def upload_to_pypi():
    """Upload to production PyPI"""
    print("🔧 Uploading to PyPI...")
    
    # Check and install twine if needed
    if not check_and_install_twine():
        return False
    
    cmd = [
        sys.executable, "-m", "twine", "upload",
        "--config-file", ".pypirc", 
        "--cert", "",  # Disable cert verification
        "--verbose",
        "dist/*"
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Upload to PyPI successful!")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Upload to PyPI failed:")
        print(e.stderr)
        return False

def main():
    """Main upload process"""
    print("🚀 Starting PyPI upload with proxy support...")
    
    # Check if dist directory exists
    if not Path("dist").exists():
        print("❌ No dist/ directory found. Run 'python -m build' first.")
        sys.exit(1)
    
    # Setup environment
    setup_proxy_environment()
    disable_ssl_warnings()
    
    # Ask user for upload preference
    choice = input("\nChoose upload destination:\n1. TestPyPI (recommended for testing)\n2. Production PyPI\n3. Both\nEnter choice (1/2/3): ").strip()
    
    if choice == "1":
        upload_to_testpypi()
    elif choice == "2":
        # Warn about production upload
        confirm = input("⚠️  You're about to upload to production PyPI. Continue? (y/N): ").strip().lower()
        if confirm == 'y':
            upload_to_pypi()
        else:
            print("Upload cancelled.")
    elif choice == "3":
        if upload_to_testpypi():
            confirm = input("\n✅ TestPyPI upload successful. Upload to production PyPI? (y/N): ").strip().lower()
            if confirm == 'y':
                upload_to_pypi()
    else:
        print("Invalid choice. Exiting.")

if __name__ == "__main__":
    main()
