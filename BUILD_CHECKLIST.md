# Build System Checklist

Use this checklist to verify the build system is working correctly.

## Initial Setup Checklist

### Prerequisites Installation

- [ ] Python 3.10+ installed
  ```powershell
  python --version
  ```

- [ ] Pip working
  ```powershell
  pip --version
  ```

- [ ] Virtual environment created (optional but recommended)
  ```powershell
  python -m venv .venv
  .venv\Scripts\Activate.ps1
  ```

- [ ] Dependencies installed
  ```powershell
  pip install -r requirements.txt
  pip install pyinstaller pytest
  ```

- [ ] Inno Setup 6 installed (for installer creation)
  - Download: https://jrsoftware.org/isdl.php
  - Install to default location

### Environment Verification

- [ ] Run environment verification
  ```powershell
  python verify_build_env.py
  ```

- [ ] All critical checks pass
  - [ ] Python version OK
  - [ ] Python packages OK
  - [ ] Project structure OK
  - [ ] Assets present OK

- [ ] Optional checks (can be warnings)
  - [ ] Virtual environment
  - [ ] Git installed
  - [ ] Inno Setup found
  - [ ] Sufficient disk space

## Build System Files Checklist

### Core Build Files

- [ ] `alarmify.spec` exists and is valid
  - [ ] Entry point is main.py
  - [ ] Assets included (logo, stylesheet, README, LICENSE)
  - [ ] Hidden imports configured
  - [ ] Console = False (GUI app)

- [ ] `installer.iss` exists and is valid
  - [ ] Version defined
  - [ ] App information complete
  - [ ] Files section includes executable
  - [ ] Icons/shortcuts configured
  - [ ] Registry entries defined

- [ ] `build_installer.py` exists and is executable
  - [ ] Has proper imports
  - [ ] Main function works
  - [ ] Command-line options work

- [ ] `version_manager.py` exists and is executable
  - [ ] Can get version
  - [ ] Can set version
  - [ ] Can bump version

- [ ] `verify_build_env.py` exists and is executable
  - [ ] Runs without errors
  - [ ] Produces readable output

### Documentation Files

- [ ] `BUILD.md` exists
- [ ] `BUILD_QUICKSTART.md` exists
- [ ] `BUILD_SYSTEM_README.md` exists
- [ ] `RELEASE.md` exists
- [ ] `CONTRIBUTING.md` exists
- [ ] `code_signing_config.md` exists
- [ ] `GET_STARTED_BUILDING.md` exists
- [ ] `IMPLEMENTATION_SUMMARY.md` exists
- [ ] `BUILD_CHECKLIST.md` exists (this file)

### CI/CD Files

- [ ] `.github/workflows/build.yml` exists
  - [ ] Valid YAML syntax
  - [ ] Three jobs defined (build, release, smoke-test)
  - [ ] Triggers configured
  - [ ] Secrets placeholders present

- [ ] `.github/RELEASE_TEMPLATE.md` exists

### Test Files

- [ ] `tests/test_build.py` exists
  - [ ] Valid Python syntax
  - [ ] Test classes defined
  - [ ] Can run with pytest

### Configuration Files

- [ ] `.gitignore` updated
  - [ ] build/ ignored
  - [ ] dist/ ignored
  - [ ] Output/ ignored
  - [ ] version_info.txt ignored

- [ ] `AGENTS.md` updated with build commands

## Functional Testing Checklist

### Local Build Testing

#### Test 1: Executable Build

- [ ] Clean previous builds
  ```powershell
  Remove-Item -Recurse -Force build, dist, Output -ErrorAction SilentlyContinue
  ```

- [ ] Build executable only
  ```powershell
  python build_installer.py --skip-inno
  ```

- [ ] Verify outputs:
  - [ ] `dist/Alarmify.exe` exists
  - [ ] Size > 10 MB
  - [ ] No errors during build

- [ ] Test executable
  - [ ] Runs without errors
  - [ ] UI appears correctly
  - [ ] No console window appears
  - [ ] Can access menus

