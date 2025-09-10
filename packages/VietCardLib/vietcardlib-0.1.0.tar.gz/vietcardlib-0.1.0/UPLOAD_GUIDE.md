# VietCardLib Upload Scripts Guide
## Hướng dẫn Upload VietCardLib lên PyPI

### 📋 Available Upload Scripts

1. **`upload_pypi.py`** - Full-featured Python script với tất cả options
2. **`quick_upload.py`** - Python script đơn giản cho upload nhanh  
3. **`upload.ps1`** - PowerShell script cho Windows
4. **`upload.bat`** - Batch file cho Windows (dễ nhất)

### 🚀 Quick Start

#### Option 1: Batch File (Dễ nhất cho Windows)
```cmd
cd VietCardLib
upload.bat
```

#### Option 2: PowerShell
```powershell
cd VietCardLib  
.\upload.ps1
```

#### Option 3: Python Scripts
```bash
cd VietCardLib
python upload_pypi.py    # Full features
python quick_upload.py   # Simple
```

### 📝 Prerequisites

1. **Build package first:**
   ```bash
   python setup.py sdist bdist_wheel
   ```

2. **Install twine:**
   ```bash
   pip install twine
   ```

3. **Create PyPI accounts:**
   - Test PyPI: https://test.pypi.org/account/register/
   - Production PyPI: https://pypi.org/account/register/

### 🔑 Authentication Options

#### Option 1: API Tokens (Recommended)
1. Go to https://test.pypi.org/manage/account/token/
2. Create token with "Entire account" scope
3. Copy token (starts with `pypi-`)
4. Use in upload script

#### Option 2: Username/Password
- Enter your PyPI username and password when prompted

#### Option 3: .pypirc file
Create `~/.pypirc` file:
```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-your-production-token

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-test-token
```

### 📦 Upload Process

#### Step 1: Test PyPI (Recommended first)
```bash
# Test upload
python quick_upload.py
# Choose option 1 (Test PyPI)

# Test installation
pip install -i https://test.pypi.org/simple/ VietCardLib

# Test import
python -c "from VietCardLib import ORBImageAligner; print('Success!')"
```

#### Step 2: Production PyPI
```bash
# Production upload
python quick_upload.py  
# Choose option 2 (Production PyPI)

# Install from production
pip install VietCardLib
```

### 🛠️ Troubleshooting

#### Common Issues:

1. **"No such file or directory: dist/"**
   ```bash
   python setup.py sdist bdist_wheel
   ```

2. **"twine: command not found"**
   ```bash
   pip install twine
   ```

3. **"403 Forbidden"**
   - Check username/password or API token
   - Ensure package name doesn't conflict

4. **"Package already exists"**
   - Update version in `setup.py`
   - Rebuild package

5. **Network/Proxy issues**
   ```bash
   # Use corporate proxy
   python -m twine upload --repository testpypi dist/* --cert "" --client-cert ""
   ```

### 📊 Upload Results

#### Successful Test PyPI Upload:
- 🔗 https://test.pypi.org/project/VietCardLib/
- 📦 `pip install -i https://test.pypi.org/simple/ VietCardLib`

#### Successful Production PyPI Upload:
- 🔗 https://pypi.org/project/VietCardLib/
- 📦 `pip install VietCardLib`

### 🔍 Verification Commands

```bash
# Check package before upload
python -m twine check dist/*

# List files in package
tar -tzf dist/VietCardLib-0.1.0.tar.gz

# Check wheel contents  
unzip -l dist/VietCardLib-0.1.0-py3-none-any.whl

# Verify installation
python -c "import VietCardLib; print(VietCardLib.__version__)"
```

### 📋 Upload Checklist

- [ ] Package built successfully (`dist/` folder exists)
- [ ] Twine installed (`pip install twine`)
- [ ] PyPI accounts created
- [ ] API tokens generated (optional)
- [ ] Package validated (`twine check dist/*`)
- [ ] Uploaded to Test PyPI first
- [ ] Tested installation from Test PyPI
- [ ] Ready for Production PyPI upload

### 🎯 Best Practices

1. **Always test on Test PyPI first**
2. **Use API tokens instead of passwords**
3. **Increment version number for each upload**
4. **Test installation after upload**
5. **Keep credentials secure**

### 💡 Quick Commands Summary

```bash
# Build
python setup.py sdist bdist_wheel

# Check
python -m twine check dist/*

# Upload Test PyPI
python -m twine upload --repository testpypi dist/*

# Upload Production PyPI  
python -m twine upload dist/*

# Test install
pip install -i https://test.pypi.org/simple/ VietCardLib
pip install VietCardLib
```
