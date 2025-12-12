"""
build_installer.py - Build script for Alarmify Windows installer

This script automates the complete build process:
1. Cleans previous build artifacts
2. Runs PyInstaller to create executable
3. Runs automated smoke tests
4. Runs Inno Setup to create installer
5. Performs final build verification

Usage:
    python build_installer.py [--skip-tests] [--skip-inno]

Output:
    dist/Alarmify.exe - Standalone Windows executable
    Output/AlarmifySetup-*.exe - Windows installer
"""

import subprocess  # Run external commands
import sys         # System-specific parameters
import shutil      # File operations
import os          # Operating system interface
import argparse    # Command-line argument parsing
from pathlib import Path  # Path manipulation
import time        # Time utilities

# Try to import logging if available, fall back to print
try:
    from logging_config import setup_logging, get_logger
    setup_logging()
    logger = get_logger(__name__)
    HAS_LOGGING = True
except ImportError:
    HAS_LOGGING = False
    logger = None


def log_info(message):
    """Log info message using logger if available, otherwise print."""
    if HAS_LOGGING and logger:
        logger.info(message)
    else:
        print(message)


def log_debug(message):
    """Log debug message using logger if available, otherwise print."""
    if HAS_LOGGING and logger:
        logger.debug(message)
    else:
        print(f"[DEBUG] {message}")


def log_error(message, exc_info=False):
    """Log error message using logger if available, otherwise print."""
    if HAS_LOGGING and logger:
        logger.error(message, exc_info=exc_info)
    else:
        print(f"[ERROR] {message}")


def log_warning(message):
    """Log warning message using logger if available, otherwise print."""
    if HAS_LOGGING and logger:
        logger.warning(message)
    else:
        print(f"[WARNING] {message}")


