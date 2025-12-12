# Release Process

This document describes how to create and publish releases for Alarmify.

## Quick Release Checklist

- [ ] All tests pass locally
- [ ] Version number updated
- [ ] CHANGELOG updated (if exists)
- [ ] Commit and push changes
- [ ] Create and push version tag
- [ ] Verify GitHub Actions build
- [ ] Test downloaded installer
- [ ] Announce release

## Detailed Release Steps

### 1. Prepare Release

#### Update Version Number

```powershell
# Bump version (automatically updates installer.iss)
python version_manager.py --bump patch  # or minor/major

# Or set specific version
python version_manager.py --set 1.2.3

# Verify version
python version_manager.py --get
```

#### Update Documentation

Update any version references in:
- `README.md` (if version mentioned)
- `CHANGELOG.md` (add release notes)
- Documentation files

#### Run Tests

```powershell
# Run all tests
python -m pytest tests/ -v

# Should show all passing
```

### 2. Commit Changes

```powershell
# Stage version changes
git add installer.iss version_info.txt

# Stage any documentation updates
git add README.md CHANGELOG.md

# Commit with descriptive message
git commit -m "Bump version to 1.2.3"

# Push to main branch
git push origin main
```

### 3. Create Release Tag

```powershell
# Create annotated tag
git tag -a v1.2.3 -m "Release version 1.2.3"

# Or lightweight tag
git tag v1.2.3

# Push tag to trigger CI/CD
git push origin v1.2.3
```

**Tag Format:** `v{major}.{minor}.{patch}` (e.g., `v1.2.3`)

### 4. Monitor GitHub Actions

1. Go to repository on GitHub
2. Click "Actions" tab
3. Watch "Build and Release" workflow
4. Verify all jobs pass:
   - ✓ build (creates executable and installer)
   - ✓ smoke-test (validates build)
   - ✓ release (creates GitHub release)

**Build takes approximately 10-15 minutes**

### 5. Verify Release

#### On GitHub

1. Go to "Releases" section
2. Find your new release
3. Verify:
   - Release title and version
   - Release notes generated
   - Installer attached (`AlarmifySetup-1.2.3.exe`)
   - Checksums file attached

#### Test Installer

1. Download installer from release
2. Verify checksum:
   ```powershell
   Get-FileHash AlarmifySetup-1.2.3.exe -Algorithm SHA256
   # Compare with checksums.txt
   ```
3. Run installer on test machine
4. Verify installation:
   - Start Menu shortcut created
   - Application launches successfully
   - Basic functionality works

### 6. Announce Release

- Post release notes on project website/blog
- Announce on social media
- Notify users via email/newsletter
- Update download links

## Release Types

### Patch Release (1.0.0 → 1.0.1)

Bug fixes and minor improvements.

```powershell
python version_manager.py --bump patch
```

**When to use:**
- Bug fixes
- Security patches
- Documentation updates
- Performance improvements

### Minor Release (1.0.0 → 1.1.0)

New features, backward compatible.

```powershell
python version_manager.py --bump minor
```

**When to use:**
- New features
- Enhancements to existing features
- Non-breaking API changes
- Deprecations (with warnings)

### Major Release (1.0.0 → 2.0.0)

Breaking changes or significant updates.

```powershell
python version_manager.py --bump major
```

**When to use:**
- Breaking changes
- Major redesigns
- Removing deprecated features
- Significant architecture changes

## Pre-release Versions

For testing before official release:

```powershell
# Set pre-release version
python version_manager.py --set 1.2.3-rc1

# Or for development builds
python version_manager.py --set 1.2.3-dev
```

**Formats:**
- Release candidate: `1.2.3-rc1`, `1.2.3-rc2`
- Beta: `1.2.3-beta1`
- Alpha: `1.2.3-alpha1`
- Development: `1.2.3-dev`

Pre-releases are marked as "Pre-release" on GitHub automatically.

## Hotfix Release

For urgent fixes to production:

