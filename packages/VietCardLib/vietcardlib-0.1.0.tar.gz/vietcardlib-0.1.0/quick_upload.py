#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Upload Script cho VietCardLib
===================================

Script upload nhanh với minimal setup
"""

import os
import sys
import subprocess
import getpass

def run_cmd(cmd, description):
    """Chạy command"""
    print(f"\n🔄 {description}")
    print(f"💻 {cmd}")
    
    result = subprocess.run(cmd, shell=True)
    if result.returncode == 0:
        print("✅ Success!")
        return True
    else:
        print("❌ Failed!")
        return False

def quick_upload():
    """Upload nhanh"""
    print("🚀 VIETCARDLIB QUICK UPLOAD")
    print("=" * 40)
    
    # Kiểm tra files
    if not os.path.exists("dist"):
        print("❌ dist/ folder not found")
        print("💡 Run: python setup.py sdist bdist_wheel")
        return
    
    files = os.listdir("dist")
    print(f"📦 Found {len(files)} files in dist/:")
    for f in files:
        print(f"   - {f}")
    
    print("\n🎯 Upload Options:")
    print("1. Test PyPI (recommended first)")
    print("2. Production PyPI")
    print("3. Both (Test first)")
    
    choice = input("\nChoice (1-3): ").strip()
    
    if choice == "1":
        upload_test()
    elif choice == "2":
        upload_prod()
    elif choice == "3":
        upload_test()
        upload_prod()
    else:
        print("❌ Invalid choice")

def upload_test():
    """Upload to Test PyPI"""
    print("\n🧪 UPLOADING TO TEST PYPI")
    print("-" * 30)
    
    # Check twine
    if not run_cmd("python -m twine check dist/*", "Checking packages"):
        return
    
    print("\n🔑 Choose authentication:")
    print("1. Username/Password")
    print("2. API Token")
    
    auth_choice = input("Choice (1-2): ").strip()
    
    if auth_choice == "1":
        username = input("Test PyPI Username: ")
        password = getpass.getpass("Test PyPI Password: ")
        
        cmd = f'python -m twine upload --repository testpypi dist/* -u "{username}" -p "{password}"'
        
    elif auth_choice == "2":
        token = getpass.getpass("Test PyPI Token (pypi-...): ")
        
        cmd = f'python -m twine upload --repository testpypi dist/* -u "__token__" -p "{token}"'
        
    else:
        print("❌ Invalid choice")
        return
    
    if run_cmd(cmd, "Uploading to Test PyPI"):
        print("\n✅ Upload successful!")
        print("🔗 https://test.pypi.org/project/VietCardLib/")
        print("📦 Test: pip install -i https://test.pypi.org/simple/ VietCardLib")

def upload_prod():
    """Upload to Production PyPI"""
    print("\n🎯 UPLOADING TO PRODUCTION PYPI")
    print("-" * 35)
    
    confirm = input("⚠️  Upload to PRODUCTION PyPI? (yes/no): ")
    if confirm.lower() != "yes":
        print("❌ Cancelled")
        return
    
    print("\n🔑 Choose authentication:")
    print("1. Username/Password")
    print("2. API Token")
    
    auth_choice = input("Choice (1-2): ").strip()
    
    if auth_choice == "1":
        username = input("PyPI Username: ")
        password = getpass.getpass("PyPI Password: ")
        
        cmd = f'python -m twine upload dist/* -u "{username}" -p "{password}"'
        
    elif auth_choice == "2":
        token = getpass.getpass("PyPI Token (pypi-...): ")
        
        cmd = f'python -m twine upload dist/* -u "__token__" -p "{token}"'
        
    else:
        print("❌ Invalid choice")
        return
    
    if run_cmd(cmd, "Uploading to Production PyPI"):
        print("\n🎉 Upload successful!")
        print("🔗 https://pypi.org/project/VietCardLib/")
        print("📦 Install: pip install VietCardLib")

if __name__ == "__main__":
    if not os.path.exists("setup.py"):
        print("❌ Run from VietCardLib directory")
        sys.exit(1)
    
    quick_upload()
