# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Alarmify

This file configures how PyInstaller builds the executable.
Run with: python -m PyInstaller alarmify.spec
"""

# Analysis: Collect all Python files and dependencies
a = Analysis(
    ['main.py'],                    # Entry point script
    pathex=[],                       # Additional paths to search
    binaries=[],                     # Binary files to include
    datas=[
        ('spotify_style.qss', '.'),  # Include stylesheet in root
        ('Logo First Draft.png', '.'),  # Include logo
    ],
    hiddenimports=[
        'PyQt5.sip',                 # Required by PyQt5
        'spotipy',                   # Spotify API
        'dotenv',                    # Environment loading
        'requests',                  # HTTP requests
    ],
    hookspath=[],                    # Custom hooks directory
    hooksconfig={},                  # Hook configuration
    runtime_hooks=[],                # Runtime hooks
    excludes=[],                     # Modules to exclude
    noarchive=False,                 # Archive Python files
)

# PYZ: Create Python archive
pyz = PYZ(a.pure)

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
    codesign_identity=None,
    entitlements_file=None,
    icon='Logo First Draft.png',     # Application icon
)

