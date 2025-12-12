"""
version_manager.py - Version management utility for Alarmify

This script manages version information across multiple files:
- installer.iss (Inno Setup)
- alarmify.spec (PyInstaller)
- Version info file for Windows executable

Usage:
    python version_manager.py --get                    # Get current version
    python version_manager.py --set 1.2.3              # Set version
    python version_manager.py --bump major|minor|patch # Bump version
"""

import argparse
import re
import sys
from pathlib import Path
from datetime import datetime


class VersionManager:
    """Manage version information across project files."""
    
    def __init__(self, project_dir=None):
        """
        Initialize version manager.
        
        Args:
            project_dir: Root directory of project (default: script location)
        """
        self.project_dir = Path(project_dir or __file__).parent.resolve()
        self.iss_file = self.project_dir / "installer.iss"
        self.spec_file = self.project_dir / "alarmify.spec"
    
    def get_version_from_iss(self):
        """
        Extract version from installer.iss file.
        
        Returns:
            Version string (e.g., "1.0.0") or None if not found
        """
        if not self.iss_file.exists():
            return None
        
        content = self.iss_file.read_text(encoding='utf-8')
        match = re.search(r'#define MyAppVersion "([^"]+)"', content)
        return match.group(1) if match else None
    
    def set_version_in_iss(self, version):
        """
        Update version in installer.iss file.
        
        Args:
            version: Version string (e.g., "1.0.0")
        """
        if not self.iss_file.exists():
            print(f"Warning: {self.iss_file} not found")
            return False
        
        content = self.iss_file.read_text(encoding='utf-8')
        new_content = re.sub(
            r'#define MyAppVersion "[^"]+"',
            f'#define MyAppVersion "{version}"',
            content
        )
        self.iss_file.write_text(new_content, encoding='utf-8')
        return True
    
    def parse_version(self, version_str):
        """
        Parse version string into components.
        
        Args:
            version_str: Version string (e.g., "1.2.3")
            
        Returns:
            Tuple of (major, minor, patch) or None if invalid
        """
        match = re.match(r'^(\d+)\.(\d+)\.(\d+)', version_str)
        if match:
            return tuple(map(int, match.groups()))
        return None
    
    def format_version(self, major, minor, patch):
        """
        Format version components into string.
        
        Args:
            major, minor, patch: Version components
            
        Returns:
            Formatted version string
        """
        return f"{major}.{minor}.{patch}"
    
    def bump_version(self, part='patch'):
        """
        Increment version number.
        
        Args:
            part: Which part to bump ('major', 'minor', or 'patch')
            
        Returns:
            New version string or None if failed
        """
        current = self.get_version_from_iss()
        if not current:
            print("Error: Could not get current version")
            return None
        
        parts = self.parse_version(current)
        if not parts:
            print(f"Error: Invalid version format: {current}")
            return None
        
        major, minor, patch = parts
        
        if part == 'major':
            major += 1
            minor = 0
            patch = 0
        elif part == 'minor':
            minor += 1
            patch = 0
        elif part == 'patch':
            patch += 1
        else:
            print(f"Error: Invalid part '{part}'. Use major, minor, or patch")
            return None
        
        new_version = self.format_version(major, minor, patch)
        self.set_version_in_iss(new_version)
        return new_version
    
    def create_version_info_file(self, version=None):
        """
        Create Windows version info file for PyInstaller.
        
        Args:
            version: Version string (default: current version)
            
        Returns:
            Path to created file or None if failed
        """
        if not version:
            version = self.get_version_from_iss()
        
        if not version:
            print("Error: No version available")
            return None
        
        parts = self.parse_version(version)
        if not parts:
            print(f"Error: Invalid version format: {version}")
            return None
        
        major, minor, patch = parts
        
        # Create version info content
        content = f'''# UTF-8
#
# Version info for Alarmify executable
#

VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({major}, {minor}, {patch}, 0),
    prodvers=({major}, {minor}, {patch}, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'Alarmify Team'),
        StringStruct(u'FileDescription', u'Alarmify - Spotify Alarm Clock'),
        StringStruct(u'FileVersion', u'{version}.0'),
        StringStruct(u'InternalName', u'Alarmify'),
        StringStruct(u'LegalCopyright', u'Copyright © {datetime.now().year} Alarmify Team'),
        StringStruct(u'OriginalFilename', u'Alarmify.exe'),
        StringStruct(u'ProductName', u'Alarmify'),
        StringStruct(u'ProductVersion', u'{version}.0')])
      ]
    ),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
'''
        
        # Write to file
        version_file = self.project_dir / "version_info.txt"
        version_file.write_text(content, encoding='utf-8')
        
        print(f"Created version info file: {version_file}")
        return version_file


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Manage Alarmify version information"
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--get',
        action='store_true',
        help='Get current version'
    )
    group.add_argument(
        '--set',
        metavar='VERSION',
        help='Set version (e.g., 1.2.3)'
    )
    group.add_argument(
        '--bump',
        choices=['major', 'minor', 'patch'],
        help='Bump version component'
    )
    group.add_argument(
        '--create-info',
        action='store_true',
        help='Create version info file for PyInstaller'
    )
    
    args = parser.parse_args()
    
    manager = VersionManager()
    
    if args.get:
        version = manager.get_version_from_iss()
        if version:
            print(version)
        else:
            print("Error: Version not found", file=sys.stderr)
            sys.exit(1)
    
    elif args.set:
        version = args.set
        parts = manager.parse_version(version)
        if not parts:
            print(f"Error: Invalid version format '{version}'", file=sys.stderr)
            print("Use format: major.minor.patch (e.g., 1.2.3)", file=sys.stderr)
            sys.exit(1)
        
        if manager.set_version_in_iss(version):
            print(f"Version updated to {version}")
            manager.create_version_info_file(version)
        else:
            print("Error: Failed to update version", file=sys.stderr)
            sys.exit(1)
    
    elif args.bump:
        new_version = manager.bump_version(args.bump)
        if new_version:
            print(f"Version bumped to {new_version}")
            manager.create_version_info_file(new_version)
        else:
            sys.exit(1)
    
    elif args.create_info:
        version_file = manager.create_version_info_file()
        if not version_file:
            sys.exit(1)


if __name__ == "__main__":
    main()
