@echo off
REM VietCardLib Upload Batch Script
REM ================================

REM Configure proxy settings
set HTTP_PROXY=http://thanhdn2:thanhdn2!@116.118.47.171:3128
set HTTPS_PROXY=http://thanhdn2:thanhdn2!@116.118.47.171:3128
set http_proxy=http://thanhdn2:thanhdn2!@116.118.47.171:3128
set https_proxy=http://thanhdn2:thanhdn2!@116.118.47.171:3128

echo.
echo ============================================================
echo 🚀 VIETCARDLIB UPLOAD SCRIPT
echo ============================================================

REM Check if setup.py exists
if not exist "setup.py" (
    echo ❌ setup.py not found. Please run from VietCardLib directory.
    pause
    exit /b 1
)

REM Check dist folder
if not exist "dist\" (
    echo ❌ dist\ folder not found
    echo 💡 Please run: python setup.py sdist bdist_wheel
    pause
    exit /b 1
)

echo 📦 Package files found:
dir dist\ /b

echo.
echo 🎯 Upload Options:
echo 1. Test PyPI (recommended first)
echo 2. Production PyPI  
echo 3. Both (Test first, then Production)
echo 4. Check packages only
echo 5. Install twine (if not installed)
echo.

set /p choice="Select option (1-5): "

if "%choice%"=="1" goto test_pypi
if "%choice%"=="2" goto prod_pypi
if "%choice%"=="3" goto both_pypi
if "%choice%"=="4" goto check_only
if "%choice%"=="5" goto install_twine

echo ❌ Invalid option
pause
exit /b 1

:install_twine
echo.
echo 📦 Installing twine...
python -m pip install twine
if %errorlevel% neq 0 (
    echo ❌ Failed to install twine
    pause
    exit /b 1
)
echo ✅ Twine installed successfully
pause
exit /b 0

:check_only
echo.
echo 🔍 Checking packages...
python -m twine check dist/*
if %errorlevel% neq 0 (
    echo ❌ Package check failed
    pause
    exit /b 1
)
echo ✅ All packages are valid!
pause
exit /b 0

:test_pypi
echo.
echo ============================================================
echo 🧪 UPLOADING TO TEST PYPI
echo ============================================================

REM Check packages first
echo 🔍 Checking packages...
python -m twine check dist/*
if %errorlevel% neq 0 (
    echo ❌ Package check failed
    pause
    exit /b 1
)

echo.
echo 🔑 Authentication options:
echo 1. Username/Password
echo 2. API Token (recommended)
echo 3. Use existing .pypirc
echo.

set /p auth_choice="Choose authentication (1-3): "

if "%auth_choice%"=="1" goto test_userpass
if "%auth_choice%"=="2" goto test_token
if "%auth_choice%"=="3" goto test_pypirc

echo ❌ Invalid choice
pause
exit /b 1

:test_userpass
set /p username="Test PyPI Username: "
set /p password="Test PyPI Password: "

echo 🚀 Uploading to Test PyPI...
python -m twine upload --repository testpypi dist/* -u "%username%" -p "%password%"
goto test_result

:test_token
set /p token="Test PyPI Token (pypi-...): "

echo 🚀 Uploading to Test PyPI...
python -m twine upload --repository testpypi dist/* -u "__token__" -p "%token%"
goto test_result

:test_pypirc
echo 🚀 Uploading to Test PyPI using .pypirc...
python -m twine upload --repository testpypi dist/*
goto test_result

:test_result
if %errorlevel% equ 0 (
    echo.
    echo ✅ Upload to Test PyPI successful!
    echo 🔗 Check at: https://test.pypi.org/project/VietCardLib/
    echo 📦 Test install: pip install -i https://test.pypi.org/simple/ VietCardLib
) else (
    echo.
    echo ❌ Upload to Test PyPI failed!
)
pause
exit /b %errorlevel%

:prod_pypi
echo.
echo ============================================================
echo 🎯 UPLOADING TO PRODUCTION PYPI
echo ============================================================

set /p confirm="⚠️  Are you sure you want to upload to PRODUCTION PyPI? (yes/no): "
if not "%confirm%"=="yes" (
    echo ❌ Upload cancelled
    pause
    exit /b 0
)

REM Check packages first
echo 🔍 Checking packages...
python -m twine check dist/*
if %errorlevel% neq 0 (
    echo ❌ Package check failed
    pause
    exit /b 1
)

echo.
echo 🔑 Authentication options:
echo 1. Username/Password
echo 2. API Token (recommended)
echo 3. Use existing .pypirc
echo.

set /p auth_choice="Choose authentication (1-3): "

if "%auth_choice%"=="1" goto prod_userpass
if "%auth_choice%"=="2" goto prod_token
if "%auth_choice%"=="3" goto prod_pypirc

echo ❌ Invalid choice
pause
exit /b 1

:prod_userpass
set /p username="PyPI Username: "
set /p password="PyPI Password: "

echo 🚀 Uploading to Production PyPI...
python -m twine upload dist/* -u "%username%" -p "%password%"
goto prod_result

:prod_token
set /p token="PyPI Token (pypi-...): "

echo 🚀 Uploading to Production PyPI...
python -m twine upload dist/* -u "__token__" -p "%token%"
goto prod_result

:prod_pypirc
echo 🚀 Uploading to Production PyPI using .pypirc...
python -m twine upload dist/*
goto prod_result

:prod_result
if %errorlevel% equ 0 (
    echo.
    echo 🎉 Upload to Production PyPI successful!
    echo 🔗 Check at: https://pypi.org/project/VietCardLib/
    echo 📦 Install: pip install VietCardLib
) else (
    echo.
    echo ❌ Upload to Production PyPI failed!
)
pause
exit /b %errorlevel%

:both_pypi
echo.
echo ============================================================
echo 🎯 SEQUENTIAL UPLOAD: Test PyPI → Production PyPI
echo ============================================================

echo Step 1: Upload to Test PyPI
call :test_pypi

if %errorlevel% equ 0 (
    echo.
    echo ⏳ Waiting 10 seconds before Production upload...
    timeout /t 10 /nobreak >nul
    
    echo.
    echo Step 2: Upload to Production PyPI
    call :prod_pypi
) else (
    echo.
    echo ❌ Test PyPI upload failed. Skipping Production upload.
)

pause
exit /b %errorlevel%