#### Test 2: Full Build with Installer

- [ ] Clean previous builds
  ```powershell
  Remove-Item -Recurse -Force build, dist, Output -ErrorAction SilentlyContinue
  ```

- [ ] Build with installer
  ```powershell
  python build_installer.py
  ```

- [ ] Verify outputs:
  - [ ] `dist/Alarmify.exe` exists
  - [ ] `Output/AlarmifySetup-*.exe` exists
  - [ ] Checksums look correct
  - [ ] No errors during build

- [ ] Test installer
  - [ ] Installer runs
  - [ ] UI is professional
  - [ ] Can select install location
  - [ ] Can choose shortcuts
  - [ ] Can choose auto-start
  - [ ] Installation completes
  - [ ] Start Menu shortcuts created
  - [ ] Application launches from shortcut
  - [ ] Uninstaller works

#### Test 3: Build Options

- [ ] Build with --skip-tests
  ```powershell
  python build_installer.py --skip-tests --skip-inno
  ```
  - [ ] Runs faster (< 3 minutes)
  - [ ] Skips test stage
  - [ ] Produces valid executable

- [ ] Build with --skip-inno
  ```powershell
  python build_installer.py --skip-inno
  ```
  - [ ] Runs without Inno Setup
  - [ ] Produces executable only
  - [ ] No installer created

### Version Management Testing

- [ ] Get current version
  ```powershell
  python version_manager.py --get
  ```
  - [ ] Returns valid version (e.g., 1.0.0)

- [ ] Set version
  ```powershell
  python version_manager.py --set 1.2.3
  ```
  - [ ] Updates installer.iss
  - [ ] Creates version_info.txt

- [ ] Bump version (patch)
  ```powershell
  python version_manager.py --bump patch
  ```
  - [ ] Increments patch number
  - [ ] Updates files

- [ ] Bump version (minor)
  ```powershell
  python version_manager.py --bump minor
  ```
  - [ ] Increments minor, resets patch

- [ ] Bump version (major)
  ```powershell
  python version_manager.py --bump major
  ```
  - [ ] Increments major, resets minor and patch

### Test Suite Testing

- [ ] Run all tests
  ```powershell
  python -m pytest tests/ -v
  ```
  - [ ] All tests pass
  - [ ] No import errors

- [ ] Run build tests specifically
  ```powershell
  python -m pytest tests/test_build.py -v
  ```
  - [ ] All build tests pass
  - [ ] Proper skip messages for optional checks

- [ ] Run tests after building
  ```powershell
  python build_installer.py --skip-inno
  python -m pytest tests/test_build.py -v
  ```
  - [ ] More tests pass (executable exists)

## CI/CD Testing Checklist

### GitHub Actions Setup

- [ ] Repository on GitHub
- [ ] .github/workflows/build.yml committed
- [ ] Actions enabled in repository settings

### Workflow Permissions

- [ ] Go to Settings → Actions → General
- [ ] Workflow permissions set to "Read and write permissions"
- [ ] Allow GitHub Actions to create and approve pull requests

### Test Workflow Triggers

#### Test 1: Push to Main

- [ ] Make small change
- [ ] Commit and push to main
  ```powershell
  git add .
  git commit -m "Test CI/CD"
  git push origin main
  ```
- [ ] Check Actions tab
- [ ] Verify build job runs
- [ ] Verify smoke-test job runs
- [ ] Both jobs pass

#### Test 2: Pull Request

- [ ] Create feature branch
- [ ] Make change and push
- [ ] Create PR to main
- [ ] Verify build runs on PR
- [ ] Verify tests pass

#### Test 3: Version Tag (Release)

- [ ] Update version
  ```powershell
  python version_manager.py --set 1.0.0
  git add installer.iss version_info.txt
  git commit -m "Release v1.0.0"
  git push origin main
  ```

- [ ] Create and push tag
  ```powershell
  git tag v1.0.0
  git push origin v1.0.0
  ```

- [ ] Verify in Actions:
  - [ ] Build job runs
  - [ ] Smoke-test job runs
  - [ ] Release job runs