1. **Create hotfix branch:**
   ```powershell
   git checkout main
   git checkout -b hotfix/1.0.1
   ```

2. **Make fixes:**
   ```powershell
   # Fix the issue
   # Update tests
   python -m pytest tests/ -v
   ```

3. **Bump version:**
   ```powershell
   python version_manager.py --bump patch
   git add installer.iss version_info.txt
   git commit -m "Hotfix: Fix critical bug"
   ```

4. **Merge and release:**
   ```powershell
   git checkout main
   git merge hotfix/1.0.1
   git push origin main
   
   # Create tag
   git tag v1.0.1
   git push origin v1.0.1
   ```

## Manual Release (Without Tag)

If you need to create a release manually:

1. Go to GitHub repository
2. Click "Actions" tab
3. Select "Build and Release" workflow
4. Click "Run workflow" button
5. Select branch
6. Check "Create a release"
7. Click "Run workflow"

**Note:** This creates a development release, not a production release.

## Rolling Back a Release

If you need to remove a bad release:

1. **Delete GitHub release:**
   - Go to Releases page
   - Click edit on the release
   - Scroll down and click "Delete this release"

2. **Delete tag:**
   ```powershell
   # Delete local tag
   git tag -d v1.2.3
   
   # Delete remote tag
   git push origin :refs/tags/v1.2.3
   ```

3. **Revert version:**
   ```powershell
   # Set back to previous version
   python version_manager.py --set 1.2.2
   
   git add installer.iss version_info.txt
   git commit -m "Revert version to 1.2.2"
   git push origin main
   ```

## Troubleshooting

### Build Fails on CI

**Check Actions log:**
1. Go to Actions tab
2. Click on failed workflow
3. Click on failed job
4. Review error messages

**Common issues:**
- Tests failing: Fix tests and re-tag
- PyInstaller errors: Check `alarmify.spec`
- Inno Setup errors: Check `installer.iss`

**Fix and re-release:**
```powershell
# Delete bad tag
git tag -d v1.2.3
git push origin :refs/tags/v1.2.3

# Fix issues and re-commit
git add .
git commit -m "Fix build issues"
git push origin main

# Re-create tag
git tag v1.2.3
git push origin v1.2.3
```

### Release Not Created

**Check workflow permissions:**
- Settings → Actions → General
- Workflow permissions: "Read and write permissions"

**Manually create release:**
1. Download artifacts from Actions
2. Go to Releases → "Draft a new release"
3. Choose tag
4. Upload artifacts manually

### Version Conflicts

**If version is already released:**
```powershell
# Bump to next version
python version_manager.py --bump patch

# Or increment manually
python version_manager.py --set 1.2.4
```

## Best Practices

### Semantic Versioning

Follow [semver.org](https://semver.org/):
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes (backward compatible)

### Release Frequency

- **Patch releases:** As needed for bugs
- **Minor releases:** Monthly or when features ready
- **Major releases:** Yearly or for major changes

### Testing Before Release

Always test:
- All unit tests pass
- Manual smoke testing
- Installation on clean system
- Upgrade from previous version

### Release Notes

Include in release notes:
- New features
- Bug fixes
- Known issues
- Breaking changes (for major releases)
- Migration guide (if needed)

### Versioning Strategy

For development:
```
1.0.0-dev → 1.0.0-beta1 → 1.0.0-rc1 → 1.0.0
```

For production:
```
1.0.0 → 1.0.1 → 1.1.0 → 2.0.0
```

## Automation

The release process is largely automated via GitHub Actions:

1. **Push tag** → Triggers build
2. **Build completes** → Creates artifacts
3. **Tests pass** → Creates release
4. **Release created** → Uploads artifacts

You only need to:
- Update version
- Commit changes
- Push tag

Everything else is automatic!

## Support

For questions about releases:
1. Check this documentation
2. Review GitHub Actions logs
3. Check existing releases for examples
4. Open an issue if problems persist
