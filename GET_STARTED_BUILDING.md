# Get Started Building Alarmify

Follow these steps to build Alarmify from source.

## Step 1: Prerequisites

Install these tools before building:

### Required

1. **Python 3.10 or higher**
   ```powershell
   # Check version
   python --version
   
   # Should show: Python 3.10.x or higher
   ```
   Download: https://www.python.org/downloads/

2. **Python Packages**
   ```powershell
   # Install dependencies
   pip install -r requirements.txt
   pip install pyinstaller
   ```

### Optional (for installer)

3. **Inno Setup 6**
   - Download: https://jrsoftware.org/isdl.php
   - Install to default location
   - Used to create Windows installer

## Step 2: Verify Environment

Run the verification script:

```powershell
python verify_build_env.py
```

This checks:
- ✓ Python version is correct
- ✓ All packages are installed
- ✓ Project files are present
- ✓ Inno Setup is available
- ✓ Disk space is sufficient

**Expected Output:**
```
✓ All checks passed! Ready to build.
```

If any checks fail, follow the suggestions to fix them.

## Step 3: Build

Choose your build type:

### Option A: Build Executable Only (Fast)

```powershell
python build_installer.py --skip-inno
```

**Output:** `dist/Alarmify.exe`

**Time:** ~2-5 minutes

**Use when:**
- Testing during development
- Don't need installer
- Inno Setup not installed

### Option B: Build Complete Installer (Recommended)

```powershell
python build_installer.py
```

**Outputs:**
- `dist/Alarmify.exe` - Standalone executable
- `Output/AlarmifySetup-1.0.0.exe` - Windows installer

**Time:** ~3-7 minutes

**Use when:**
- Creating release
- Need professional installer
- Want Start Menu shortcuts

### Option C: Build Without Tests (Fastest)

```powershell
python build_installer.py --skip-tests --skip-inno
```

**Time:** ~1-3 minutes

**Use when:**
- Rapid iteration during development
- Already tested manually

## Step 4: Test Your Build

### Test Executable

```powershell
# Run the executable
.\dist\Alarmify.exe
```

Verify:
- ✓ Application launches
- ✓ UI appears correctly
- ✓ No error messages
- ✓ Can navigate menus

### Test Installer

```powershell
# Run the installer
.\Output\AlarmifySetup-1.0.0.exe
```

Verify:
- ✓ Installer launches
- ✓ Can complete installation
- ✓ Start Menu shortcuts created
- ✓ Application runs from shortcut

### Run Automated Tests

```powershell
# Run all tests
python -m pytest tests/ -v

# Run build verification tests
python -m pytest tests/test_build.py -v
```

## Step 5: Troubleshooting

### Problem: "Python not found"

**Solution:**
```powershell
# Add Python to PATH during installation
# Or use full path:
C:\Python310\python.exe verify_build_env.py
```

### Problem: "Module not found"

**Solution:**
```powershell
# Reinstall dependencies
pip install -r requirements.txt
pip install pyinstaller pytest
```

### Problem: "ISCC.exe not found"

**Solution:**
```powershell
# Either install Inno Setup:
# Download from: https://jrsoftware.org/isdl.php

# Or skip installer creation:
python build_installer.py --skip-inno
```

### Problem: "Build fails with error"

**Solution:**
```powershell
# Clean everything and rebuild
Remove-Item -Recurse -Force build, dist, Output -ErrorAction SilentlyContinue
python build_installer.py
```

### Problem: "Executable won't run"

**Solution:**
```powershell
# Check if antivirus is blocking it
# Try running as administrator
# Check Windows SmartScreen settings
```

## Common Build Scenarios

### Scenario 1: Quick Development Build

```powershell
# Fast build for testing
python build_installer.py --skip-tests --skip-inno

# Test it
.\dist\Alarmify.exe
```

### Scenario 2: Release Build

```powershell
# Update version
python version_manager.py --bump minor

# Full build with all checks
python build_installer.py

# Test installer
.\Output\AlarmifySetup-1.1.0.exe
```

### Scenario 3: Debug Build

```powershell
# Edit alarmify.spec:
# Change: console=False to console=True

# Build
python -m PyInstaller alarmify.spec

# Run and see console output
.\dist\Alarmify.exe
```

## Next Steps

### For Developers

- Read [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines
- Check [BUILD.md](BUILD.md) for detailed build documentation
- Review [BUILD_QUICKSTART.md](BUILD_QUICKSTART.md) for quick reference

### For Releases

- Follow [RELEASE.md](RELEASE.md) for release process
- Use version_manager.py for version updates
- Test on clean Windows installation

### For Code Signing

- Read [code_signing_config.md](code_signing_config.md)
- Obtain code signing certificate
- Configure signing in build scripts

## Build System Files

Quick reference to build system files:

| File | Purpose |
|------|---------|
| `build_installer.py` | Main build script |
| `alarmify.spec` | PyInstaller config |
| `installer.iss` | Inno Setup script |
| `version_manager.py` | Version management |
| `verify_build_env.py` | Environment check |

## Getting Help

### Check Documentation

1. **GET_STARTED_BUILDING.md** (this file) - Getting started
2. **BUILD_QUICKSTART.md** - Quick reference
3. **BUILD.md** - Complete guide
4. **RELEASE.md** - Release process
5. **CONTRIBUTING.md** - Development guide

### Run Verification

```powershell
python verify_build_env.py
```

### Check Tests

```powershell
python -m pytest tests/test_build.py -v
```

### Search Issues

Check GitHub Issues for similar problems:
https://github.com/yourusername/alarmify/issues

### Create Issue

If stuck, create an issue with:
- What you tried to do
- What went wrong (error messages)
- Your environment (Python version, OS)
- Output from verify_build_env.py

## Success!

If you successfully built Alarmify, congratulations! 🎉

You now have:
- ✓ Working development environment
- ✓ Built executable or installer
- ✓ Understanding of build process

Share your experience or contribute improvements!

---

**Quick Commands Summary**

```powershell
# Setup
pip install -r requirements.txt
pip install pyinstaller

# Verify
python verify_build_env.py

# Build
python build_installer.py

# Test
python -m pytest tests/ -v
.\dist\Alarmify.exe

# Version
python version_manager.py --get
```

**Need Help?** Check [BUILD.md](BUILD.md) or create an issue on GitHub.