def find_inno_setup():
    """
    Locate Inno Setup Compiler (ISCC.exe).
    
    Returns:
        Path to ISCC.exe or None if not found
    """
    # Common installation paths for Inno Setup
    common_paths = [
        Path(r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"),
        Path(r"C:\Program Files\Inno Setup 6\ISCC.exe"),
        Path(r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe"),
        Path(r"C:\Program Files\Inno Setup 5\ISCC.exe"),
    ]
    
    # Check common paths
    for path in common_paths:
        if path.exists():
            return path
    
    # Try to find in PATH
    try:
        result = subprocess.run(
            ["where", "ISCC.exe"],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            return Path(result.stdout.strip().split('\n')[0])
    except Exception:
        pass
    
    return None


def clean_build_artifacts(script_dir):
    """
    Remove previous build artifacts.
    
    Args:
        script_dir: Root directory of the project
    """
    log_info("\n[1/5] Cleaning previous builds...")
    
    directories_to_clean = [
        script_dir / "build",
        script_dir / "dist",
        script_dir / "Output",
    ]
    
    for directory in directories_to_clean:
        if directory.exists():
            try:
                shutil.rmtree(directory)
                log_info(f"  Removed: {directory}")
            except Exception as e:
                log_error(f"  Failed to remove {directory}: {e}", exc_info=True)
                sys.exit(1)
        else:
            log_debug(f"  Directory does not exist: {directory}")
    
    log_info("  Clean complete!")


def run_pyinstaller(script_dir):
    """
    Run PyInstaller to create the executable.
    
    Args:
        script_dir: Root directory of the project
        
    Returns:
        Path to the created executable
    """
    log_info("\n[2/5] Running PyInstaller...")
    spec_file = script_dir / "alarmify.spec"
    
    if not spec_file.exists():
        log_error(f"Spec file not found: {spec_file}")
        sys.exit(1)
    
    log_debug(f"Using spec file: {spec_file}")
    
    result = subprocess.run(
        [sys.executable, "-m", "PyInstaller", str(spec_file), "--clean"],
        cwd=str(script_dir),
        capture_output=False  # Show output in real-time
    )
    
    if result.returncode != 0:
        log_error(f"PyInstaller failed with return code: {result.returncode}")
        return None
    
    exe_path = script_dir / "dist" / "Alarmify.exe"
    
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        log_info(f"\n  Success! Created: {exe_path}")
        log_info(f"  Size: {size_mb:.2f} MB")
        return exe_path
    else:
        log_error("Executable not found!")
        return None


def run_smoke_tests(exe_path):
    """
    Run basic smoke tests on the built executable.
    
    Args:
        exe_path: Path to the executable to test
        
    Returns:
        True if tests pass, False otherwise
    """
    log_info("\n[3/5] Running smoke tests...")
    
    # Test 1: Verify executable exists and is readable
    log_info("  Test 1: Executable exists...")
    if not exe_path.exists():
        log_error("    FAILED: Executable not found")
        return False
    log_info("    PASSED")
    
    # Test 2: Verify executable size is reasonable (> 10 MB)
    log_info("  Test 2: Executable size check...")
    size_mb = exe_path.stat().st_size / (1024 * 1024)
    if size_mb < 10:
        log_error(f"    FAILED: Executable too small ({size_mb:.2f} MB)")
        return False
    log_info(f"    PASSED ({size_mb:.2f} MB)")
    
    # Test 3: Verify executable has PE header (Windows executable)
    log_info("  Test 3: PE header validation...")
    try:
        with open(exe_path, 'rb') as f:
            header = f.read(2)
            if header != b'MZ':
                log_error("    FAILED: Invalid PE header")
                return False
    except Exception as e:
        log_error(f"    FAILED: {e}")
        return False
    log_info("    PASSED")
    
    # Test 4: Try to run executable with --version flag (if supported)
    # This is a basic test - the app should start and exit cleanly
    # We don't actually test this as it would require GUI initialization
    log_info("  Test 4: Executable dependencies check...")
    log_info("    SKIPPED (GUI app - cannot test headless)")
    
    log_info("\n  All smoke tests passed!")
    return True


def run_inno_setup(script_dir, iscc_path):
    """
    Run Inno Setup to create the installer.
    
    Args:
        script_dir: Root directory of the project
        iscc_path: Path to ISCC.exe
        
    Returns:
        Path to the created installer or None if failed
    """
    log_info("\n[4/5] Running Inno Setup...")
    
    iss_file = script_dir / "installer.iss"
    
    if not iss_file.exists():
        log_error(f"  {iss_file} not found")
        return None
    
    result = subprocess.run(
        [str(iscc_path), str(iss_file)],
        cwd=str(script_dir),
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        log_error("Inno Setup failed!")
        log_error(result.stdout)
        log_error(result.stderr)
        return None
    
    # Find the created installer
    output_dir = script_dir / "Output"
    installer_files = list(output_dir.glob("AlarmifySetup*.exe"))
    
    if installer_files:
        installer_path = installer_files[0]
        size_mb = installer_path.stat().st_size / (1024 * 1024)
        log_info(f"\n  Success! Created: {installer_path}")
        log_info(f"  Size: {size_mb:.2f} MB")
        return installer_path
    else:
        log_error("Installer not found in Output directory!")
        return None


def verify_build(exe_path, installer_path):
    """
    Final verification of the build outputs.
    
    Args:
        exe_path: Path to the executable
        installer_path: Path to the installer (or None if skipped)
    """
    log_info("\n[5/5] Final verification...")
    
    log_info(f"\n  Executable: {exe_path}")
    log_info(f"    Size: {exe_path.stat().st_size / (1024 * 1024):.2f} MB")
    log_info(f"    Modified: {time.ctime(exe_path.stat().st_mtime)}")
    
    if installer_path:
        log_info(f"\n  Installer: {installer_path}")
        log_info(f"    Size: {installer_path.stat().st_size / (1024 * 1024):.2f} MB")
        log_info(f"    Modified: {time.ctime(installer_path.stat().st_mtime)}")
    
    log_info("\n  Verification complete!")


def main():
    """Build the Alarmify Windows executable and installer."""
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Build Alarmify installer")
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip smoke tests"
    )
    parser.add_argument(
        "--skip-inno",
        action="store_true",
        help="Skip Inno Setup (create only executable)"
    )
    args = parser.parse_args()
    
    log_info("=" * 60)
    log_info("Building Alarmify Windows Installer")
    log_info("=" * 60)
    
    # Get script directory (where build_installer.py is located)
    script_dir = Path(__file__).parent.resolve()
    log_debug(f"Script directory: {script_dir}")
    
    # Step 1: Clean previous build artifacts
    clean_build_artifacts(script_dir)
    
    # Step 2: Run PyInstaller
    exe_path = run_pyinstaller(script_dir)
    if not exe_path:
        log_error("\nBuild failed at PyInstaller stage!")
        sys.exit(1)
    
    # Step 3: Run smoke tests
    if not args.skip_tests:
        if not run_smoke_tests(exe_path):
            log_error("\nSmoke tests failed!")
            sys.exit(1)
    else:
        log_info("\n[3/5] Smoke tests skipped (--skip-tests)")
    
    # Step 4: Run Inno Setup
    installer_path = None
    if not args.skip_inno:
        iscc_path = find_inno_setup()
        if iscc_path:
            log_info(f"  Found Inno Setup: {iscc_path}")
            installer_path = run_inno_setup(script_dir, iscc_path)
            if not installer_path:
                log_warning("Installer creation failed, but executable is ready")
        else:
            log_info("\n[4/5] Inno Setup not found - skipping installer creation")
            log_info("  Install from: https://jrsoftware.org/isdl.php")
    else:
        log_info("\n[4/5] Inno Setup skipped (--skip-inno)")
    
    # Step 5: Final verification
    verify_build(exe_path, installer_path)
    
    # Summary
    log_info("\n" + "=" * 60)
    log_info("Build complete!")
    log_info("=" * 60)
    log_info(f"\nExecutable: {exe_path}")
    if installer_path:
        log_info(f"Installer:  {installer_path}")
    log_info("\nReady for distribution!")
    log_info("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log_warning("Build interrupted by user")
        sys.exit(130)
    except Exception as e:
        log_error(f"Unexpected error during build: {e}", exc_info=True)
        sys.exit(1)