- [ ] Verify release created:
  - [ ] Go to Releases section
  - [ ] Release v1.0.0 exists
  - [ ] Release notes present
  - [ ] Installer attached
  - [ ] Checksums attached

- [ ] Test release:
  - [ ] Download installer
  - [ ] Verify checksum
  - [ ] Install and test

#### Test 4: Manual Trigger

- [ ] Go to Actions → Build and Release
- [ ] Click "Run workflow"
- [ ] Select branch
- [ ] Check "Create a release" (optional)
- [ ] Click "Run workflow"
- [ ] Verify workflow runs
- [ ] Check outputs

## Documentation Checklist

### Documentation Accuracy

- [ ] All file paths in docs are correct
- [ ] All commands in docs work
- [ ] Code examples are valid
- [ ] Links work (internal and external)

### Documentation Completeness

- [ ] BUILD.md covers all build aspects
- [ ] RELEASE.md covers release process
- [ ] CONTRIBUTING.md has contribution guidelines
- [ ] Code signing documented
- [ ] Quick reference available
- [ ] Troubleshooting sections present

### Documentation Accessibility

- [ ] README updated with build info
- [ ] Getting started guide available
- [ ] AGENTS.md updated
- [ ] Clear next steps for users

## Code Signing Checklist (Optional)

### Preparation

- [ ] Read code_signing_config.md
- [ ] Understand certificate requirements
- [ ] Know your Certificate Authority options
- [ ] Understand costs ($100-500/year)

### Local Setup (When Certificate Obtained)

- [ ] Certificate acquired
- [ ] Certificate imported to Windows
- [ ] SignTool installed (Windows SDK)
- [ ] Uncomment signing code in build_installer.py
- [ ] Test signing locally
- [ ] Verify signature

### GitHub Actions Setup (When Certificate Obtained)

- [ ] Convert certificate to Base64
- [ ] Add CERT_BASE64 secret
- [ ] Add CERT_PASSWORD secret
- [ ] Enable signing steps in workflow (if: true)
- [ ] Test signing in CI
- [ ] Verify signed artifacts

## Final Verification Checklist

### Before First Release

- [ ] All files committed to Git
- [ ] No sensitive data in repository
- [ ] .gitignore properly configured
- [ ] All documentation reviewed
- [ ] Local build works
- [ ] CI/CD build works
- [ ] Installer tested on clean system
- [ ] All tests pass

### Regular Maintenance

- [ ] Check for dependency updates monthly
- [ ] Review GitHub Actions usage
- [ ] Test on new Windows versions
- [ ] Update documentation as needed
- [ ] Monitor issues and discussions

## Troubleshooting Reference

### If Build Fails

1. Run: `python verify_build_env.py`
2. Check: Python version and packages
3. Clean: Remove build/, dist/, Output/
4. Retry: `python build_installer.py`
5. Check: Error messages carefully
6. Search: GitHub issues for similar problems

### If Tests Fail

1. Run: `python -m pytest tests/ -v --tb=short`
2. Check: Which tests fail
3. Verify: Test requirements met
4. Check: Test assumptions valid
5. Fix: Issues and re-run

### If CI/CD Fails

1. Check: GitHub Actions logs
2. Verify: Workflow syntax (YAML)
3. Check: Permissions settings
4. Verify: Secrets configured (if using)
5. Test: Locally first

## Success Criteria

All items checked = Build system fully functional! ✅

Minimum for basic usage:
- [ ] Local executable build works
- [ ] Tests pass
- [ ] Documentation accessible
- [ ] No critical errors

Minimum for releases:
- [ ] Full build works (with installer)
- [ ] Version management works
- [ ] CI/CD pipeline functional
- [ ] Release process tested

Minimum for production:
- [ ] All above items ✓
- [ ] Tested on clean systems
- [ ] Documentation complete
- [ ] Support resources ready

---

**Checklist Version**: 1.0  
**Last Updated**: December 12, 2025  
**Status**: Complete build system implementation
