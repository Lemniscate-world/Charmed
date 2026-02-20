# Build and Installer Guide

This document explains how to build Charmed from source and create installers.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Build Process](#build-process)
- [Build Scripts](#build-scripts)
- [Continuous Integration](#continuous-integration)
- [Code Signing](#code-signing)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software

1. **Python 3.10+**
   - Download from [python.org](https://www.python.org/downloads/)
   - Verify: `python --version`

2. **PyInstaller**
   - Installed via requirements: `pip install pyinstaller`
   - Used to create standalone executable

3. **Inno Setup 6** (for installer creation)
   - Download from [jrsoftware.org](https://jrsoftware.org/isdl.php)
   - Install to default location: `C:\Program Files (x86)\Inno Setup 6\`

### Optional Software

4. **Windows SDK** (for code signing)
   - Includes SignTool for code signing
   - Part of Visual Studio or standalone download

5. **Git** (for version control)
   - Download from [git-scm.com](https://git-scm.com/)

## Quick Start

### Build Executable Only

```powershell
# Setup environment
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install pyinstaller

# Build executable
python build_installer.py --skip-inno
```

Output: `dist/Charmed.exe`

### Build Complete Installer

```powershell
# Install Inno Setup first (see Prerequisites)

# Build everything
python build_installer.py
```

Output: 
- `dist/Charmed.exe` - Standalone executable
- `Output/CharmedSetup-1.0.0.exe` - Windows installer

## Build Process

The build process consists of 5 stages:

### Stage 1: Clean Build Artifacts

Removes previous build outputs:
- `build/` - PyInstaller build cache
- `dist/` - Executable output directory
- `Output/` - Installer output directory

### Stage 2: PyInstaller Build

Creates standalone executable using `charmed.spec`:

1. Analyzes `main.py` and dependencies
2. Collects Python modules and packages
3. Bundles assets (logo, stylesheet, README, LICENSE)
4. Creates single-file executable
5. Applies compression (UPX)

Configuration in `charmed.spec`:
- Entry point: `main.py`
- Icon: `Logo First Draft.png`
- Console: Hidden (GUI app)
- Architecture: Native (x64 on 64-bit Windows)

### Stage 3: Smoke Tests

Automated validation of built executable:

1. **Existence Check**: Verify file exists
2. **Size Check**: Ensure size > 10 MB
3. **PE Header Check**: Validate Windows executable format
4. **Dependency Check**: Verify all DLLs are bundled

Skip with: `python build_installer.py --skip-tests`

### Stage 4: Inno Setup Build

Creates Windows installer from executable:

1. Packages executable and assets
2. Creates Start Menu shortcuts
3. Adds uninstaller
4. Configures registry entries
5. Sets up auto-start option (user choice)

Configuration in `installer.iss`:
- App information and version
- Installation directory
- Shortcuts and icons
- Registry keys
- File associations (future)

Skip with: `python build_installer.py --skip-inno`

### Stage 5: Final Verification

Verifies all outputs and displays summary:
- File paths and sizes
- Modification timestamps
- Build statistics

## Build Scripts

### build_installer.py

Main build orchestration script.

**Usage:**
```powershell
python build_installer.py [options]
```

**Options:**
- `--skip-tests` - Skip smoke tests
- `--skip-inno` - Skip Inno Setup (executable only)

**Example:**
```powershell
# Full build with all stages
python build_installer.py

# Quick build without installer
python build_installer.py --skip-inno

# Build without running tests
python build_installer.py --skip-tests
```

### charmed.spec

PyInstaller specification file. Configures:
- Entry point and dependencies
- Data files to include
- Hidden imports
- Executable options

**Edit to:**
- Add new data files
- Include additional dependencies
- Change executable icon
- Modify compression settings

### installer.iss

Inno Setup script. Configures:
- Installer appearance and behavior
- File installation locations
- Shortcuts and registry entries
- Custom installation options

**Key Sections:**
- `[Setup]` - Basic installer configuration
- `[Files]` - Files to install
- `[Icons]` - Shortcuts to create
- `[Tasks]` - User-selectable options
- `[Registry]` - Registry modifications
- `[Code]` - Advanced logic (Pascal Script)

### version_manager.py

Version management utility.

**Usage:**
```powershell
# Get current version
python version_manager.py --get

# Set version
python version_manager.py --set 1.2.3

# Bump version
python version_manager.py --bump major  # 1.0.0 -> 2.0.0
python version_manager.py --bump minor  # 1.0.0 -> 1.1.0
python version_manager.py --bump patch  # 1.0.0 -> 1.0.1

# Create version info file
python version_manager.py --create-info
```

Updates version in:
- `installer.iss` - Inno Setup script
- `version_info.txt` - Windows version resource

## Continuous Integration

### GitHub Actions Workflow

File: `.github/workflows/build.yml`

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests
- Version tags (`v*.*.*`)
- Manual workflow dispatch

**Jobs:**

1. **build** - Build executable and installer
   - Setup Python environment
   - Install dependencies
   - Run tests
   - Build with PyInstaller
   - Create installer with Inno Setup
   - Generate checksums
   - Upload artifacts

2. **release** - Create GitHub release (tags only)
   - Download build artifacts
   - Generate release notes
   - Create GitHub release
   - Attach installer and checksums

3. **smoke-test** - Verify build quality
   - Download executable
   - Run automated smoke tests
   - Validate PE structure

### Creating a Release

1. **Update version:**
   ```powershell
   python version_manager.py --set 1.2.3
   git add installer.iss version_info.txt
   git commit -m "Bump version to 1.2.3"
   ```

2. **Create and push tag:**
   ```powershell
   git tag v1.2.3
   git push origin v1.2.3
   ```

3. **GitHub Actions will:**
   - Build executable and installer
   - Run tests
   - Create GitHub release
   - Upload release assets

### Manual Release

Trigger from GitHub:
1. Go to Actions tab
2. Select "Build and Release" workflow
3. Click "Run workflow"
4. Check "Create a release"
5. Click "Run workflow"

## Code Signing

See [code_signing_config.md](code_signing_config.md) for complete instructions.

**Quick Setup:**

1. **Obtain certificate** from CA (DigiCert, Sectigo, etc.)

2. **For local builds:**
   ```powershell
   # Import certificate
   Import-PfxCertificate -FilePath cert.pfx -CertStoreLocation Cert:\CurrentUser\My
   
   # Update build_installer.py (uncomment signing code)
   ```

3. **For GitHub Actions:**
   ```powershell
   # Convert to Base64
   [Convert]::ToBase64String([IO.File]::ReadAllBytes("cert.pfx")) | Out-File cert.txt
   
   # Add GitHub secrets:
   # - CERT_BASE64 (certificate content)
   # - CERT_PASSWORD (certificate password)
   ```

4. **Enable in workflow:**
   - Edit `.github/workflows/build.yml`
   - Change `if: false` to `if: true` for signing steps

## Troubleshooting

### PyInstaller Issues

**Error: Module not found**
- Add to `hiddenimports` in `charmed.spec`
- Example: `'PyQt5.sip'`

**Error: Data file not found**
- Add to `datas` in `charmed.spec`
- Example: `('Logo First Draft.png', '.')`

**Executable too large**
- Disable UPX: Set `upx=False` in `charmed.spec`
- Exclude unused modules in `excludes`

**Executable fails to run**
- Test with `console=True` to see error messages
- Check for missing DLLs with Dependency Walker

### Inno Setup Issues

**Error: ISCC.exe not found**
- Install Inno Setup
- Update path in `build_installer.py`

**Error: Source file not found**
- Ensure PyInstaller completed successfully
- Check paths in `installer.iss` match actual files

**Registry access denied**
- Run with administrator privileges
- Or change `PrivilegesRequired` in `installer.iss`

### Build Performance

**Slow build times**
- Use `--skip-tests` during development
- Enable PyInstaller cache (default)
- Use SSD for build directory

**Incremental builds**
- PyInstaller caches in `build/` directory
- Keep cache between builds for faster rebuilds
- Clean cache if issues occur

### GitHub Actions Issues

**Workflow fails on tests**
- Check test output in Actions logs
- Run tests locally first: `pytest tests/ -v`

**Installer not created**
- Verify Inno Setup installation in workflow
- Check `installer.iss` syntax

**Artifacts not uploaded**
- Check file paths in workflow
- Verify files exist after build

## Build Variants

### Debug Build

For debugging, enable console window:

1. Edit `charmed.spec`:
   ```python
   console=True,  # Change from False
   ```

2. Build:
   ```powershell
   python -m PyInstaller charmed.spec
   ```

### Development Build

Quick build without compression:

1. Edit `charmed.spec`:
   ```python
   upx=False,  # Disable compression
   ```

2. Build:
   ```powershell
   python build_installer.py --skip-tests --skip-inno
   ```

### Production Build

Full build with all optimizations:

```powershell
# Clean everything
Remove-Item -Recurse -Force build, dist, Output -ErrorAction SilentlyContinue

# Build with all stages
python build_installer.py
```

## Additional Resources

- [PyInstaller Documentation](https://pyinstaller.org/en/stable/)
- [Inno Setup Documentation](https://jrsoftware.org/ishelp/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Windows Code Signing](https://docs.microsoft.com/en-us/windows/win32/seccrypto/cryptography-tools)

## Support

For build issues:
1. Check this documentation
2. Review error messages carefully
3. Search existing GitHub issues
4. Create new issue with:
   - Build command used
   - Complete error output
   - System information (OS, Python version)
   - Build environment (local or CI)
