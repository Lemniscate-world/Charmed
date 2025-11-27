"""
build_installer.py - Build script for Alarmify Windows installer

This script automates the build process using PyInstaller.
It creates a single executable file that includes all dependencies.

Usage:
    python build_installer.py

Output:
    dist/Alarmify.exe - Standalone Windows executable
"""

import subprocess  # Run external commands
import sys         # System-specific parameters
import shutil      # File operations
from pathlib import Path  # Path manipulation


def main():
    """Build the Alarmify Windows executable."""
    
    print("=" * 50)
    print("Building Alarmify Windows Installer")
    print("=" * 50)
    
    # Get script directory (where build_installer.py is located)
    script_dir = Path(__file__).parent.resolve()
    
    # Step 1: Clean previous build artifacts
    print("\n[1/3] Cleaning previous builds...")
    build_dir = script_dir / "build"
    dist_dir = script_dir / "dist"
    
    if build_dir.exists():
        shutil.rmtree(build_dir)
        print(f"  Removed: {build_dir}")
    
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
        print(f"  Removed: {dist_dir}")
    
    # Step 2: Run PyInstaller
    print("\n[2/3] Running PyInstaller...")
    spec_file = script_dir / "alarmify.spec"
    
    result = subprocess.run(
        [sys.executable, "-m", "PyInstaller", str(spec_file)],
        cwd=str(script_dir),
        capture_output=False  # Show output in real-time
    )
    
    if result.returncode != 0:
        print("\n[ERROR] PyInstaller failed!")
        sys.exit(1)
    
    # Step 3: Verify output
    print("\n[3/3] Verifying build...")
    exe_path = dist_dir / "Alarmify.exe"
    
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"  Success! Created: {exe_path}")
        print(f"  Size: {size_mb:.2f} MB")
    else:
        print("\n[ERROR] Executable not found!")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("Build complete!")
    print(f"Installer: {exe_path}")
    print("=" * 50)


if __name__ == "__main__":
    main()

