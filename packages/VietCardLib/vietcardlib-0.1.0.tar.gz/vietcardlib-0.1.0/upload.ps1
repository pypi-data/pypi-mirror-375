# VietCardLib Upload Script for Windows PowerShell
# ================================================

Write-Host "🚀 VIETCARDLIB UPLOAD SCRIPT" -ForegroundColor Green
Write-Host "=" * 50

# Check if we're in the right directory
if (-not (Test-Path "setup.py")) {
    Write-Host "❌ setup.py not found. Please run from VietCardLib directory." -ForegroundColor Red
    exit 1
}

# Check dist folder
if (-not (Test-Path "dist")) {
    Write-Host "❌ dist/ folder not found" -ForegroundColor Red
    Write-Host "💡 Please run: python setup.py sdist bdist_wheel" -ForegroundColor Yellow
    exit 1
}

$distFiles = Get-ChildItem "dist"
Write-Host "📦 Found $($distFiles.Count) files in dist/:" -ForegroundColor Cyan
foreach ($file in $distFiles) {
    $sizeKB = [math]::Round($file.Length / 1024, 1)
    Write-Host "   - $($file.Name) ($sizeKB KB)" -ForegroundColor Gray
}

# Main menu
Write-Host "`n🎯 Upload Options:" -ForegroundColor Yellow
Write-Host "1. Test PyPI (recommended first)"
Write-Host "2. Production PyPI"
Write-Host "3. Both (Test PyPI first, then Production)"
Write-Host "4. Check packages only"

$choice = Read-Host "Select option (1-4)"

switch ($choice) {
    "1" {
        Write-Host "`n🧪 UPLOADING TO TEST PYPI" -ForegroundColor Cyan
        Write-Host "-" * 30
        
        # Check packages first
        Write-Host "🔍 Checking packages..." -ForegroundColor Yellow
        python -m twine check dist/*
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Package check failed" -ForegroundColor Red
            exit 1
        }
        
        # Get credentials
        Write-Host "`n🔑 Authentication method:" -ForegroundColor Yellow
        Write-Host "1. Username/Password"
        Write-Host "2. API Token (recommended)"
        
        $authChoice = Read-Host "Choose (1-2)"
        
        if ($authChoice -eq "1") {
            $username = Read-Host "Test PyPI Username"
            $password = Read-Host "Test PyPI Password" -AsSecureString
            $passwordText = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($password))
            
            Write-Host "🚀 Uploading to Test PyPI..." -ForegroundColor Green
            python -m twine upload --repository testpypi dist/* -u $username -p $passwordText
        }
        elseif ($authChoice -eq "2") {
            $token = Read-Host "Test PyPI Token (pypi-...)" -AsSecureString
            $tokenText = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($token))
            
            Write-Host "🚀 Uploading to Test PyPI..." -ForegroundColor Green
            python -m twine upload --repository testpypi dist/* -u "__token__" -p $tokenText
        }
        else {
            Write-Host "❌ Invalid choice" -ForegroundColor Red
            exit 1
        }
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "`n✅ Upload to Test PyPI successful!" -ForegroundColor Green
            Write-Host "🔗 Check at: https://test.pypi.org/project/VietCardLib/" -ForegroundColor Cyan
            Write-Host "📦 Test install: pip install -i https://test.pypi.org/simple/ VietCardLib" -ForegroundColor Yellow
        } else {
            Write-Host "`n❌ Upload to Test PyPI failed!" -ForegroundColor Red
        }
    }
    
    "2" {
        Write-Host "`n🎯 UPLOADING TO PRODUCTION PYPI" -ForegroundColor Magenta
        Write-Host "-" * 35
        
        $confirm = Read-Host "⚠️  Are you sure you want to upload to PRODUCTION PyPI? (yes/no)"
        if ($confirm -ne "yes") {
            Write-Host "❌ Upload cancelled" -ForegroundColor Red
            exit 0
        }
        
        # Check packages first
        Write-Host "🔍 Checking packages..." -ForegroundColor Yellow
        python -m twine check dist/*
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Package check failed" -ForegroundColor Red
            exit 1
        }
        
        # Get credentials
        Write-Host "`n🔑 Authentication method:" -ForegroundColor Yellow
        Write-Host "1. Username/Password"
        Write-Host "2. API Token (recommended)"
        
        $authChoice = Read-Host "Choose (1-2)"
        
        if ($authChoice -eq "1") {
            $username = Read-Host "PyPI Username"
            $password = Read-Host "PyPI Password" -AsSecureString
            $passwordText = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($password))
            
            Write-Host "🚀 Uploading to Production PyPI..." -ForegroundColor Green
            python -m twine upload dist/* -u $username -p $passwordText
        }
        elseif ($authChoice -eq "2") {
            $token = Read-Host "PyPI Token (pypi-...)" -AsSecureString
            $tokenText = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($token))
            
            Write-Host "🚀 Uploading to Production PyPI..." -ForegroundColor Green
            python -m twine upload dist/* -u "__token__" -p $tokenText
        }
        else {
            Write-Host "❌ Invalid choice" -ForegroundColor Red
            exit 1
        }
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "`n🎉 Upload to Production PyPI successful!" -ForegroundColor Green
            Write-Host "🔗 Check at: https://pypi.org/project/VietCardLib/" -ForegroundColor Cyan
            Write-Host "📦 Install: pip install VietCardLib" -ForegroundColor Yellow
        } else {
            Write-Host "`n❌ Upload to Production PyPI failed!" -ForegroundColor Red
        }
    }
    
    "3" {
        Write-Host "`n🎯 SEQUENTIAL UPLOAD: Test PyPI → Production PyPI" -ForegroundColor Magenta
        Write-Host "This will upload to Test PyPI first, then Production PyPI"
        
        $confirm = Read-Host "Continue? (yes/no)"
        if ($confirm -ne "yes") {
            Write-Host "❌ Cancelled" -ForegroundColor Red
            exit 0
        }
        
        # Call this script recursively for Test PyPI
        Write-Host "`n📍 Step 1: Test PyPI Upload" -ForegroundColor Cyan
        & powershell.exe -File $PSCommandPath -ArgumentList "1"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "`n⏳ Waiting 10 seconds before Production upload..." -ForegroundColor Yellow
            Start-Sleep -Seconds 10
            
            Write-Host "`n📍 Step 2: Production PyPI Upload" -ForegroundColor Cyan
            & powershell.exe -File $PSCommandPath -ArgumentList "2"
        } else {
            Write-Host "`n❌ Test PyPI upload failed. Skipping Production upload." -ForegroundColor Red
        }
    }
    
    "4" {
        Write-Host "`n🔍 CHECKING PACKAGES" -ForegroundColor Cyan
        Write-Host "-" * 20
        
        python -m twine check dist/*
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "`n✅ All packages are valid!" -ForegroundColor Green
        } else {
            Write-Host "`n❌ Package validation failed!" -ForegroundColor Red
        }
    }
    
    default {
        Write-Host "❌ Invalid option" -ForegroundColor Red
        exit 1
    }
}

Write-Host "`n🎯 Upload script completed!" -ForegroundColor Green
