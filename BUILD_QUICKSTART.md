# Build System Quick Start

Quick reference for building and releasing Alarmify.

## Prerequisites

```powershell
# Install Python dependencies
pip install -r requirements.txt
pip install pyinstaller

# Install Inno Setup (Windows installer creator)
# Download from: https://jrsoftware.org/isdl.php
```

## Common Commands

### Development

```powershell
# Run application
python main.py

# Run tests
python -m pytest tests/ -v

# Run build tests
python -m pytest tests/test_build.py -v
```

### Building

```powershell
# Build executable only (fast)
python build_installer.py --skip-inno

# Build executable and installer (full)
python build_installer.py

# Build without tests (faster)
python build_installer.py --skip-tests
```

### Versioning

```powershell
# Check current version
python version_manager.py --get

# Set version
python version_manager.py --set 1.2.3

# Bump version
python version_manager.py --bump patch   # 1.0.0 -> 1.0.1
python version_manager.py --bump minor   # 1.0.0 -> 1.1.0
python version_manager.py --bump major   # 1.0.0 -> 2.0.0
```

### Releasing

```powershell
# 1. Update version
python version_manager.py --bump patch

# 2. Commit
git add installer.iss version_info.txt
git commit -m "Bump version to 1.0.1"
git push

# 3. Tag and push
git tag v1.0.1
git push origin v1.0.1

# GitHub Actions will automatically:
# - Build executable and installer
# - Run tests
# - Create GitHub release
```

## File Structure

```
alarmify/
├── .github/
│   └── workflows/
│       └── build.yml           # CI/CD pipeline
├── tests/
│   └── test_build.py           # Build verification tests
├── alarmify.spec               # PyInstaller config
├── installer.iss               # Inno Setup script
├── build_installer.py          # Build orchestration
├── version_manager.py          # Version management
├── BUILD.md                    # Full build documentation
├── RELEASE.md                  # Release process guide
└── code_signing_config.md      # Code signing setup
```

## Build Outputs

```
dist/
└── Alarmify.exe               # Standalone executable (~50-100 MB)

Output/
└── AlarmifySetup-1.0.0.exe    # Windows installer (~50-100 MB)
```

## Troubleshooting

### Build fails

```powershell
# Clean and rebuild
Remove-Item -Recurse -Force build, dist, Output
python build_installer.py
```

### Inno Setup not found

- Install from https://jrsoftware.org/isdl.php
- Or build executable only: `python build_installer.py --skip-inno`

### Tests fail

```powershell
# Run tests with details
python -m pytest tests/ -v --tb=short
```

### Executable won't run

```powershell
# Build with console to see errors
# Edit alarmify.spec: console=True
python -m PyInstaller alarmify.spec
.\dist\Alarmify.exe
```

## Code Signing (Optional)

See [code_signing_config.md](code_signing_config.md) for complete setup.

Quick steps:
1. Obtain code signing certificate
2. Update `build_installer.py` (uncomment signing code)
3. Update `installer.iss` (uncomment SignTool config)
4. For CI: Add GitHub secrets (CERT_BASE64, CERT_PASSWORD)

## CI/CD Pipeline

GitHub Actions automatically:
- ✅ Runs on push to main/develop
- ✅ Runs on pull requests
- ✅ Builds on version tags (v*.*.*)
- ✅ Runs all tests
- ✅ Creates executable and installer
- ✅ Runs smoke tests
- ✅ Creates GitHub release (on tags)
- ✅ Uploads artifacts

View workflow: `.github/workflows/build.yml`

## Documentation

- **BUILD.md** - Complete build documentation
- **RELEASE.md** - Release process guide
- **CONTRIBUTING.md** - Contribution guidelines
- **code_signing_config.md** - Code signing setup
- **BUILD_QUICKSTART.md** - This file

## Support

- Check documentation first
- Search GitHub issues
- Review GitHub Actions logs
- Create new issue with details

---

**Quick Links:**
- [Full Build Guide](BUILD.md)
- [Release Process](RELEASE.md)
- [Code Signing](code_signing_config.md)
- [Contributing](CONTRIBUTING.md)
