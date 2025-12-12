# Build System Documentation

This document provides an overview of the Alarmify build and installer system.

## Overview

The Alarmify build system provides:
- **Automated executable creation** using PyInstaller
- **Windows installer** with Inno Setup
- **Build verification** with automated smoke tests
- **Version management** across all build files
- **CI/CD pipeline** with GitHub Actions
- **Code signing placeholders** for future implementation
- **Automated releases** on version tags

## Files Created/Updated

### Build Configuration

| File | Purpose |
|------|---------|
| `alarmify.spec` | PyInstaller specification - defines how executable is built |
| `installer.iss` | Inno Setup script - creates Windows installer with shortcuts |
| `build_installer.py` | Build orchestration - runs PyInstaller and Inno Setup sequentially |
| `version_manager.py` | Version management utility - updates version across files |
| `verify_build_env.py` | Environment verification - checks build prerequisites |

### CI/CD

| File | Purpose |
|------|---------|
| `.github/workflows/build.yml` | GitHub Actions workflow - automated builds and releases |
| `.github/RELEASE_TEMPLATE.md` | Release notes template for creating releases |

### Documentation

| File | Purpose |
|------|---------|
| `BUILD.md` | Complete build system documentation |
| `RELEASE.md` | Release process guide with step-by-step instructions |
| `CONTRIBUTING.md` | Contribution guidelines including build system info |
| `code_signing_config.md` | Code signing setup guide |
| `BUILD_QUICKSTART.md` | Quick reference for common build tasks |
| `BUILD_SYSTEM_README.md` | This file - build system overview |
| `AGENTS.md` | Updated with build system commands |

### Tests

| File | Purpose |
|------|---------|
| `tests/test_build.py` | Build verification tests - validates build outputs |

### Configuration

| File | Purpose |
|------|---------|
| `.gitignore` | Updated to ignore build artifacts and outputs |

## Quick Start

### Prerequisites

1. **Python 3.10+** with pip
2. **PyInstaller** - `pip install pyinstaller`
3. **Inno Setup 6** - Download from https://jrsoftware.org/isdl.php

### Verify Environment

```powershell
python verify_build_env.py
```

This checks:
- Python version
- Required packages
- Project structure
- Inno Setup installation
- Available disk space

### Build Executable

```powershell
# Build standalone executable
python build_installer.py --skip-inno

# Output: dist/Alarmify.exe
```

### Build Installer

```powershell
# Build complete installer (requires Inno Setup)
python build_installer.py

# Outputs:
# - dist/Alarmify.exe (standalone executable)
# - Output/AlarmifySetup-1.0.0.exe (installer)
```

### Run Tests

```powershell
# Run all tests including build tests
python -m pytest tests/ -v

# Run only build verification tests
python -m pytest tests/test_build.py -v
```

## Build Process

The build system follows these stages:

1. **Clean** - Remove previous build artifacts
2. **PyInstaller** - Create standalone executable
3. **Smoke Tests** - Verify executable validity
4. **Inno Setup** - Create Windows installer
5. **Verification** - Final checks and summary

### Stage Details

#### 1. Clean (build_installer.py)
- Removes `build/`, `dist/`, `Output/` directories
- Ensures fresh build environment

#### 2. PyInstaller (alarmify.spec)
- Analyzes dependencies from `main.py`
- Bundles Python interpreter and packages
- Includes assets (logo, stylesheet, README, LICENSE)
- Creates single-file executable
- Applies UPX compression
- Size: ~50-100 MB

#### 3. Smoke Tests (build_installer.py)
- Executable exists and is readable
- Size is reasonable (> 10 MB)
- Valid PE (Windows executable) header
- 64-bit architecture verification

#### 4. Inno Setup (installer.iss)
- Packages executable with metadata
- Creates Start Menu shortcuts
- Adds uninstaller
- Configures optional auto-start
- Sets up registry entries
- Creates desktop shortcut (optional)

#### 5. Verification (build_installer.py)
- Displays file paths and sizes
- Shows timestamps
- Generates checksums
- Prints summary

## Version Management

### Current Version

```powershell
python version_manager.py --get
```

### Set Version

```powershell
python version_manager.py --set 1.2.3
```

### Bump Version

```powershell
# Patch release (1.0.0 -> 1.0.1)
python version_manager.py --bump patch

# Minor release (1.0.0 -> 1.1.0)
python version_manager.py --bump minor

# Major release (1.0.0 -> 2.0.0)
python version_manager.py --bump major
```

Version is updated in:
- `installer.iss` - Inno Setup script
- `version_info.txt` - Windows version resource (created)

## CI/CD Pipeline

### GitHub Actions Workflow

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Version tags matching `v*.*.*` pattern
- Manual workflow dispatch

**Jobs:**

1. **build** - Build executable and installer
   - Setup Python 3.10
   - Install dependencies
   - Run tests
   - Install Inno Setup
   - Build executable with PyInstaller
   - Build installer with Inno Setup
   - Create checksums
   - Upload artifacts

2. **release** - Create GitHub release (tags only)
   - Download build artifacts
   - Extract version from tag
   - Generate release notes
   - Create GitHub release
   - Attach installer and checksums

3. **smoke-test** - Verify build quality
   - Download executable artifact
   - Run smoke tests
   - Validate PE structure

### Creating a Release

```powershell
# 1. Update version
python version_manager.py --set 1.2.3

# 2. Commit changes
git add installer.iss version_info.txt
git commit -m "Bump version to 1.2.3"
git push origin main

# 3. Create and push tag
git tag v1.2.3
git push origin v1.2.3

# GitHub Actions automatically builds and releases
```

## Code Signing

