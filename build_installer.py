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
import logging     # Structured logging
from logging.handlers import RotatingFileHandler  # Log rotation
from pathlib import Path  # Path manipulation
from datetime import datetime  # Timestamp generation


def setup_logging():
    """
    Configure logging with rotating file handler.
    
    Creates a logs directory in the application folder and sets up
    a rotating file handler with timestamped log files. Logs are
    configured with INFO level and include contextual information.
    """
    # Get script directory
    script_dir = Path(__file__).parent.resolve()
    
    # Create logs directory if it doesn't exist
    logs_dir = script_dir / 'logs'
    logs_dir.mkdir(exist_ok=True)
    
    # Generate timestamped log filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = logs_dir / f'build_{timestamp}.log'
    
    # Configure rotating file handler (10MB per file, keep 5 backups)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    
    # Configure console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatter with timestamp, level, module, and message
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Get logger for this module
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


# Initialize logger for this module
logger = setup_logging()


def main():
    """Build the Alarmify Windows executable."""
    
    logger.info("=" * 50)
    logger.info("Building Alarmify Windows Installer")
    logger.info("=" * 50)
    
    # Get script directory (where build_installer.py is located)
    script_dir = Path(__file__).parent.resolve()
    logger.debug(f"Script directory: {script_dir}")
    
    # Step 1: Clean previous build artifacts
    logger.info("[1/3] Cleaning previous builds...")
    build_dir = script_dir / "build"
    dist_dir = script_dir / "dist"
    
    if build_dir.exists():
        try:
            shutil.rmtree(build_dir)
            logger.info(f"Removed: {build_dir}")
        except Exception as e:
            logger.error(f"Failed to remove build directory: {e}", exc_info=True)
            sys.exit(1)
    else:
        logger.debug(f"Build directory does not exist: {build_dir}")
    
    if dist_dir.exists():
        try:
            shutil.rmtree(dist_dir)
            logger.info(f"Removed: {dist_dir}")
        except Exception as e:
            logger.error(f"Failed to remove dist directory: {e}", exc_info=True)
            sys.exit(1)
    else:
        logger.debug(f"Dist directory does not exist: {dist_dir}")
    
    # Step 2: Run PyInstaller
    logger.info("[2/3] Running PyInstaller...")
    spec_file = script_dir / "alarmify.spec"
    
    if not spec_file.exists():
        logger.error(f"Spec file not found: {spec_file}")
        sys.exit(1)
    
    logger.debug(f"Using spec file: {spec_file}")
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "PyInstaller", str(spec_file)],
            cwd=str(script_dir),
            capture_output=False  # Show output in real-time
        )
        
        if result.returncode != 0:
            logger.error(f"PyInstaller failed with return code: {result.returncode}")
            sys.exit(1)
        
        logger.info("PyInstaller completed successfully")
    except Exception as e:
        logger.error(f"Failed to run PyInstaller: {e}", exc_info=True)
        sys.exit(1)
    
    # Step 3: Verify output
    logger.info("[3/3] Verifying build...")
    exe_path = dist_dir / "Alarmify.exe"
    
    if exe_path.exists():
        try:
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            logger.info(f"Success! Created: {exe_path}")
            logger.info(f"Size: {size_mb:.2f} MB")
        except Exception as e:
            logger.warning(f"Could not determine file size: {e}")
            logger.info(f"Success! Created: {exe_path}")
    else:
        logger.error(f"Executable not found at expected path: {exe_path}")
        logger.error("Build verification failed!")
        sys.exit(1)
    
    logger.info("=" * 50)
    logger.info("Build complete!")
    logger.info(f"Installer: {exe_path}")
    logger.info("=" * 50)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.warning("Build interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error during build: {e}", exc_info=True)
        sys.exit(1)
