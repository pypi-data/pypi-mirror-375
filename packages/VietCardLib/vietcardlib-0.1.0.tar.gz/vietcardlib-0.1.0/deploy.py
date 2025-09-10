#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VietCardLib Deploy Script
========================

Script để deploy VietCardLib lên PyPI
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Chạy command và hiển thị kết quả"""
    print(f"\n🔄 {description}")
    print(f"Command: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Success!")
            if result.stdout:
                print(f"Output: {result.stdout.strip()}")
        else:
            print(f"❌ Error!")
            if result.stderr:
                print(f"Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False
    
    return True

def clean_build():
    """Dọn dẹp build artifacts"""
    print("\n🧹 Cleaning build artifacts...")
    
    dirs_to_clean = ['build', 'dist', 'VietCardLib.egg-info']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   ✅ Removed {dir_name}")
        else:
            print(f"   ⏭️  {dir_name} not found")

def check_dependencies():
    """Kiểm tra các dependencies cần thiết"""
    print("\n🔍 Checking build dependencies...")
    
    required_packages = ['build', 'twine', 'wheel']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"   ❌ {package} is missing")
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        install_cmd = f"pip install {' '.join(missing_packages)}"
        if not run_command(install_cmd, "Installing build dependencies"):
            return False
    
    return True

def build_package():
    """Build package"""
    print("\n🏗️  Building package...")
    
    # Build using python -m build (modern way)
    if not run_command("python -m build", "Building distribution packages"):
        return False
    
    # Check if files were created
    if not os.path.exists("dist"):
        print("❌ Distribution directory not created")
        return False
    
    dist_files = os.listdir("dist")
    if not dist_files:
        print("❌ No distribution files created")
        return False
    
    print(f"✅ Created distribution files:")
    for file in dist_files:
        print(f"   📦 {file}")
    
    return True

def check_package():
    """Kiểm tra package với twine"""
    print("\n🔍 Checking package with twine...")
    
    return run_command("python -m twine check dist/*", "Checking package")

def upload_to_test_pypi():
    """Upload to Test PyPI"""
    print("\n🚀 Uploading to Test PyPI...")
    
    return run_command(
        "python -m twine upload --repository testpypi dist/*",
        "Uploading to Test PyPI"
    )

def upload_to_pypi():
    """Upload to PyPI"""
    print("\n🚀 Uploading to PyPI...")
    
    return run_command(
        "python -m twine upload dist/*",
        "Uploading to PyPI"
    )

def main():
    print("🎯 VietCardLib Deploy Script")
    print("=" * 50)
    
    # Kiểm tra current directory
    if not os.path.exists("setup.py"):
        print("❌ setup.py not found. Please run from VietCardLib directory.")
        sys.exit(1)
    
    # Hiển thị menu
    print("\nDeploy options:")
    print("1. Build only")
    print("2. Build and check")
    print("3. Build and upload to Test PyPI")
    print("4. Build and upload to PyPI")
    print("5. Clean build artifacts")
    
    choice = input("\nSelect option (1-5): ").strip()
    
    if choice == "5":
        clean_build()
        return
    
    # Kiểm tra dependencies
    if not check_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Dọn dẹp build cũ
    clean_build()
    
    # Build package
    if not build_package():
        print("❌ Build failed")
        sys.exit(1)
    
    if choice == "1":
        print("\n✅ Build completed successfully!")
        return
    
    # Check package
    if not check_package():
        print("❌ Package check failed")
        sys.exit(1)
    
    if choice == "2":
        print("\n✅ Build and check completed successfully!")
        return
    
    # Upload
    if choice == "3":
        if upload_to_test_pypi():
            print("\n✅ Successfully uploaded to Test PyPI!")
            print("🔗 Check at: https://test.pypi.org/project/VietCardLib/")
        else:
            print("❌ Upload to Test PyPI failed")
            sys.exit(1)
    
    elif choice == "4":
        confirm = input("\n⚠️  Are you sure you want to upload to PyPI? (yes/no): ")
        if confirm.lower() == "yes":
            if upload_to_pypi():
                print("\n🎉 Successfully uploaded to PyPI!")
                print("🔗 Check at: https://pypi.org/project/VietCardLib/")
            else:
                print("❌ Upload to PyPI failed")
                sys.exit(1)
        else:
            print("❌ Upload cancelled")
    
    else:
        print("❌ Invalid option")
        sys.exit(1)

if __name__ == "__main__":
    main()
