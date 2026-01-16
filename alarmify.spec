# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Alarmify

This file configures how PyInstaller builds the executable.
Run with: python -m PyInstaller alarmify.spec
"""

import sys
from pathlib import Path

# Get the base path
block_cipher = None

# Check if version info file exists
version_file_path = Path('version_info.txt')
version_file = str(version_file_path) if version_file_path.exists() else None

# Analysis: Collect all Python files and dependencies
a = Analysis(
    ['main.py'],                    # Entry point script
    pathex=[],                       # Additional paths to search
    binaries=[],                     # Binary files to include
    datas=[
        ('spotify_style.qss', '.'),  # Include stylesheet in root
        ('Logo First Draft.png', '.'),  # Include logo
        ('README.md', '.'),          # Include README
        ('LICENSE', '.'),            # Include license
        ('cloud_sync', 'cloud_sync'),  # Include cloud_sync module
    ],
    hiddenimports=[
        'PyQt5.sip',                 # Required by PyQt5
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'spotipy',                   # Spotify API
        'spotipy.oauth2',
        'dotenv',                    # Environment loading
        'requests',                  # HTTP requests
        'schedule',                  # Scheduling library
        'urllib3',                   # HTTP library
        'certifi',                   # SSL certificates
        'logging_config',            # Centralized logging configuration
        'device_wake_manager',       # Device wake and reliability management
        'cloud_sync',                # Cloud sync module
        'cloud_sync.cloud_auth',     # Cloud authentication
        'cloud_sync.cloud_sync_api', # Cloud sync API
        'cloud_sync.cloud_sync_manager',  # Cloud sync manager
        'cloud_sync.sync_conflict_resolver',  # Sync conflict resolution
    ],
    hookspath=[],                    # Custom hooks directory
    hooksconfig={},                  # Hook configuration
    runtime_hooks=[],                # Runtime hooks
    excludes=[
        'pytest',                    # Don't include test framework
        'unittest',
        'test',
    ],
    noarchive=False,                 # Archive Python files
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

# PYZ: Create Python archive
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# EXE: Create executable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Alarmify',                 # Output executable name
    debug=False,                     # Disable debug mode
    bootloader_ignore_signals=False,
    strip=False,                     # Don't strip symbols
    upx=True,                        # Compress with UPX if available
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,                   # Hide console window (GUI app)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,          # TODO: Add code signing identity
    entitlements_file=None,
    icon='Logo First Draft.png',     # Application icon
    version_file=version_file,       # Version info from version_info.txt
)