Code signing is configured but disabled by default.

### Setup Code Signing

1. **Obtain Certificate**
   - Purchase from CA (DigiCert, Sectigo, etc.)
   - Cost: ~$100-500/year

2. **Local Setup**
   - Store certificate securely
   - Update `build_installer.py` (uncomment signing code)
   - Update `installer.iss` (uncomment SignTool config)

3. **GitHub Actions Setup**
   - Convert certificate to Base64
   - Add GitHub secrets: `CERT_BASE64`, `CERT_PASSWORD`
   - Enable signing steps in workflow (change `if: false` to `if: true`)

See [code_signing_config.md](code_signing_config.md) for complete instructions.

## Build Outputs

### Executable (dist/Alarmify.exe)

- **Type:** Standalone Windows executable
- **Size:** ~50-100 MB
- **Architecture:** 64-bit (x64)
- **Console:** Hidden (GUI app)
- **Compression:** UPX enabled
- **Usage:** Run directly, no installation needed

### Installer (Output/AlarmifySetup-*.exe)

- **Type:** Inno Setup installer
- **Size:** ~50-100 MB
- **Features:**
  - Start Menu shortcuts
  - Desktop shortcut (optional)
  - Auto-start option (optional)
  - Uninstaller
  - Registry entries
  - File associations (future)

### Artifacts (GitHub Actions)

- `Alarmify-Executable` - Standalone executable
- `Alarmify-Installer` - Windows installer
- `Checksums` - SHA256 checksums

## Build Customization

### Add Data Files

Edit `alarmify.spec`:
```python
datas=[
    ('spotify_style.qss', '.'),
    ('new_file.txt', '.'),  # Add your file
],
```

### Add Dependencies

Edit `alarmify.spec`:
```python
hiddenimports=[
    'PyQt5.sip',
    'new_package',  # Add your package
],
```

### Change Installer Options

Edit `installer.iss`:
- App info: `[Setup]` section
- Files: `[Files]` section
- Shortcuts: `[Icons]` section
- Tasks: `[Tasks]` section
- Registry: `[Registry]` section

### Modify Build Process

Edit `build_installer.py`:
- Add new stages
- Customize verification
- Integrate additional tools

## Troubleshooting

### Build Fails

```powershell
# Clean everything
Remove-Item -Recurse -Force build, dist, Output

# Verify environment
python verify_build_env.py

# Rebuild
python build_installer.py
```

### Missing Dependencies

```powershell
# Reinstall packages
pip install -r requirements.txt
pip install pyinstaller pytest
```

### Inno Setup Not Found

- Install from https://jrsoftware.org/isdl.php
- Or build without installer: `python build_installer.py --skip-inno`

### Tests Fail

```powershell
# Run with verbose output
python -m pytest tests/ -v --tb=short

# Run specific test
python -m pytest tests/test_build.py -v
```

## Documentation Structure

```
├── BUILD_SYSTEM_README.md      # This file - overview
├── BUILD_QUICKSTART.md         # Quick reference
├── BUILD.md                    # Complete build guide
├── RELEASE.md                  # Release process
├── CONTRIBUTING.md             # Contribution guidelines
└── code_signing_config.md      # Code signing setup
```

**For Developers:**
- Start with BUILD_QUICKSTART.md
- Reference BUILD.md for details
- Follow CONTRIBUTING.md for contributions

**For Releases:**
- Follow RELEASE.md step-by-step
- Use version_manager.py for versions

**For CI/CD:**
- Check .github/workflows/build.yml
- Review GitHub Actions logs

## Support

### Getting Help

1. **Check Documentation**
   - BUILD.md - Complete build guide
   - RELEASE.md - Release process
   - code_signing_config.md - Signing setup

2. **Verify Environment**
   ```powershell
   python verify_build_env.py
   ```

3. **Check Logs**
   - Local: Console output
   - CI: GitHub Actions logs

4. **Search Issues**
   - GitHub Issues tab
   - Look for similar problems

5. **Create Issue**
   - Provide error messages
   - Include environment details
   - Attach logs if possible

### Common Issues

| Issue | Solution |
|-------|----------|
| Module not found | Add to `hiddenimports` in alarmify.spec |
| Data file missing | Add to `datas` in alarmify.spec |
| Inno Setup not found | Install from jrsoftware.org or use --skip-inno |
| Tests fail | Run pytest with -v flag for details |
| Build too slow | Use --skip-tests during development |

## Best Practices

1. **Version Control**
   - Commit before building
   - Tag releases properly (v1.2.3)
   - Use semantic versioning

2. **Testing**
   - Run tests before building
   - Test built executable
   - Verify installer on clean system

3. **Documentation**
   - Update version in docs
   - Keep CHANGELOG current
   - Document breaking changes

4. **Releases**
   - Follow RELEASE.md process
   - Test release thoroughly
   - Generate clear release notes

5. **CI/CD**
   - Monitor GitHub Actions
   - Fix failures promptly
   - Keep workflows updated

## Future Enhancements

Potential improvements:
- [ ] Automatic CHANGELOG generation
- [ ] Multi-platform builds (macOS, Linux)
- [ ] Delta updates for installers
- [ ] Crash reporting integration
- [ ] Automated update checks
- [ ] Build time optimization
- [ ] Package signing automation
- [ ] Installer themes

## License

This build system is part of Alarmify and follows the same license.

---

**Quick Links:**
- [Build Quick Start](BUILD_QUICKSTART.md)
- [Complete Build Guide](BUILD.md)
- [Release Process](RELEASE.md)
- [Contributing](CONTRIBUTING.md)
- [Code Signing](code_signing_config.md)
